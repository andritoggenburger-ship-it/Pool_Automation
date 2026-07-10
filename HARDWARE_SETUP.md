# Hardware Setup Guide

## Parts List

| Item | Qty | Notes |
|------|-----|-------|
| WaveShare ESP32-C6 Zero | 1 | Main microcontroller |
| DS18B20 Temperature Sensor | 3 | Waterproof probe version recommended |
| GY-INA219 I2C Current Sensor | 1 | With 0.1Ω shunt resistor |
| 4-20mA Water Level Sensor | 1 | 5M range, 24V compatible |
| Resistor 4.7kΩ 1/4W | 1 | One-wire pull-up (essential for 3m cable) |
| Resistor 4.7kΩ 1/4W | 2 | I2C pull-ups (if not on sensor boards) |
| Shielded Twisted Pair Cable | 10m | For 3m sensor runs (recommended) |
| DC 24V Power Supply | 1 | Primary power source (e.g., 5A) |
| 9-36V to 5V Buck Converter | 1 | Converts 24V to 5V 5A for ESP32 and sensors |
| USB Cable (optional) | 1 | Alternative to buck converter output |

## Detailed Wiring

### 0. Power Supply and Buck Converter (Primary)

**24V to 5V Conversion:**
```
DC 24V Supply
    │
    ├─ Positive (+24V) ────► Buck Converter IN+
    │
    └─ Negative (GND) ────► Buck Converter IN- (GND)


Buck Converter Module Output:
    ├─ 5V OUT ────────────► ESP32 USB Power Input
    └─ GND ────────────────► ESP32 GND (Common GND)
```

**Buck Converter Specifications:**
- Input: 9-36V DC (handles 24V safely)
- Output: USB 5V 5A (powers ESP32 directly)
- Connection: Screw terminals (24V in) → USB port out
- Protection: Usually includes overload and thermal protection

**Power Distribution from ESP32:**
Once ESP32 is powered via USB, it provides 3.3V for sensors:
```
ESP32 3.3V pin ───► INA219 VCC
ESP32 3.3V pin ───► DS18B20 VCC × 3
ESP32 GND pin ────► All sensor grounds (common GND)
```

**Advantages of this configuration:**
- ✅ USB connection is clean and standardized
- ✅ ESP32's 3.3V output easily powers small sensors
- ✅ All sensor grounds tied to ESP32 (low noise)
- ✅ Water sensor powered directly from 24V (no buck converter needed for it)

### 1. One-Wire Temperature Sensors (DS18B20)

**Single Bus Configuration** (all 3 sensors share same data line)

```
ESP32 GPIO 10 ──[4.7kΩ Pull-up]── +3.3V
      |
      ├─── DS18B20 #1
      |     ├─ Data (middle pin)
      |     ├─ GND (left pin)
      |     └─ VCC (right pin)
      |
      ├─── DS18B20 #2
      |     ├─ Data (middle pin)
      |     ├─ GND (left pin)
      |     └─ VCC (right pin)
      |
      └─── DS18B20 #3
            ├─ Data (middle pin)
            ├─ GND (left pin)
            └─ VCC (right pin)

All GND pins → ESP32 GND
All VCC pins → ESP32 3.3V pin
```

**Pull-up Resistor Installation:**
```
+3.3V ───[4.7kΩ]───┬─── GPIO 10
                   │
              100nF capacitor
                   │
                  GND
```

### 2. I2C Current Sensor (GY-INA219)

```
INA219 Board          ESP32-C6
┌────────────────┐
│ VCC ─────────────── 3.3V (from ESP32)
│ GND ─────────────── GND (from ESP32)
│ SCL ───────────────► GPIO 21 (I2C Clock)
│ SDA ───────────────► GPIO 20 (I2C Data)
└────────────────┘

Optional: Add 4.7kΩ pull-ups on SDA/SCL if not on board:
    3.3V ──[4.7kΩ]── SDA (GPIO 20)
    3.3V ──[4.7kΩ]── SCL (GPIO 21)
```

### 3. Water Level Sensor (4-20mA) + INA219

```
Water Level Sensor (4-20mA Output, 24V powered)
    │
    ├─ Red (VCC) ─────────► 24V Supply (+)
    ├─ Black (GND) ───────► 24V Supply (-) / Common GND
    └─ Yellow (Signal) ───► INA219 IN+ (measures current)

INA219 Shunt Connections (green terminal block)
    ├─ IN+ ◄─── Yellow wire from water sensor (4-20mA signal)
    └─ IN- ◄─── GND (Common ground)
```

**Current Flow Path:**
```
24V Supply → Water Sensor → Signal (4-20mA) → INA219 IN+ → Shunt (0.1Ω) → INA219 IN- → GND
```

**Key Points:**
- Water sensor powered directly from 24V supply
- 4-20mA current loop is independent of buck converter
- INA219 measures current and calculates depth
- All grounds must be common (24V GND = ESP32 GND)

### 4. Complete Wiring Summary

**Power Supply Chain:**
```
24V DC Supply → Buck Converter USB → ESP32 USB Port → ESP32 powers sensors via 3.3V
```

**Detailed Connections:**

| Source | Destination | Function | Voltage |
|--------|-------------|----------|---------|
| 24V Supply + | Buck Converter IN+ | Power input | 24V |
| 24V Supply - | Buck Converter IN- | Ground/Return | GND |
| Buck Converter USB | ESP32 USB Port | Main power | 5V |
| **ESP32 3.3V** | **INA219 VCC** | **Sensor power** | **3.3V** |
| **ESP32 3.3V** | **DS18B20 VCC × 3** | **Sensor power** | **3.3V** |
| **24V Supply +** | **Water Sensor VCC** | **Water sensor power** | **24V** |
| 24V Supply - | Water Sensor GND | Water sensor return | GND |
| ESP32 GND | INA219 GND | Ground | GND |
| ESP32 GND | DS18B20 GND × 3 | Ground | GND |
| ESP32 GPIO 10 | DS18B20 × 3 data | One-wire data | 3.3V (pulled up via 4.7kΩ) |
| ESP32 GPIO 20 (SDA) | INA219 SDA | I2C data | 3.3V |
| ESP32 GPIO 21 (SCL) | INA219 SCL | I2C clock | 3.3V |
| Water Sensor Signal | INA219 IN+ | 4-20mA current | 0-24V analog |

**Simplified ESP32 Pin Usage:**
```
ESP32 USB Port    ← Buck Converter USB 5V (main power)
ESP32 3.3V pin    → INA219 VCC + DS18B20 VCC × 3
ESP32 GND pin     → All sensors + 24V supply GND (common)
ESP32 GPIO 10     → DS18B20 × 3 data (with 4.7kΩ pull-up to 3.3V)
ESP32 GPIO 20 SDA → INA219 SDA
ESP32 GPIO 21 SCL → INA219 SCL
```

## Cable Length Recommendations

| Cable | Length | Type | Notes |
|-------|--------|------|-------|
| One-Wire (GPIO 10 to sensors) | 3m | Shielded twisted pair | Use external 4.7kΩ pull-up |
| I2C (GPIO 20/21 to INA219) | 1m | Twisted pair + shield | Keep short if possible |
| Water sensor (to INA219) | 5m (built-in) | 4-20mA current loop | Less susceptible to noise |

## Signal Line Protection (Optional but Recommended)

For harsh outdoor/pond environment:

```
GPIO 10 Data Line:
    ESP32 ──[100Ω]──┬─── Sensor Data
                    │
                  Ferrite bead (optional)
                    │
                   GND

I2C Lines:
    Both SDA/SCL protected with:
    - Ferrite beads at ESP32 side
    - Twisted pair shielding
    - Shield grounded at ESP32 only
```

## Power Supply Considerations

### Your Setup: 24V Supply + Buck Converter with USB (Recommended)

**Configuration:**
```
24V Supply
    ├─ (+) ──► Buck Converter IN+ ──► USB Port ──► ESP32 USB
    │
    ├─ (-) ──► Buck Converter IN- ──► GND
    │                                  │
    │                                  └─ Common GND
    │
    └─ (+) ──► Water Sensor VCC (24V direct)
```

**How sensors get power:**
1. ESP32 draws 5V from buck converter USB port
2. ESP32's onboard regulator provides 3.3V
3. INA219 and DS18B20 sensors powered from ESP32 3.3V pin
4. Water sensor powered directly from 24V supply

**Advantages:**
- ✅ Simplest wiring (USB cable to ESP32)
- ✅ ESP32 3.3V safely powers small sensors
- ✅ Water sensor gets full 24V (no voltage loss over cable)
- ✅ All grounds common (low EMI)
- ✅ Buck converter USB is industry standard

**Key Point:** The water sensor is powered independently from 24V, while ESP32 and small sensors use regulated 5V→3.3V from the buck converter. This is optimal for long cable runs at the pond.

## Assembly Checklist

- [ ] ESP32-C6 Zero board
- [ ] 3× DS18B20 sensors with waterproof probes
- [ ] GY-INA219 board
- [ ] 4-20mA water depth sensor
- [ ] 4.7kΩ pull-up resistor for one-wire
- [ ] Shielded twisted pair cable
- [ ] Connectors (JST, terminal blocks, etc.)
- [ ] Power supply (USB + optionally 24V)
- [ ] Ferrite beads and capacitors for EMI protection

## Testing Procedure

1. **Visual Inspection**
   - No shorts between traces
   - All connections secure
   - Correct polarity on power

2. **Continuity Check** (with multimeter)
   - One-Wire: GPIO 10 → all sensor data pins
    - I2C SDA: GPIO 20 → INA219 SDA
    - I2C SCL: GPIO 21 → INA219 SCL
   - All GNDs connected

3. **Power-On Test**
   - Connect USB, check LED lights
   - No smoke or unusual heat
   - Serial console shows boot messages

4. **Sensor Discovery** (via WebREPL or serial)
   ```python
   # One-wire sensors
   from machine import Pin
   from onewire import OneWire
   ds_pin = Pin(10, Pin.IN, Pin.PULL_UP)
   ow = OneWire(ds_pin)
   print(ow.scan())  # Should show 3 device addresses
   
   # I2C devices
   from machine import I2C, Pin
    i2c = I2C(0, scl=Pin(21), sda=Pin(20), freq=400000)
   print([hex(x) for x in i2c.scan()])  # Should show 0x40
   ```

## Troubleshooting Wiring

### Problem: Sensors not detected
- Check GPIO pin numbers match code
- Verify pull-up resistor present for one-wire
- Test with multimeter: GPIO 10 should be ~3.3V when idle
- For I2C: both lines should be ~3.3V when idle

### Problem: Intermittent readings
- One-wire without external pull-up: add 4.7kΩ resistor
- Long cables: use shielded twisted pair
- Shield grounding issues: ground only at ESP32 side

### Problem: I2C devices not found
- Check SCL/SDA not swapped
- Verify 400kHz frequency works (try 100kHz for testing)
- Add pull-up resistors if not on board
- Disconnect and reconnect devices

### Problem: Current readings incorrect
- Verify shunt resistor is 0.1Ω (usually marked R100)
- Check water sensor wired to IN+/IN- correctly
- Verify signal polarity (positive current flow)
- Check 0Ω resistor jumpers on INA219 board

## Final Verification

Before deploying to pond:

1. All sensors reading in WebREPL ✓
2. MQTT publishing to Home Assistant ✓
3. Water depth calibration verified ✓
4. WiFi signal strength adequate ✓
5. Weatherproof enclosure sealed ✓
6. All cables rated for outdoor use ✓
7. Backup power plan (battery) ✓
