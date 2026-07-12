# Home Assistant Green Integration Guide

## Overview

This guide walks through integrating your ESP32 pond monitoring system with **Home Assistant Green** using **ESPHome native API integration**.

**What you'll have after this guide:**
- ✅ Automatic sensor discovery in Home Assistant
- ✅ Real-time water tank depth, temperature, and current readings
- ✅ Automations based on tank level
- ✅ Dashboard with gauges and graphs
- ✅ Alerts when tank is empty or full

## Prerequisites

- Home Assistant Green running on your network
- ESPHome add-on installed and running in Home Assistant
- ESP32 with firmware uploaded from [pond-node-1-bare.esphome.yaml](c:/Users/toggenan/OneDrive%20-%20BELIMO%20Automation%20AG/Desktop/Pool-Automation/pond-node-1-bare.esphome.yaml)
- WiFi network accessible to both devices

## Step 1: Install ESPHome in Home Assistant

### 1.1 Install ESPHome Add-on

Use the ESPHome add-on for the active pond node deployment.

1. Open Home Assistant at `http://homeassistant.local:8123/`
2. Go to **Settings → Add-ons**
3. Open **Add-on Store**
4. Search for **ESPHome**
5. Install and start it

### 1.2 Start the Add-on

1. Go to **Settings → Add-ons → ESPHome**
2. Click **"Start"** button
3. Check **"Start on boot"** (recommended)
4. Look for green checkmark indicating it's running

### 1.3 Open the ESPHome Dashboard

1. Open the ESPHome add-on
2. Open the dashboard / web UI
3. The pond node should appear there once configured

## Step 2: Add or Edit the Pond Node

### 2.1 Use the Current YAML

Use [pond-node-1-bare.esphome.yaml](c:/Users/toggenan/OneDrive%20-%20BELIMO%20Automation%20AG/Desktop/Pool-Automation/pond-node-1-bare.esphome.yaml) as the source of truth.

### 2.2 Verify Current Device Behavior

- One-wire bus: `GPIO19`
- INA219: `GPIO20` / `GPIO21`
- Temperature entities:
  - `Pond Water Temp Deep`
  - `Pond Water Temp Skimmer`
- Water level entities:
  - `Pond Sensor Current`
  - `Pond Water Depth`
- Device maintenance entity:
  - `Pond Node Restart`

### 2.3 Install / Update the Firmware

1. First flash by USB if required.
2. After first flash, use **Install → Wirelessly** for OTA updates.
3. After boot, Home Assistant should auto-discover the ESPHome device.

## Step 3: Verify Entities in Home Assistant

### 3.1 Expected Entities

Once online, the ESPHome integration should expose:

- `sensor.pond_water_depth`
- `sensor.pond_sensor_current`
- `sensor.pond_water_temp_deep`
- `sensor.pond_water_temp_skimmer`
- `sensor.pond_node_wifi_rssi`
- `sensor.pond_node_uptime`
- `button.pond_node_restart`

### 3.2 Notes on Water Depth

- Current depth scaling uses a calibrated span and an offset.
- Displayed depth only updates after the raw value stays at least `0.01 m` away for `5 minutes`.
- This reduces flicker around small level changes.

### 3.3 Notes on Temperature Sensors

- Deep sensor address: `0x08000000ca532328`
- Skimmer sensor address: `0x68000000ca317728`
- Both are on the same GPIO19 one-wire bus.

## Step 4: Example Dashboard Cards

Recommended cards:
- Gauge for `sensor.pond_water_depth`
- Entities card for both temperature sensors
- History graph for `sensor.pond_sensor_current`
- Button card for `button.pond_node_restart`

## Step 5: Example Automations

### 5.1 Alert When Tank is Empty

**Automation: Low Pond Level**

1. Go to **Settings → Automations & Scenes → Create Automation**
2. **Trigger**: State
  - Entity: `sensor.pond_water_depth`
   - Condition: Less than `0.5`m
   - For at least: 5 minutes
3. **Action**: Notification
  - Title: "Pond Alert"
  - Message: "Pond depth is {{ states('sensor.pond_water_depth') }}m"
   - Notify service: `notify.notify` (or your phone)

### 5.2 Alert When Tank is Full

**Automation: High Pond Level**

1. **Trigger**: State
  - Entity: `sensor.pond_water_depth`
   - Condition: Greater than `4.5`m
   - For at least: 5 minutes
2. **Action**: Notification
  - Title: "Pond Level High"
  - Message: "Pond depth is {{ states('sensor.pond_water_depth') }}m"

### 5.3 Temperature Alert

**Automation: Abnormal Temperature**

1. **Trigger**: State
  - Entity: `sensor.pond_water_temp_deep`
   - Condition: Greater than `35`°C (adjust as needed)
2. **Action**: Notification
   - Title: "🌡️ High Water Temperature"
  - Message: "Deep water temperature: {{ states('sensor.pond_water_temp_deep') }}°C"

### Example YAML Automation

Add to `automations.yaml`:

```yaml
- id: low_water_tank
  alias: "Low Pond Level Alert"
  trigger:
    - platform: numeric_state
      entity_id: sensor.pond_water_depth
      below: 0.5
      for:
        minutes: 5
  action:
    - service: notify.notify
      data:
        title: "Pond Alert"
        message: >
          Pond depth is low: 
          {{ states('sensor.pond_water_depth') }}m

- id: high_water_tank
  alias: "High Pond Level Alert"
  trigger:
    - platform: numeric_state
      entity_id: sensor.pond_water_depth
      above: 4.5
      for:
        minutes: 5
  action:
    - service: notify.notify
      data:
        title: "Pond Level High"
        message: >
          Pond depth is now: 
          {{ states('sensor.pond_water_depth') }}m

- id: high_temp_alert
  alias: "High Water Temperature"
  trigger:
    - platform: numeric_state
      entity_id: sensor.pond_water_temp_deep
      above: 35
      for:
        minutes: 10
  action:
    - service: notify.notify
      data:
        title: "🌡️ High Temperature"
        message: >
          Deep water temp: 
          {{ states('sensor.pond_water_temp_deep') }}°C
```

## Step 6: Create Dashboard

### 6.1 Create Custom Dashboard

1. Go to **Dashboard**
2. Click **"+ Create Dashboard"**
3. Name it: **"Pond"**
4. Click **"Create"**

### 6.2 Add Gauge Cards

**Depth Gauge:**
```yaml
type: gauge
entity: sensor.pond_water_depth
min: 0
max: 3.1
title: Pond Water Depth
unit_of_measurement: m
```

**Current Gauge:**
```yaml
type: gauge
entity: sensor.pond_sensor_current
min: 0
max: 25
title: Pond Sensor Current
unit_of_measurement: mA
```

### 6.3 Add Temperature Cards

```yaml
type: custom:thermostat-card
entity: sensor.pond_water_temp_deep
title: Pond Water Temp Deep
```

Add a second card for `sensor.pond_water_temp_skimmer`.

### 6.4 Add History Graph

```yaml
type: statistics-graph
entities:
  - sensor.pond_water_depth
  - sensor.pond_water_temp_deep
  - sensor.pond_sensor_current
period: day
title: Pond History
chart_type: line
```

### 6.5 Example Dashboard YAML

Save as `pond_dashboard.yaml`:

```yaml
views:
  - title: Pond
    badges: []
    cards:
      - type: gauge
        entity: sensor.pond_water_depth
        min: 0
        max: 3.1
        title: Pond Depth
        unit_of_measurement: m
        severity:
          green: 2.0
          yellow: 1.0
          red: 0.5

      - type: gauge
        entity: sensor.pond_sensor_current
        min: 4
        max: 20
        title: Pond Sensor Current
        unit_of_measurement: mA

      - type: vertical-stack
        cards:
          - type: entities
            title: Water Temperature
            entities:
              - sensor.pond_water_temp_deep
              - sensor.pond_water_temp_skimmer

      - type: statistics-graph
        entities:
          - sensor.pond_water_depth
          - sensor.pond_water_temp_deep
        period: day
        title: 24 Hour History
        chart_type: line

      - type: entities
        title: Sensor Status
        entities:
          - sensor.pond_water_depth
          - sensor.pond_sensor_current
          - sensor.pond_water_temp_deep
          - sensor.pond_water_temp_skimmer
          - button.pond_node_restart
```

## Step 7: Advanced Configuration

### 7.1 Custom Sensor Template (Optional)

Create a template sensor to calculate tank volume:

```yaml
# Add to configuration.yaml
template:
  - sensor:
      - name: "Tank Volume"
        unique_id: water_tank_volume
        unit_of_measurement: "L"
        state: >
          {% set depth = states('sensor.pond_water_depth') | float(0) %}
          {% set area = 1.5 %}
          {{ (depth * area * 1000) | round(1) }}
        icon: mdi:water
```

### 7.2 Notification Services

Ensure you have notification service configured:

1. Go to **Settings → Devices & Services → Notifications**
2. Select mobile app or email notification
3. Enable in automations

### 7.3 Restart the Node Remotely

The current ESPHome config exposes a restart button in Home Assistant:

1. Open the device page for the pond node
2. Find `Pond Node Restart`
3. Press it to reboot the ESP32 over WiFi
4. Watch real-time sensor data

## Step 8: Troubleshooting

### Issue: Sensors Not Appearing in HA

**Check 1: ESPHome Device Online**
- Open the ESPHome dashboard
- Confirm the pond node is online and reachable
- If needed, open logs from ESPHome

**Check 2: ESPHome Logs**
- Verify WiFi connection succeeded
- Verify both DS18B20 addresses are detected
- Verify INA219 is reading current

**Check 3: Home Assistant ESPHome Integration**
- Go to **Settings → Devices & Services**
- Confirm the pond node appears as an ESPHome device

**Check 4: WiFi Connection**
- ESP32 should show connected WiFi IP on serial
- Try pinging ESP32 IP from PC

### Issue: Sensors Show "Unknown"

**Cause 1: Node offline or boot looping**
- Check if ESP32 is still running
- Check ESPHome logs for boot or sensor errors
- Use `Pond Node Restart` if remote reboot is needed

**Cause 2: WiFi or sensor issue**
- Check WiFi signal at pond
- Confirm one-wire pull-up and GPIO19 wiring
- Confirm INA219 is still visible on I2C

### Issue: ESPHome Device Not Updating

**Verify OTA/API settings in the YAML:**
- `api:` is enabled
- `ota:` password matches the deployed node
- WiFi credentials are correct

**Check sensor-specific behavior:**
- Water depth display can intentionally hold for 5 minutes inside the configured anti-flicker logic
- Temperature template sensors keep the last valid value through up to 3 consecutive read errors

### Issue: Home Assistant Unresponsive

- Don't run too many expensive automations
- 30-second sensor updates are fine for the current ESPHome setup
- Check HA system load: Settings → System → About
- Restart if needed: Settings → System → Restart

## Step 9: Backup & Restore

### 9.1 Backup Configuration

1. Go to **Settings → System → Backups**
2. Click **"Create Backup"**
3. Name it: "Water Tank Setup"
4. Download it to PC for safekeeping

### 9.2 Restore Configuration

If you need to restore:
1. Go to **Backups** section
2. Select backup
3. Click **"Restore"**

## Step 10: Next Steps

### Optional Enhancements

1. **Database Logging**
   - Automatically logs sensor data to database
   - Create long-term graphs
   - Settings → Devices & Services → History Stats

2. **Mobile App Notifications**
   - Install Home Assistant app on phone
   - Get push notifications for tank alerts

3. **YAML Automations**
   - Use advanced YAML for complex logic
   - Integrate with other smart home devices

4. **API Integrations**
   - Send data to external services
   - Create IFTTT rules
   - Log to cloud service

## Reference: Current ESPHome Entities

The active pond node exposes these primary Home Assistant entities:

```
sensor.pond_water_depth
sensor.pond_sensor_current
sensor.pond_water_temp_deep
sensor.pond_water_temp_skimmer
sensor.pond_node_wifi_rssi
sensor.pond_node_uptime
button.pond_node_restart
```

## Getting Help

If integration doesn't work:

1. **Check HA Logs:**
   - Settings → System → Logs
   - Look for MQTT errors

2. **Check Add-on Logs:**
   - Settings → Add-ons → Mosquitto → Logs
   - Look for connection errors

3. **Use MQTT Explorer:**
   - Download MQTT Explorer desktop app
   - Connect to `192.168.1.100:1883`
   - Browse topic tree to verify data

4. **Home Assistant Community:**
   - https://community.home-assistant.io/
   - Search for MQTT + ESP32 questions

## Reference Links

- [Home Assistant MQTT Documentation](https://www.home-assistant.io/integrations/mqtt/)
- [Home Assistant Green Docs](https://www.home-assistant.io/installation/home-assistant-green/)
- [Mosquitto Documentation](https://mosquitto.org/documentation/)
- [MQTT Discovery Format](https://www.home-assistant.io/integrations/mqtt/#discovery)
