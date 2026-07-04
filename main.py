"""
ESP32-C6 Water Tank Monitoring System
- 3x DS18B20 Temperature Sensors (One-Wire)
- GY-INA219 Current Sensor (I2C)
- 4-20mA Water Depth Sensor
- MQTT Publishing to Home Assistant
- WebREPL for Remote Debugging
"""

import machine
import network
import time
import json
from machine import Pin, I2C
from onewire import OneWire
from ds18x20 import DS18X20
import umqtt.simple

# ============================================================================
# CONFIGURATION - EDIT THESE VALUES
# ============================================================================

WIFI_SSID = "YOUR_WIFI_SSID"
WIFI_PASSWORD = "YOUR_WIFI_PASSWORD"

MQTT_BROKER = "192.168.1.100"  # Change to your MQTT broker IP
MQTT_PORT = 1883
MQTT_USER = None  # Set to username if needed, None for no auth
MQTT_PASSWORD = None  # Set to password if needed
MQTT_CLIENT_ID = "esp32_water_tank"

# Home Assistant MQTT Discovery
HA_DISCOVERY_PREFIX = "homeassistant"
DEVICE_NAME = "Water Tank"
DEVICE_ID = "water_tank_sensor"

# GPIO Configuration
ONE_WIRE_GPIO = 10  # DS18B20 data pin
I2C_SDA_GPIO = 8
I2C_SCL_GPIO = 9

# Sensor Configuration
INA219_ADDRESS = 0x40  # GY-INA219 I2C address
INA219_CONFIG_REGISTER = 0x00
INA219_CALIBRATION_REGISTER = 0x05
INA219_POWER_REGISTER = 0x03
INA219_CURRENT_REGISTER = 0x04
INA219_BUSV_REGISTER = 0x02

# Water Depth Calibration (4-20mA sensor, 5m range)
WATER_DEPTH_MIN_MA = 4.0  # 4mA = 0m
WATER_DEPTH_MAX_MA = 20.0  # 20mA = 5m
WATER_DEPTH_MIN_M = 0.0
WATER_DEPTH_MAX_M = 5.0
WATER_SHUNT_RESISTANCE = 0.1  # Shunt resistor value in ohms (typically 0.1Ω)

# Update interval
UPDATE_INTERVAL_SECONDS = 300  # 5 minutes

# ============================================================================
# GLOBALS
# ============================================================================

mqtt_client = None
wlan = None
ds_sensors = None
ina219_i2c = None
sensor_addresses = []

# ============================================================================
# LOGGING
# ============================================================================

def log(message):
    """Print timestamped log message"""
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")

# ============================================================================
# WiFi MANAGEMENT
# ============================================================================

def connect_wifi():
    """Connect to WiFi with retry logic"""
    global wlan
    
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    
    if not wlan.isconnected():
        log(f"Connecting to WiFi: {WIFI_SSID}")
        wlan.connect(WIFI_SSID, WIFI_PASSWORD)
        
        timeout = 20
        while not wlan.isconnected() and timeout > 0:
            time.sleep(1)
            timeout -= 1
            print(".", end="", flush=True)
        
        print()
        
        if wlan.isconnected():
            log(f"WiFi connected: {wlan.ifconfig()}")
            return True
        else:
            log("WiFi connection failed")
            return False
    else:
        log(f"Already connected to WiFi: {wlan.ifconfig()}")
        return True

def ensure_wifi():
    """Ensure WiFi connection, reconnect if needed"""
    global wlan
    
    if wlan is None or not wlan.isconnected():
        return connect_wifi()
    return True

# ============================================================================
# MQTT MANAGEMENT
# ============================================================================

def setup_mqtt():
    """Setup MQTT connection"""
    global mqtt_client
    
    try:
        if MQTT_USER and MQTT_PASSWORD:
            mqtt_client = umqtt.simple.MQTTClient(
                MQTT_CLIENT_ID, MQTT_BROKER, MQTT_PORT,
                MQTT_USER, MQTT_PASSWORD
            )
        else:
            mqtt_client = umqtt.simple.MQTTClient(
                MQTT_CLIENT_ID, MQTT_BROKER, MQTT_PORT
            )
        
        mqtt_client.connect()
        log(f"MQTT connected to {MQTT_BROKER}:{MQTT_PORT}")
        return True
    except Exception as e:
        log(f"MQTT connection failed: {e}")
        return False

def publish_discovery():
    """Publish Home Assistant MQTT Discovery messages"""
    try:
        # Temperature sensors discovery
        for i in range(3):
            sensor_id = f"temp_{i+1}"
            topic = f"{HA_DISCOVERY_PREFIX}/sensor/{DEVICE_ID}/{sensor_id}/config"
            
            config = {
                "name": f"{DEVICE_NAME} Temp {i+1}",
                "unique_id": f"{DEVICE_ID}_{sensor_id}",
                "state_topic": f"water_tank/sensors/{sensor_id}",
                "unit_of_measurement": "°C",
                "device_class": "temperature",
                "device": {
                    "identifiers": [DEVICE_ID],
                    "name": DEVICE_NAME
                }
            }
            
            mqtt_client.publish(topic, json.dumps(config))
        
        # Current sensor discovery
        topic = f"{HA_DISCOVERY_PREFIX}/sensor/{DEVICE_ID}/current/config"
        config = {
            "name": f"{DEVICE_NAME} Current",
            "unique_id": f"{DEVICE_ID}_current",
            "state_topic": "water_tank/sensors/current",
            "unit_of_measurement": "mA",
            "device_class": "current",
            "device": {
                "identifiers": [DEVICE_ID],
                "name": DEVICE_NAME
            }
        }
        mqtt_client.publish(topic, json.dumps(config))
        
        # Water depth discovery
        topic = f"{HA_DISCOVERY_PREFIX}/sensor/{DEVICE_ID}/depth/config"
        config = {
            "name": f"{DEVICE_NAME} Depth",
            "unique_id": f"{DEVICE_ID}_depth",
            "state_topic": "water_tank/sensors/depth",
            "unit_of_measurement": "m",
            "icon": "mdi:water",
            "device": {
                "identifiers": [DEVICE_ID],
                "name": DEVICE_NAME
            }
        }
        mqtt_client.publish(topic, json.dumps(config))
        
        log("Home Assistant Discovery published")
        return True
    except Exception as e:
        log(f"Discovery publish failed: {e}")
        return False

def publish_sensor(sensor_name, value):
    """Publish single sensor reading"""
    try:
        topic = f"water_tank/sensors/{sensor_name}"
        mqtt_client.publish(topic, str(value))
    except Exception as e:
        log(f"Publish failed for {sensor_name}: {e}")

# ============================================================================
# TEMPERATURE SENSORS (DS18B20)
# ============================================================================

def init_temperature_sensors():
    """Initialize one-wire temperature sensors"""
    global ds_sensors, sensor_addresses
    
    try:
        # Use internal pull-up for initial testing
        # For production with 3m cables, add external 4.7kΩ resistor
        one_wire_pin = Pin(ONE_WIRE_GPIO, Pin.IN, Pin.PULL_UP)
        ds = DS18X20(OneWire(one_wire_pin))
        
        # Find all connected sensors
        ds.scan()
        sensor_addresses = ds.roms
        
        if len(sensor_addresses) > 0:
            log(f"Found {len(sensor_addresses)} DS18B20 sensors")
            for i, addr in enumerate(sensor_addresses):
                log(f"  Sensor {i+1}: {addr.hex()}")
            ds_sensors = ds
            return True
        else:
            log("No DS18B20 sensors found!")
            return False
    except Exception as e:
        log(f"Temperature sensor init failed: {e}")
        return False

def read_temperatures():
    """Read all temperature sensors"""
    try:
        if ds_sensors is None:
            return [None, None, None]
        
        # Trigger conversion
        ds_sensors.convert_temp()
        time.sleep(0.75)  # Wait for conversion
        
        temps = []
        for i in range(3):
            if i < len(sensor_addresses):
                temp = ds_sensors.read_temp(sensor_addresses[i])
                temps.append(temp)
                log(f"Temp {i+1}: {temp}°C")
            else:
                temps.append(None)
        
        return temps
    except Exception as e:
        log(f"Temperature reading failed: {e}")
        return [None, None, None]

# ============================================================================
# INA219 CURRENT SENSOR
# ============================================================================

def init_ina219():
    """Initialize INA219 current sensor"""
    global ina219_i2c
    
    try:
        ina219_i2c = I2C(0, scl=Pin(I2C_SCL_GPIO), sda=Pin(I2C_SDA_GPIO), freq=400000)
        
        # Scan I2C bus
        devices = ina219_i2c.scan()
        log(f"I2C devices found: {[hex(x) for x in devices]}")
        
        if INA219_ADDRESS in devices:
            # Configure INA219
            # Config: 16V range, 400mA max, 1x gain
            config = 0x399F  # Default configuration
            config_bytes = bytes([config >> 8, config & 0xFF])
            ina219_i2c.writeto_mem(INA219_ADDRESS, INA219_CONFIG_REGISTER, config_bytes)
            
            # Calibration for 0.1Ω shunt: Calibration = 0.04096 / (Current_LSB * Shunt)
            # Using 1mA LSB: Calibration = 0.04096 / (0.001 * 0.1) = 409.6 ≈ 0x019A
            calibration = 0x019A
            cal_bytes = bytes([calibration >> 8, calibration & 0xFF])
            ina219_i2c.writeto_mem(INA219_ADDRESS, INA219_CALIBRATION_REGISTER, cal_bytes)
            
            log("INA219 initialized at 0x40")
            return True
        else:
            log(f"INA219 not found at 0x{INA219_ADDRESS:02x}")
            return False
    except Exception as e:
        log(f"INA219 init failed: {e}")
        return False

def read_ina219():
    """Read current and power from INA219"""
    try:
        if ina219_i2c is None:
            return None, None
        
        # Read shunt voltage (register 0x01)
        shunt_data = ina219_i2c.readfrom_mem(INA219_ADDRESS, 0x01, 2)
        shunt_voltage_raw = (shunt_data[0] << 8) | shunt_data[1]
        # Convert to voltage (LSB = 10µV)
        shunt_voltage = (shunt_voltage_raw >> 3) * 0.00001  # In volts
        
        # Calculate current from shunt voltage (I = V / R)
        current_ma = (shunt_voltage / WATER_SHUNT_RESISTANCE) * 1000  # In mA
        
        # Read power
        power_data = ina219_i2c.readfrom_mem(INA219_ADDRESS, INA219_POWER_REGISTER, 2)
        power_raw = (power_data[0] << 8) | power_data[1]
        power = power_raw * 0.002  # 2mW per LSB
        
        log(f"Current: {current_ma:.2f}mA, Power: {power:.2f}mW")
        
        return current_ma, power
    except Exception as e:
        log(f"INA219 read failed: {e}")
        return None, None

def current_to_depth(current_ma):
    """Convert 4-20mA current to water depth"""
    if current_ma is None:
        return None
    
    # Clamp current to range
    current_ma = max(WATER_DEPTH_MIN_MA, min(WATER_DEPTH_MAX_MA, current_ma))
    
    # Linear interpolation: 4mA -> 0m, 20mA -> 5m
    depth = (current_ma - WATER_DEPTH_MIN_MA) / (WATER_DEPTH_MAX_MA - WATER_DEPTH_MIN_MA)
    depth = depth * (WATER_DEPTH_MAX_M - WATER_DEPTH_MIN_M) + WATER_DEPTH_MIN_M
    
    log(f"Water Depth: {depth:.2f}m ({current_ma:.2f}mA)")
    
    return depth

# ============================================================================
# MAIN LOOP
# ============================================================================

def main():
    """Main application loop"""
    global mqtt_client
    
    # Enable WebREPL for remote debugging
    try:
        import webrepl
        webrepl.start()
        log("WebREPL started on port 8266 (connect via web browser)")
    except Exception as e:
        log(f"WebREPL startup warning: {e}")
    
    # Connect WiFi
    if not ensure_wifi():
        log("Failed to connect WiFi, retrying...")
        time.sleep(5)
        return
    
    # Setup MQTT
    if not setup_mqtt():
        log("Failed to setup MQTT, retrying...")
        time.sleep(5)
        return
    
    # Publish discovery
    publish_discovery()
    
    # Initialize sensors
    log("Initializing sensors...")
    init_temperature_sensors()
    init_ina219()
    
    # Main polling loop
    log(f"Starting sensor polling loop ({UPDATE_INTERVAL_SECONDS}s interval)")
    
    while True:
        try:
            # Ensure WiFi and MQTT are connected
            ensure_wifi()
            if mqtt_client is None or not hasattr(mqtt_client, 'sock'):
                setup_mqtt()
            
            # Read temperature sensors
            temps = read_temperatures()
            
            # Read current sensor
            current_ma, power = read_ina219()
            
            # Convert current to depth
            depth_m = current_to_depth(current_ma)
            
            # Publish readings
            for i, temp in enumerate(temps):
                if temp is not None:
                    publish_sensor(f"temp_{i+1}", f"{temp:.2f}")
            
            if current_ma is not None:
                publish_sensor("current", f"{current_ma:.2f}")
            
            if depth_m is not None:
                publish_sensor("depth", f"{depth_m:.2f}")
            
            log("Readings published")
            
            # Wait for next update
            log(f"Sleeping for {UPDATE_INTERVAL_SECONDS}s...")
            time.sleep(UPDATE_INTERVAL_SECONDS)
            
        except Exception as e:
            log(f"Main loop error: {e}")
            time.sleep(10)

# ============================================================================
# ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        log("Program interrupted by user")
        if mqtt_client is not None:
            mqtt_client.disconnect()
    except Exception as e:
        log(f"Fatal error: {e}")
