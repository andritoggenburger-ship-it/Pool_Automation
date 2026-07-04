# ESP32 Water Tank Monitoring System

## Overview

Complete MicroPython firmware for monitoring a water tank with:
- **3x DS18B20** temperature sensors (one-wire bus)
- **GY-INA219** current sensor (I2C)
- **4-20mA water depth sensor**
- **MQTT** publishing to Home Assistant
- **WebREPL** for remote debugging

## Hardware Setup

### GPIO Pins Used

| Component | GPIO Pin | Function |
|-----------|----------|----------|
| DS18B20 (1-wire) | GPIO 10 | Data line (requires 4.7kΩ pull-up to 3.3V) |
| I2C SDA | GPIO 8 | I2C Data |
| I2C SCL | GPIO 9 | I2C Clock |

### Wiring Diagram

```
ESP32-C6 Zero
┌─────────────────────────────────────────┐
│                                         │
│  GPIO 10 ──[4.7kΩ]──┬── +3.3V         │
│           │         │                  │
│           ├─ DS18B20 #1 (data pin)     │
│           ├─ DS18B20 #2 (data pin)     │
│           └─ DS18B20 #3 (data pin)     │
│                                         │
│  GPIO 8  ──────── SDA ─── INA219       │
│  GPIO 9  ──────── SCL ─── INA219       │
│  GND     ──────── GND                  │
│  3.3V    ──────── VCC                  │
│                                         │
│  +3.3V   ──────── VCC (INA219)         │
│  GND     ──────── GND (INA219)         │
│                                         │
│  GND, +5V ────── Water Sensor (4-20mA) │
│  IN+ (INA219) ── 4-20mA sensor signal  │
│  IN- (INA219) ── GND                   │
│                                         │
└─────────────────────────────────────────┘
```

### Temperature Sensors (DS18B20)

- All three sensors share the **same GPIO 10 data line**
- Each sensor needs separate GND and VCC connections
- **IMPORTANT**: Add external 4.7kΩ pull-up resistor between GPIO 10 and 3.3V
  - Required for 3m cable runs
  - Place resistor near ESP32

### Current Sensor (GY-INA219)

- I2C Address: `0x40` (default)
- Shunt resistor: 0.1Ω (R100 on board)
- Water sensor (4-20mA) connects to green terminal block:
  - Positive: IN+
  - Negative: IN- (GND)

## Installation

### 1. Flash MicroPython Firmware

```bash
# Download ESP32-C6 firmware: https://micropython.org/download/esp32c6/
# Using esptool.py:
esptool.py --chip esp32c6 --port COM3 erase_flash
esptool.py --chip esp32c6 --port COM3 write_flash -z 0x0 esp32c6-*.bin
```

### 2. Upload Script

Use **Thonny IDE** or **WebREPL** to upload:

```
Upload main.py to ESP32
```

Alternatively, via command line:
```bash
ampy --port COM3 put main.py
```

### 3. Configure Settings

Edit `main.py` and update:

```python
WIFI_SSID = "your_wifi_name"
WIFI_PASSWORD = "your_wifi_password"
MQTT_BROKER = "192.168.1.100"  # Your HA Green IP
MQTT_USER = None  # If needed
MQTT_PASSWORD = None  # If needed
```

### 4. First Boot

Connect to serial console (115200 baud) to see startup messages:

```
[2024-XX-XX HH:MM:SS] Connecting to WiFi: your_wifi_name
...
[2024-XX-XX HH:MM:SS] WiFi connected: ('192.168.1.50', '255.255.255.0', '192.168.1.1', '8.8.8.8')
[2024-XX-XX HH:MM:SS] MQTT connected to 192.168.1.100:1883
[2024-XX-XX HH:MM:SS] Found 3 DS18B20 sensors
[2024-XX-XX HH:MM:SS] INA219 initialized at 0x40
```

## Home Assistant Integration

### Automatic Discovery

The script publishes Home Assistant MQTT Discovery messages automatically:
1. Entities appear in HA automatically
2. No manual YAML configuration needed
3. Check **Settings → Devices & Services → MQTT**

### Manual MQTT Configuration (if needed)

```yaml
mqtt:
  - sensor:
      - name: "Water Tank Temp 1"
        state_topic: "water_tank/sensors/temp_1"
        unit_of_measurement: "°C"
        device_class: temperature

      - name: "Water Tank Temp 2"
        state_topic: "water_tank/sensors/temp_2"
        unit_of_measurement: "°C"
        device_class: temperature

      - name: "Water Tank Temp 3"
        state_topic: "water_tank/sensors/temp_3"
        unit_of_measurement: "°C"
        device_class: temperature

      - name: "Water Tank Depth"
        state_topic: "water_tank/sensors/depth"
        unit_of_measurement: "m"

      - name: "Water Sensor Current"
        state_topic: "water_tank/sensors/current"
        unit_of_measurement: "mA"
        device_class: current
```

## Remote Debugging

### WebREPL (Browser-Based)

1. Connect to ESP32 via WebREPL:
   - Visit: `http://micropython.org/webrepl/`
   - Enter: `ws://192.168.1.50:8266` (your ESP32 IP)

2. Execute commands live:
```python
# Check WiFi status
import network
wlan = network.WLAN(network.STA_IF)
print(wlan.ifconfig())

# Read temperature sensor
from ds18x20 import DS18X20
from onewire import OneWire
from machine import Pin
ds = DS18X20(OneWire(Pin(10, Pin.IN, Pin.PULL_UP)))
ds.scan()
ds.convert_temp()
import time
time.sleep(0.75)
temps = [ds.read_temp(addr) for addr in ds.roms]
print(temps)

# Scan I2C devices
from machine import I2C, Pin
i2c = I2C(0, scl=Pin(9), sda=Pin(8))
print([hex(x) for x in i2c.scan()])
```

### Thonny IDE

1. Open Thonny
2. Tools → Options → Interpreter
3. Select "MicroPython (ESP32)"
4. Port: `COM3` (or your port)
5. Click "Connect"
6. Use REPL tab for live debugging

## Troubleshooting

### No DS18B20 Sensors Found

1. Check 4.7kΩ pull-up resistor is present
2. Verify GPIO 10 connections
3. Check OneWire data line voltage: should be ~3.3V
4. Test with WebREPL:
```python
from machine import Pin
pin = Pin(10, Pin.IN, Pin.PULL_UP)
print(pin.value())  # Should read 1 (HIGH)
```

### INA219 Not Found

1. Check I2C connections (SDA=GPIO8, SCL=GPIO9)
2. Verify pull-up resistors on I2C lines (often built into sensor board)
3. Test with WebREPL:
```python
from machine import I2C, Pin
i2c = I2C(0, scl=Pin(9), sda=Pin(8), freq=400000)
devices = i2c.scan()
print([hex(x) for x in devices])  # Should include 0x40
```

### WiFi Connection Fails

1. Check SSID and password spelling
2. Ensure ESP32 is in WiFi range
3. Check if router uses 2.4GHz (ESP32-C6 doesn't support 5GHz)
4. View boot logs on serial console

### MQTT Connection Fails

1. Verify MQTT broker IP is correct
2. Check broker is running (`mosquitto` on Home Assistant)
3. Check firewall allows port 1883
4. Verify credentials if authentication enabled

## Configuration Reference

| Setting | Default | Description |
|---------|---------|-------------|
| `WIFI_SSID` | YOUR_WIFI_SSID | Your WiFi network name |
| `WIFI_PASSWORD` | YOUR_WIFI_PASSWORD | WiFi password |
| `MQTT_BROKER` | 192.168.1.100 | MQTT broker IP (HA Green) |
| `MQTT_PORT` | 1883 | MQTT port |
| `UPDATE_INTERVAL_SECONDS` | 300 | Polling interval (5 minutes) |
| `INA219_ADDRESS` | 0x40 | I2C address of GY-INA219 |
| `WATER_DEPTH_MIN_MA` | 4.0 | Minimum current (0m depth) |
| `WATER_DEPTH_MAX_MA` | 20.0 | Maximum current (5m depth) |

## Water Depth Calibration

The 4-20mA sensor is calibrated as:
- **4mA** → 0m (empty)
- **20mA** → 5m (full)

To adjust for different ranges:

```python
# For 10m range:
WATER_DEPTH_MAX_M = 10.0

# For different sensor range (e.g., 0-3m):
WATER_DEPTH_MIN_MA = 4.0
WATER_DEPTH_MAX_MA = 20.0
WATER_DEPTH_MIN_M = 0.0
WATER_DEPTH_MAX_M = 3.0
```

## Files

- `main.py` - Main MicroPython firmware script
- `README.md` - This documentation

## License

Public Domain

## Support

For issues:
1. Check serial console output
2. Use WebREPL to test components individually
3. Verify hardware connections
4. Check Home Assistant MQTT integration is enabled
