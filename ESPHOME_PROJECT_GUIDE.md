# ESPHome Project Guide for Pond Monitoring

## Goal

This guide explains how to implement your existing pond project with ESPHome on a WaveShare ESP32-C6 Zero.

Project scope:
- 2 x DS18B20 temperature sensors on one shared one-wire bus
- Deep sensor and skimmer sensor exposed separately in Home Assistant
- 1 x INA219 over I2C
- 1 x 4-20 mA water level sensor, powered by 24V, measured through INA219
- 30-second sensor updates
- 5-minute delayed display update for water depth changes >= 0.01 m
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
- One-wire data: GPIO19
- I2C SDA: GPIO20
- I2C SCL: GPIO21
- DS18B20 pull-up: external 4.7k resistor from GPIO19 to 3.3V
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
- 20 mA -> calibrated span with `depth_cal_max_m = 3.0769`
- Ground-reference correction via `depth_cal_offset_m = 0.94`
- Display update held for 5 minutes unless the new level stays at least 0.01 m away

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

Use [pond-node-1-bare.esphome.yaml](c:/Users/toggenan/OneDrive%20-%20BELIMO%20Automation%20AG/Desktop/Pool-Automation/pond-node-1-bare.esphome.yaml) as the active configuration. Keep the following implementation details in sync with that file.

Current config summary:

```yaml
one_wire:
  - platform: gpio
    pin: GPIO19

i2c:
  sda: GPIO20
  scl: GPIO21
  frequency: 100kHz

sensor:
  - platform: ina219
    update_interval: 30s

  - platform: template
    name: Pond Water Depth
    update_interval: 30s
    # Display changes only after 5 minutes outside a 0.01 m deadband.

  - platform: dallas_temp
    id: pond_temp_deep_raw
    address: ${ds18_addr_1}

  - platform: dallas_temp
    id: pond_temp_skimmer_raw
    address: ${ds18_addr_2}

  - platform: template
    name: Pond Water Temp Deep

  - platform: template
    name: Pond Water Temp Skimmer
```

Important:
- Deep sensor address: `0x08000000ca532328`
- Skimmer sensor address: `0x68000000ca317728`

## Step 4: First Flash by USB

1. Connect ESP32-C6 by USB.
2. In ESPHome, click Install.
3. Choose Plug into this computer or the method supported by your setup.
4. Flash once over USB.

After first successful flash, OTA should be available over WiFi.

## Step 5: Discover DS18B20 Addresses

1. Open ESPHome logs.
2. Look for discovered one-wire devices.
3. Copy each real address into the YAML for the deep and skimmer sensors.
4. Reinstall OTA.

## Step 6: Home Assistant Integration

ESPHome API entities should appear automatically in Home Assistant.

Expected entities:
- Pond Water Temp Deep
- Pond Water Temp Skimmer
- Pond Sensor Current
- Pond Water Depth
- Pond Node WiFi RSSI
- Pond Node Uptime
- Pond Node Restart

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
- Current active data pin is GPIO19.

2. INA219 measurement path:
- Ensure current loop actually passes through INA219 shunt path.
- Validate expected 4-20 mA against multimeter at commissioning.

3. Update interval:
- Sensors currently update every 30 s.
- Water depth display changes are intentionally delayed by 5 minutes when the difference is only marginal.

4. Fallback network:
- Keep fallback AP enabled so recovery is possible if WiFi credentials break.

## Migration Path from Current MicroPython Project

1. Keep existing wiring unchanged.
2. Flash ESPHome once via USB.
3. Verify INA219 reads valid current.
4. Verify both DS18B20 addresses and temperatures.
5. Enable HA automations.
6. Retire old MicroPython runtime from this device.

## Troubleshooting

Problem: INA219 not found
- Confirm I2C address is 0x40.
- Check GPIO20 and GPIO21 wiring.
- Lower I2C frequency to 50 kHz temporarily.

Problem: DS18B20 missing or unstable
- Verify 4.7k pull-up to 3.3V.
- Confirm data pin is GPIO19.
- Check cable joins and waterproof connectors.

Problem: Depth wrong but current looks correct
- Reconfirm linear mapping and sensor range.
- Check whether your probe is exactly 0-5 m model.
- Adjust `depth_cal_offset_m` for constant reference shifts.
- Adjust `depth_cal_max_m` if the scale error changes with level.

Problem: OTA fails
- Ensure device is online and API key/password matches.
- Check WiFi RSSI.
- Try one USB flash, then resume OTA.

## Optional Next Improvements

- Add median filters for temperature and current
- Add depth rate-of-change sensor
- Add reboot switch entity for remote maintenance
- Add safe mode / watchdog alert automation
