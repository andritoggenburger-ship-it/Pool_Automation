# ESPHome Project Guide for Pond Monitoring

## Goal

This guide explains how to implement your existing pond project with ESPHome on a WaveShare ESP32-C6 Zero.

Project scope:
- 3 x DS18B20 temperature sensors on one shared one-wire bus
- 1 x INA219 over I2C
- 1 x 4-20 mA water level sensor, powered by 24V, measured through INA219
- 5-minute sensor update interval
- Integration with Home Assistant Green
- Remote updates over WiFi

## Why ESPHome for This Project

ESPHome gives you:
- Native Home Assistant integration with auto-discovery
- OTA updates from Home Assistant
- Centralized configuration in YAML
- Logs and diagnostics in the HA UI
- Easier lifecycle management than custom scripts

Important note:
- ESPHome OTA updates include your application and platform packages used by ESPHome.
- For major framework jumps, some devices may still occasionally need one USB flash, but day-to-day updates are OTA.

## Hardware Mapping

Use the same pin plan you already defined:
- One-wire data: GPIO10
- I2C SDA: GPIO20
- I2C SCL: GPIO21
- DS18B20 pull-up: external 4.7k resistor from GPIO10 to 3.3V
- GPIO8 reserved for onboard WS2812 status LED

Power topology:
- 24V supply powers water sensor directly
- Buck converter 24V to 5V USB powers ESP32 via USB
- INA219 and DS18B20 powered from ESP32 3.3V pin
- Common ground across all components

## High-Level Architecture

1. ESPHome reads raw values from:
- DS18B20 sensors via one-wire
- INA219 current sensor via I2C

2. ESPHome computes derived sensor:
- Water depth from current using linear mapping
- 4 mA -> 0.0 m
- 20 mA -> 5.0 m

3. Home Assistant receives entities automatically via ESPHome API.

4. Updates are deployed OTA from HA or ESPHome Dashboard.

## Prerequisites

- Home Assistant Green installed and online
- ESPHome add-on installed in Home Assistant
- ESP32-C6 connected once by USB for first flash
- Your WiFi SSID and password

## Step 1: Install ESPHome Add-on in Home Assistant

1. Open Home Assistant.
2. Go to Settings -> Add-ons -> Add-on Store.
3. Install ESPHome.
4. Start the add-on.
5. Enable Start on boot.

## Step 2: Create New ESPHome Device

In ESPHome UI:
1. Click New Device.
2. Name it, for example pond-node-1.
3. Select ESP32 platform.
4. Choose ESP32-C6 board profile if available in your version.
5. Enter WiFi credentials.

If board profile naming differs by release, use a compatible ESP32-C6 board entry and keep framework as esp-idf.

## Step 3: Use This ESPHome Configuration

Create or replace the YAML with the following base. Then adjust names and addresses if needed.

```yaml
esphome:
  name: pond-node-1
  friendly_name: Pond Node 1

esp32:
  board: esp32-c6-devkitc-1
  framework:
    type: esp-idf

# Logging and management
logger:

api:
  encryption:
    key: "REPLACE_WITH_GENERATED_KEY"

ota:
  - platform: esphome
    password: "REPLACE_WITH_OTA_PASSWORD"

wifi:
  ssid: "REPLACE_WIFI_SSID"
  password: "REPLACE_WIFI_PASSWORD"
  power_save_mode: none
  ap:
    ssid: "Pond-Node-Fallback"
    password: "REPLACE_FALLBACK_PASSWORD"

captive_portal:

# Optional static IP
# manual_ip:
#   static_ip: 192.168.1.50
#   gateway: 192.168.1.1
#   subnet: 255.255.255.0

# Keep updates every 5 minutes where possible
interval:
  - interval: 300s
    then:
      - component.update: ds18b20_1
      - component.update: ds18b20_2
      - component.update: ds18b20_3
      - component.update: ina219_current
      - component.update: ina219_bus_voltage
      - component.update: ina219_power

# I2C for INA219
i2c:
  sda: GPIO20
  scl: GPIO21
  scan: true
  frequency: 100kHz

# One-wire bus
one_wire:
  - platform: gpio
    pin: GPIO10

sensor:
  - platform: ina219
    address: 0x40
    shunt_resistance: 0.1 ohm
    max_voltage: 26.0V
    max_current: 0.4A
    current:
      name: Pond Sensor Current
      id: ina219_current
      unit_of_measurement: mA
      accuracy_decimals: 2
      filters:
        - multiply: 1000.0
      update_interval: never
    bus_voltage:
      name: Pond Sensor Bus Voltage
      id: ina219_bus_voltage
      update_interval: never
    power:
      name: Pond Sensor Power
      id: ina219_power
      update_interval: never

  # Derived depth from 4-20 mA -> 0-5 m
  - platform: template
    name: Pond Water Depth
    id: pond_depth
    unit_of_measurement: m
    accuracy_decimals: 2
    update_interval: 300s
    lambda: |-
      float current_ma = id(ina219_current).state;

      if (isnan(current_ma)) {
        return NAN;
      }

      // Clamp to expected range
      if (current_ma < 4.0f) current_ma = 4.0f;
      if (current_ma > 20.0f) current_ma = 20.0f;

      // Linear map: 4mA -> 0m, 20mA -> 5m
      float depth_m = (current_ma - 4.0f) * (5.0f / 16.0f);
      return depth_m;

  # DS18B20 sensors on shared bus
  - platform: dallas_temp
    address: 0x0000000000000001
    name: Pond Temp Sensor 1
    id: ds18b20_1
    update_interval: never

  - platform: dallas_temp
    address: 0x0000000000000002
    name: Pond Temp Sensor 2
    id: ds18b20_2
    update_interval: never

  - platform: dallas_temp
    address: 0x0000000000000003
    name: Pond Temp Sensor 3
    id: ds18b20_3
    update_interval: never

  # Device health sensors
  - platform: wifi_signal
    name: Pond Node WiFi RSSI
    update_interval: 300s

  - platform: uptime
    name: Pond Node Uptime
    update_interval: 300s
```

Important:
- Replace DS18B20 addresses with real discovered addresses after first boot.
- Address format is device-specific; ESPHome logs will show them.

## Step 4: First Flash by USB

1. Connect ESP32-C6 by USB.
2. In ESPHome, click Install.
3. Choose Plug into this computer or the method supported by your setup.
4. Flash once over USB.

After first successful flash, OTA should be available over WiFi.

## Step 5: Discover DS18B20 Addresses

1. Open ESPHome logs.
2. Look for discovered one-wire devices.
3. Copy each real address into the YAML for the three sensors.
4. Reinstall OTA.

## Step 6: Home Assistant Integration

ESPHome API entities should appear automatically in Home Assistant.

Expected entities:
- Pond Temp Sensor 1
- Pond Temp Sensor 2
- Pond Temp Sensor 3
- Pond Sensor Current
- Pond Water Depth
- Pond Sensor Bus Voltage
- Pond Sensor Power
- Pond Node WiFi RSSI
- Pond Node Uptime

## Step 7: Recommended Home Assistant Automations

Examples:
- Low water alert if depth < 0.5 m for 10 minutes
- High water alert if depth > 4.5 m for 10 minutes
- Sensor fault alert if current < 3.8 mA or > 20.5 mA
- Node offline alert if device unavailable for more than 15 minutes

## Step 8: OTA Update Workflow

Normal update flow:
1. Edit YAML in ESPHome.
2. Click Install -> Wirelessly.
3. Device reboots with new firmware.
4. Verify sensors and automations.

This is the ESPHome equivalent of appliance-like update behavior.

## Practical Notes for Your Build

1. One-wire reliability over 3 m cable:
- Keep external 4.7k pull-up.
- Use twisted pair or shielded cable.
- Keep ground clean and common.

2. INA219 measurement path:
- Ensure current loop actually passes through INA219 shunt path.
- Validate expected 4-20 mA against multimeter at commissioning.

3. Update interval:
- 300 s is good for slow-changing pond levels.
- You can still keep device health sensors at 300 s.

4. Fallback network:
- Keep fallback AP enabled so recovery is possible if WiFi credentials break.

## Migration Path from Current MicroPython Project

1. Keep existing wiring unchanged.
2. Flash ESPHome once via USB.
3. Verify INA219 reads valid current.
4. Verify all 3 DS18B20 addresses and temperatures.
5. Enable HA automations.
6. Retire old MicroPython runtime from this device.

## Troubleshooting

Problem: INA219 not found
- Confirm I2C address is 0x40.
- Check GPIO20 and GPIO21 wiring.
- Lower I2C frequency to 50 kHz temporarily.

Problem: DS18B20 missing or unstable
- Verify 4.7k pull-up to 3.3V.
- Confirm data pin is GPIO10.
- Check cable joins and waterproof connectors.

Problem: Depth wrong but current looks correct
- Reconfirm linear mapping and sensor range.
- Check whether your probe is exactly 0-5 m model.
- Apply optional calibration offset in template lambda.

Problem: OTA fails
- Ensure device is online and API key/password matches.
- Check WiFi RSSI.
- Try one USB flash, then resume OTA.

## Optional Next Improvements

- Add median filters for temperature and current
- Add depth rate-of-change sensor
- Add reboot switch entity for remote maintenance
- Add safe mode / watchdog alert automation
