# Configuration Template for Legacy MicroPython ESP32 Water Tank Monitor

This file documents the older `main.py`-based MicroPython setup.

The active pond node configuration is now ESPHome-based and lives in [pond-node-1-bare.esphome.yaml](c:/Users/toggenan/OneDrive%20-%20BELIMO%20Automation%20AG/Desktop/Pool-Automation/pond-node-1-bare.esphome.yaml).

Current active ESPHome differences from the legacy template:
- One-wire data pin is `GPIO19`
- I2C pins are `GPIO20` / `GPIO21`
- Two DS18B20 sensors are used: deep and skimmer
- Home Assistant integration uses ESPHome native API
- Water depth uses calibrated span/offset plus delayed display update logic

## Quick Start Configuration

Copy this template to update `main.py`:

```python
# ============================================================================
# YOUR CONFIGURATION - UPDATE THESE VALUES
# ============================================================================

# WiFi Settings
WIFI_SSID = "YourWiFiName"              # Your 2.4GHz WiFi network
WIFI_PASSWORD = "YourPassword123"       # WiFi password

# MQTT Broker (Home Assistant)
MQTT_BROKER = "192.168.1.100"          # IP address of HA Green / MQTT broker
MQTT_PORT = 1883                        # Standard MQTT port
MQTT_USER = None                        # Username (None if no auth)
MQTT_PASSWORD = None                    # Password (None if no auth)

# Device Identification
MQTT_CLIENT_ID = "esp32_water_tank"     # Unique identifier for this ESP32
DEVICE_NAME = "Water Tank"              # Display name in Home Assistant
DEVICE_ID = "water_tank_sensor"         # Unique device ID

# Home Assistant MQTT Discovery
HA_DISCOVERY_PREFIX = "homeassistant"   # Standard prefix (don't change)

# GPIO Pin Configuration (default recommended, change only if needed)
ONE_WIRE_GPIO = 19                      # DS18B20 one-wire data pin (legacy template differs from active YAML path)
I2C_SDA_GPIO = 20                       # I2C data pin
I2C_SCL_GPIO = 21                       # I2C clock pin

# I2C Sensor Configuration
INA219_ADDRESS = 0x40                   # GY-INA219 address (default)

# Water Depth Sensor Calibration
# 4-20mA current level sensor mapping to depth in meters
WATER_DEPTH_MIN_MA = 4.0                # Current at minimum depth (0m)
WATER_DEPTH_MAX_MA = 20.0               # Current at maximum depth (5m)
WATER_DEPTH_MIN_M = 0.0                 # Minimum depth
WATER_DEPTH_MAX_M = 5.0                 # Maximum depth (5m range sensor)
WATER_SHUNT_RESISTANCE = 0.1            # INA219 shunt resistor (0.1Ω typical)

# Update Interval
UPDATE_INTERVAL_SECONDS = 300           # Reading interval in seconds
                                         # 300s = 5 minutes (recommended for slow changes)
```

## Configuration Examples

### Example 1: Basic Local Setup

```python
WIFI_SSID = "MyHome"
WIFI_PASSWORD = "MyPassword2024"
MQTT_BROKER = "192.168.1.100"           # HA Green local IP
MQTT_USER = None                        # No authentication
MQTT_PASSWORD = None
UPDATE_INTERVAL_SECONDS = 300           # 5 minutes
```

### Example 2: With MQTT Authentication

```python
WIFI_SSID = "MyHome"
WIFI_PASSWORD = "MyPassword2024"
MQTT_BROKER = "192.168.1.100"
MQTT_USER = "mqtt_user"                 # Home Assistant MQTT user
MQTT_PASSWORD = "mqtt_password_here"    # Your MQTT password
```

### Example 3: Remote MQTT Broker

```python
WIFI_SSID = "MyHome"
WIFI_PASSWORD = "MyPassword2024"
MQTT_BROKER = "mqtt.example.com"        # Cloud MQTT service
MQTT_PORT = 8883                        # TLS port
MQTT_USER = "your_username"
MQTT_PASSWORD = "your_password"
```

### Example 4: Different Water Sensor Range (10m)

```python
WATER_DEPTH_MIN_MA = 4.0
WATER_DEPTH_MAX_MA = 20.0
WATER_DEPTH_MIN_M = 0.0
WATER_DEPTH_MAX_M = 10.0                # Changed to 10m max
```

### Example 5: Faster Update Interval (1 minute)

```python
UPDATE_INTERVAL_SECONDS = 60            # 1 minute for more responsive monitoring
```

## Configuration Validation

After updating `main.py`, verify your settings:

1. **WiFi SSID**: Ensure it's 2.4GHz (ESP32-C6 doesn't support 5GHz)
2. **MQTT Broker**: Should be reachable from ESP32
3. **GPIO Pins**: Match your physical wiring
4. **Sensor Range**: Verify with your water sensor datasheet

## Finding Your Settings

### WiFi SSID and Password
- Check your router settings or label
- On Windows: Settings → Network & Internet → WiFi → Manage known networks
- On Mac: System Preferences → Network → WiFi

### HA Green MQTT Broker IP
- In Home Assistant: Settings → Devices & Services → MQTT
- Look for "broker" information
- Usually `192.168.x.x` on local network

### MQTT Credentials
- If auto-setup: Check Home Assistant MQTT integration
- If manual setup: Check your `configuration.yaml` for MQTT section
- Default HA user: `homeassistant`

### INA219 Address
- Default: `0x40` (with addr pin unconnected)
- Alternative options: `0x41`, `0x44`, `0x45` (check board configuration)

## Troubleshooting Configuration

### WiFi Connection Fails
```python
# Try faster retry:
UPDATE_INTERVAL_SECONDS = 10  # Reconnect faster
# Check SSID is exactly correct (case-sensitive)
# Verify no special characters in password
```

### MQTT Connection Fails
```python
# Verify broker is running (check HA logs)
# Ensure port is correct (1883 for unencrypted, 8883 for TLS)
# Check firewall allows port access
# Verify credentials if using authentication
```

### Sensors Not Detected
```python
# Wrong GPIO pins - recheck wiring
# Missing pull-up resistor - add 4.7kΩ for one-wire
# Wrong I2C address - try 0x41, 0x44, 0x45
# Run i2c.scan() in WebREPL to find address
```

## Advanced Configuration

### Custom MQTT Topics

Edit the `publish_sensor()` calls in `main.py`:

```python
# Change from:
topic = f"water_tank/sensors/{sensor_name}"

# To custom structure:
topic = f"myhouse/tank/{sensor_name}"  # myhouse/tank/temp_1, etc.
```

### Logging Frequency

Enable verbose logging for debugging:

```python
# Add to main loop before readings:
log(f"Loop {loop_count}: Reading sensors...")
loop_count += 1
```

### Custom Temperature Calibration

Add offset to temperature readings:

```python
# In read_temperatures():
TEMP_CALIBRATION_OFFSET = -0.5  # Adjust each reading by -0.5°C
temp = ds_sensors.read_temp(sensor_addresses[i]) + TEMP_CALIBRATION_OFFSET
```

### Custom Depth Conversion

For non-standard water sensor:

```python
def current_to_depth(current_ma):
    # Your custom formula here
    # Example: quadratic mapping
    if current_ma is None:
        return None
    
    # Instead of linear interpolation
    normalized = (current_ma - 4.0) / 16.0  # 0.0 to 1.0
    depth = 5.0 * (normalized ** 1.1)       # Non-linear response
    return depth
```

## Legacy MQTT Topics

These topics apply only to the older `main.py`-based MicroPython path:

```
homeassistant/sensor/water_tank_sensor/temp_1/config
homeassistant/sensor/water_tank_sensor/temp_2/config
homeassistant/sensor/water_tank_sensor/temp_3/config
homeassistant/sensor/water_tank_sensor/current/config
homeassistant/sensor/water_tank_sensor/depth/config

water_tank/sensors/temp_1
water_tank/sensors/temp_2
water_tank/sensors/temp_3
water_tank/sensors/current
water_tank/sensors/depth
```

## Next Steps

1. Update configuration in `main.py`
2. Upload to ESP32
3. Check serial console for connection messages
4. Verify MQTT topics in Home Assistant
5. Create automations based on tank level

## Support

For configuration issues:
- Check WebREPL output
- Review Home Assistant logs
- Verify MQTT broker connectivity
- Test each sensor individually
