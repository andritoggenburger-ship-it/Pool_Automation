# ESP32 Pond Monitoring System

## Overview

Current ESPHome-based pond monitoring configuration with:
- **2x DS18B20** temperature sensors on one shared one-wire bus
  - `Pond Water Temp Deep`
  - `Pond Water Temp Skimmer`
- **GY-INA219** current sensor (I2C)
- **4-20mA water depth sensor**
- **Native ESPHome integration** with Home Assistant
- **OTA updates** and remote restart from Home Assistant

## Hardware Setup

### GPIO Pins Used

| Component | GPIO Pin | Function |
|-----------|----------|----------|
| DS18B20 (1-wire) | GPIO 19 | Data line (requires 4.7kΩ pull-up to 3.3V) |
| I2C SDA | GPIO 20 | I2C Data |
| I2C SCL | GPIO 21 | I2C Clock |

Note: GPIO 8 is reserved for the onboard WS2812 RGB LED in the current ESPHome heartbeat setup.

### Wiring Diagram

```
ESP32-C6 Zero
┌─────────────────────────────────────────┐
│                                         │
│  GPIO 19 ──[4.7kΩ]──┬── +3.3V         │
│           │         │                  │
│           ├─ DS18B20 Deep (data pin)   │
│           └─ DS18B20 Skimmer (data pin)│
│                                         │
│  GPIO 20 ──────── SDA ─── INA219       │
│  GPIO 21 ──────── SCL ─── INA219       │
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

- Both sensors share the **same GPIO 19 data line**
- Each sensor needs separate GND and VCC connections
- **IMPORTANT**: Add external 4.7kΩ pull-up resistor between GPIO 19 and 3.3V
  - Place resistor near ESP32
- Installed sensor names in Home Assistant:
  - `Pond Water Temp Deep`
  - `Pond Water Temp Skimmer`
- Deep sensor last-meter Ethernet mapping:
  - data (yellow) -> Ethernet green
  - ground -> Ethernet green/white
  - 3.3V -> Ethernet blue

### Current Sensor (GY-INA219)

- I2C Address: `0x40` (default)
- Shunt resistor: 0.1Ω (R100 on board)
- Water sensor (4-20mA) connects to green terminal block:
  - Positive: IN+
  - Negative: IN- (GND)

## Current ESPHome Setup

### 1. Active Firmware

The active device configuration is stored in [pond-node-1-bare.esphome.yaml](c:/Users/toggenan/OneDrive%20-%20BELIMO%20Automation%20AG/Desktop/Pool-Automation/pond-node-1-bare.esphome.yaml).

### 2. Key ESPHome Behavior

- One-wire bus on `GPIO19`
- INA219 on `GPIO20`/`GPIO21`
- Raw current is filtered with median plus exponential moving average
- Water depth uses calibrated linear mapping with `depth_cal_max_m = 3.0769` and `depth_cal_offset_m = 0.94`
- Displayed water depth only changes after the new value stays at least `0.01 m` away for `5 minutes`
- A restart button is exposed to Home Assistant as `Pond Node Restart`

### 3. Home Assistant Entities

- `Pond Water Depth`
- `Pond Sensor Current`
- `Pond Water Temp Deep`
- `Pond Water Temp Skimmer`
- `Pond Node WiFi RSSI`
- `Pond Node Uptime`
- `Pond Node Restart`

### 4. Flash and Updates

- First flash can be done by USB from the ESPHome add-on or dashboard.
- Normal updates are OTA over WiFi.
- Home Assistant discovers the device through the ESPHome API.

## Legacy Files

The repository still contains MicroPython-oriented files such as `main.py` and some legacy notes. The active deployment path for the pond node is the ESPHome YAML above.

## Troubleshooting Notes

- If one-wire becomes unstable, verify the 4.7k pull-up to 3.3V and re-check GPIO19 continuity.
- If temperature sensors appear as `unavailable`, confirm both DS18B20 addresses in the YAML match the installed probes.
- If depth is offset by a constant amount, adjust `depth_cal_offset_m`.
- If depth error changes across the range, adjust `depth_cal_max_m` instead.

See the dedicated guides for hardware setup, Home Assistant integration, and ESPHome deployment details.

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
