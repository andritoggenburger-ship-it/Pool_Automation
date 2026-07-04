# Home Assistant Green Integration Guide

## Overview

This guide walks through integrating your ESP32 water tank monitoring system with **Home Assistant Green** via MQTT.

**What you'll have after this guide:**
- ✅ Automatic sensor discovery in Home Assistant
- ✅ Real-time water tank depth, temperature, and current readings
- ✅ Automations based on tank level
- ✅ Dashboard with gauges and graphs
- ✅ Alerts when tank is empty or full

## Prerequisites

- Home Assistant Green running on your network
- MQTT broker installed and running (included with HA Green)
- ESP32 with firmware uploaded (from `main.py`)
- WiFi network accessible to both devices

## Step 1: Enable MQTT on Home Assistant Green

### 1.1 Verify MQTT is Available

Home Assistant Green comes with Mosquitto MQTT broker add-on pre-installed.

1. Open Home Assistant at `http://homeassistant.local:8123/`
2. Go to **Settings → Add-ons** (or search for "Add-ons")
3. Click **"Add-on Store"** (bottom right)
4. Search for **"Mosquitto"**
5. Check if it shows as "Installed" (if not, install it)

### 1.2 Start Mosquitto if Not Running

1. Go to **Settings → Add-ons → Mosquitto broker**
2. Click **"Start"** button
3. Check **"Start on boot"** (recommended)
4. Look for green checkmark indicating it's running

### 1.3 Note the Broker IP Address

1. Go to **Settings → System → Network**
2. Find the IPv4 address (e.g., `192.168.1.100`)
3. This is your `MQTT_BROKER` IP for the ESP32 config

## Step 2: Configure MQTT in Home Assistant

### 2.1 Enable MQTT Integration

1. Go to **Settings → Devices & Services**
2. Click **"Create Automation"** button (bottom right)
3. Search for **"MQTT"**
4. If not found, install via "Add Integration"
5. Select **"MQTT"**

### 2.2 MQTT Configuration

Select **"Mosquitto broker"** (the add-on you installed)

**Configuration:**
```yaml
broker: localhost  # Or your HA Green IP
username: (leave blank if no auth)
password: (leave blank if no auth)
discovery_prefix: homeassistant
```

Click **"Submit"** and **"Finish"**

### 2.3 Verify MQTT Connection

1. Go to **Developer Tools → MQTT**
2. Subscribe to: `#` (shows all topics)
3. You should see incoming messages once ESP32 connects

## Step 3: Configure ESP32

### 3.1 Edit Configuration in main.py

Open `main.py` on the ESP32 and update:

```python
# WiFi Settings
WIFI_SSID = "Your_WiFi_SSID"
WIFI_PASSWORD = "Your_WiFi_Password"

# MQTT Broker (Home Assistant Green)
MQTT_BROKER = "192.168.1.100"  # Your HA Green IP (from Step 1.3)
MQTT_PORT = 1883
MQTT_USER = None  # If no authentication
MQTT_PASSWORD = None
```

### 3.2 Upload Updated main.py

Use **Thonny IDE** or WebREPL to upload the modified `main.py` to ESP32:

1. Connect to ESP32 via Thonny
2. Open `main.py`
3. Make changes (WiFi SSID, HA IP)
4. Save and upload
5. Restart ESP32

### 3.3 Verify Connection

Check serial console (115200 baud):
```
[2024-XX-XX HH:MM:SS] Connecting to WiFi: Your_WiFi_SSID
[2024-XX-XX HH:MM:SS] WiFi connected: ('192.168.1.50', ...)
[2024-XX-XX HH:MM:SS] MQTT connected to 192.168.1.100:1883
[2024-XX-XX HH:MM:SS] Found 3 DS18B20 sensors
[2024-XX-XX HH:MM:SS] INA219 initialized at 0x40
[2024-XX-XX HH:MM:SS] Home Assistant Discovery published
```

## Step 4: Verify Sensors Appear in Home Assistant

### 4.1 Check Device Discovery

1. Go to **Settings → Devices & Services → MQTT**
2. You should see **"Water Tank"** device
3. Click on it to see discovered entities:
   - Water Tank Temp 1
   - Water Tank Temp 2
   - Water Tank Temp 3
   - Water Tank Current
   - Water Tank Depth

### 4.2 View Sensor Values

1. Go to **Dashboard**
2. Click **"+ Create Card"** → **"By Entity"**
3. Select each sensor to add to dashboard:
   - `sensor.water_tank_temp_1`
   - `sensor.water_tank_temp_2`
   - `sensor.water_tank_temp_3`
   - `sensor.water_tank_depth`
   - `sensor.water_tank_current`

### 4.3 Format Display

For each card, configure:
- **Thermostat Card** for temperatures (shows gauge)
- **Gauge Card** for depth (0-5m range)
- **Number Card** for current (0-25mA range)

## Step 5: Create Automations

### 5.1 Alert When Tank is Empty

**Automation: Low Water Tank**

1. Go to **Settings → Automations & Scenes → Create Automation**
2. **Trigger**: State
   - Entity: `sensor.water_tank_depth`
   - Condition: Less than `0.5`m
   - For at least: 5 minutes
3. **Action**: Notification
   - Title: "⚠️ Water Tank Alert"
   - Message: "Tank depth is {{ state_attr('sensor.water_tank_depth', 'state') }}m"
   - Notify service: `notify.notify` (or your phone)

### 5.2 Alert When Tank is Full

**Automation: High Water Tank**

1. **Trigger**: State
   - Entity: `sensor.water_tank_depth`
   - Condition: Greater than `4.5`m
   - For at least: 5 minutes
2. **Action**: Notification
   - Title: "✅ Water Tank Full"
   - Message: "Tank is at {{ state_attr('sensor.water_tank_depth', 'state') }}m"

### 5.3 Temperature Alert

**Automation: Abnormal Temperature**

1. **Trigger**: State
   - Entity: `sensor.water_tank_temp_1`
   - Condition: Greater than `35`°C (adjust as needed)
2. **Action**: Notification
   - Title: "🌡️ High Water Temperature"
   - Message: "Tank temperature: {{ state_attr('sensor.water_tank_temp_1', 'state') }}°C"

### Example YAML Automation

Add to `automations.yaml`:

```yaml
- id: low_water_tank
  alias: "Low Water Tank Alert"
  trigger:
    - platform: numeric_state
      entity_id: sensor.water_tank_depth
      below: 0.5
      for:
        minutes: 5
  action:
    - service: notify.notify
      data:
        title: "⚠️ Water Tank Alert"
        message: >
          Tank depth is low: 
          {{ states('sensor.water_tank_depth') }}m

- id: high_water_tank
  alias: "High Water Tank Alert"
  trigger:
    - platform: numeric_state
      entity_id: sensor.water_tank_depth
      above: 4.5
      for:
        minutes: 5
  action:
    - service: notify.notify
      data:
        title: "✅ Water Tank Full"
        message: >
          Tank is now: 
          {{ states('sensor.water_tank_depth') }}m

- id: high_temp_alert
  alias: "High Water Temperature"
  trigger:
    - platform: numeric_state
      entity_id: sensor.water_tank_temp_1
      above: 35
      for:
        minutes: 10
  action:
    - service: notify.notify
      data:
        title: "🌡️ High Temperature"
        message: >
          Tank temp: 
          {{ states('sensor.water_tank_temp_1') }}°C
```

## Step 6: Create Dashboard

### 6.1 Create Custom Dashboard

1. Go to **Dashboard**
2. Click **"+ Create Dashboard"**
3. Name it: **"Water Tank"**
4. Click **"Create"**

### 6.2 Add Gauge Cards

**Depth Gauge:**
```yaml
type: gauge
entity: sensor.water_tank_depth
min: 0
max: 5
title: Water Tank Depth
unit_of_measurement: m
```

**Current Gauge:**
```yaml
type: gauge
entity: sensor.water_tank_current
min: 0
max: 25
title: Water Sensor Current
unit_of_measurement: mA
```

### 6.3 Add Temperature Cards

```yaml
type: custom:thermostat-card
entity: sensor.water_tank_temp_1
title: Tank Temperature (Sensor 1)
```

Repeat for `sensor.water_tank_temp_2` and `sensor.water_tank_temp_3`

### 6.4 Add History Graph

```yaml
type: statistics-graph
entities:
  - sensor.water_tank_depth
  - sensor.water_tank_temp_1
  - sensor.water_tank_current
period: day
title: Water Tank History
chart_type: line
```

### 6.5 Example Dashboard YAML

Save as `water_tank_dashboard.yaml`:

```yaml
views:
  - title: Water Tank
    badges: []
    cards:
      - type: gauge
        entity: sensor.water_tank_depth
        min: 0
        max: 5
        title: Tank Depth
        unit_of_measurement: m
        severity:
          green: 2.0
          yellow: 1.0
          red: 0.5

      - type: gauge
        entity: sensor.water_tank_current
        min: 4
        max: 20
        title: Sensor Current
        unit_of_measurement: mA

      - type: vertical-stack
        cards:
          - type: entities
            title: Water Temperature
            entities:
              - sensor.water_tank_temp_1
              - sensor.water_tank_temp_2
              - sensor.water_tank_temp_3

      - type: statistics-graph
        entities:
          - sensor.water_tank_depth
          - sensor.water_tank_temp_1
        period: day
        title: 24 Hour History
        chart_type: line

      - type: entities
        title: Sensor Status
        entities:
          - sensor.water_tank_depth
          - sensor.water_tank_current
          - sensor.water_tank_temp_1
          - sensor.water_tank_temp_2
          - sensor.water_tank_temp_3
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
          {% set depth = states('sensor.water_tank_depth') | float(0) %}
          {% set area = 1.5 %}
          {{ (depth * area * 1000) | round(1) }}
        icon: mdi:water
```

### 7.2 Notification Services

Ensure you have notification service configured:

1. Go to **Settings → Devices & Services → Notifications**
2. Select mobile app or email notification
3. Enable in automations

### 7.3 MQTT Topic Monitoring

View all published topics:

1. Go to **Developer Tools → MQTT**
2. Click **"Subscribe to a topic"**
3. Enter: `water_tank/#`
4. Watch real-time sensor data

## Step 8: Troubleshooting

### Issue: Sensors Not Appearing in HA

**Check 1: MQTT Connection**
```
Developer Tools → MQTT → Subscribe to: homeassistant/sensor/#
Should see discovery topics like: 
  homeassistant/sensor/water_tank_sensor/temp_1/config
```

**Check 2: ESP32 Serial Output**
- Look for "MQTT connected" message
- Look for "Home Assistant Discovery published"

**Check 3: MQTT Broker Running**
- Settings → Add-ons → Mosquitto → Check "Started" status

**Check 4: WiFi Connection**
- ESP32 should show connected WiFi IP on serial
- Try pinging ESP32 IP from PC

### Issue: Sensors Show "Unknown"

**Cause 1: No data published recently**
- Check if ESP32 is still running
- Verify 5-minute update interval hasn't passed
- Check serial console for errors

**Cause 2: MQTT disconnected**
- Check WiFi signal at pond
- Check firewall allows port 1883
- Check MQTT broker log: Settings → Add-ons → Mosquitto → Logs

### Issue: MQTT Discovery Not Working

**Verify Discovery Prefix:**
```python
# In main.py, should be:
HA_DISCOVERY_PREFIX = "homeassistant"
```

**Check Sensor Names:**
```python
# Make sure these exist:
DEVICE_ID = "water_tank_sensor"
DEVICE_NAME = "Water Tank"
```

### Issue: Home Assistant Unresponsive

- Don't run too many expensive automations
- 5-minute sensor updates are fine
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

## Reference: MQTT Topics

Your ESP32 publishes to:

```
Discovery Topics (auto-created):
homeassistant/sensor/water_tank_sensor/temp_1/config
homeassistant/sensor/water_tank_sensor/temp_2/config
homeassistant/sensor/water_tank_sensor/temp_3/config
homeassistant/sensor/water_tank_sensor/current/config
homeassistant/sensor/water_tank_sensor/depth/config

Data Topics (updates every 5 minutes):
water_tank/sensors/temp_1
water_tank/sensors/temp_2
water_tank/sensors/temp_3
water_tank/sensors/current
water_tank/sensors/depth
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
