# ESP32-C6 Zero Pinout Reference

## Quick Reference: Pins Used in This Project

| GPIO | Function | Connected To | Wire Color (Suggested) |
|------|----------|--------------|----------------------|
| 3.3V | Power | INA219 VCC, DS18B20 VCC × 3 | Red |
| GND | Ground | INA219 GND, DS18B20 GND × 3, 24V GND | Black |
| GPIO 8 | Onboard RGB LED | WS2812 status LED | Purple |
| GPIO 10 | One-Wire Data | DS18B20 × 3 data lines | Yellow |
| GPIO 20 | I2C SDA | INA219 SDA | Green |
| GPIO 21 | I2C SCL | INA219 SCL | Blue |
| USB | Power | Buck Converter 5V USB output | Red/Black |

## Full Pinout Diagram

```
ESP32-C6 Zero Mini Development Board (with Headers)

TOP VIEW - Left Side (Pin Headers):
┌─────────────────────────────┐
│  GND        ← GND (common)  │ Pin 1
│  GPIO 3     (ADC)           │ Pin 2
│  GPIO 2     (ADC)           │ Pin 3
│  GPIO 1     (RTC)           │ Pin 4
│  GPIO 0     (RTC)           │ Pin 5
│  GPIO 5     (GPIO)          │ Pin 6
│  GPIO 6     (GPIO)          │ Pin 7
│  GPIO 7     (GPIO)          │ Pin 8
│  GPIO 8   ← WS2812 RGB LED  │ Pin 9
│  GPIO 10  ← ONE-WIRE DATA   │ Pin 11
│  GPIO 4    (GPIO)           │ Pin 12
│  GPIO 18   (GPIO)           │ Pin 13
│  GPIO 19   (GPIO)           │ Pin 14
│  GPIO 20  ← I2C SDA         │ Pin 15
│  GPIO 21  ← I2C SCL         │ Pin 16
│  3.3V     ← POWER (sensors) │ Pin 17
│  5V       (from USB)        │ Pin 18
│  GND      ← GND             │ Pin 19
└─────────────────────────────┘

TOP VIEW - Right Side (USB and GND):
┌─────────────────────────────┐
│  USB ← POWER (from buck)    │ Micro USB
│  GND ← COMMON GROUND        │ Ground
└─────────────────────────────┘
```

## Detailed Pin Descriptions

### Power Pins

| Pin | Name | Voltage | Usage | Status |
|-----|------|---------|-------|--------|
| 17 | 3.3V | 3.3V | Sensor power (INA219, DS18B20) | **Used** ✅ |
| 18 | 5V | 5V | Onboard 5V rail (from USB) | Not used in this project |
| USB | 5V USB | 5V | Main power from buck converter | **Used** ✅ |
| 1 | GND | 0V | Ground reference | **Used** ✅ (shared) |
| 19 | GND | 0V | Ground reference | **Used** ✅ (shared) |

### GPIO Pins - Used

| GPIO | Pin # | I/O | Special Function | Project Use | Status |
|------|-------|-----|------------------|------------|--------|
| 8 | 9 | I/O | WS2812 data (board-specific) | Onboard RGB LED | **Used** ✅ |
| 10 | 11 | I/O | GPIO | One-Wire Data (DS18B20) | **Used** ✅ |
| 20 | 15 | I/O | GPIO | I2C SDA (INA219) | **Used** ✅ |
| 21 | 16 | I/O | GPIO | I2C SCL (INA219) | **Used** ✅ |

### GPIO Pins - Available for Future Use

| GPIO | Pin # | I/O | Special Function | Status |
|------|-------|-----|------------------|--------|
| 0 | 5 | I/O | RTC GPIO, can wake from deep sleep | Available |
| 1 | 4 | I/O | RTC GPIO | Available |
| 2 | 3 | I/O | ADC, RTC GPIO | Available |
| 3 | 2 | I/O | ADC, RTC GPIO | Available |
| 4 | 12 | I/O | GPIO, ADC | Available |
| 5 | 6 | I/O | GPIO | Available |
| 6 | 7 | I/O | GPIO | Available |
| 7 | 8 | I/O | GPIO | Available |
| 18 | 13 | I/O | GPIO, SPI | Available |
| 19 | 14 | I/O | GPIO, SPI | Available |

## Physical Layout

```
WaveShare ESP32-C6 Zero Mini Board:

Front View (Component Side):
┌─────────────────────────────┐
│  ◎ ◎ ◎ ◎ ◎ ◎ ◎ ◎ ◎ ◎ ◎ ◎  │ ← Left Pin Header (Pins 1-12)
│                             │
│  [Micro USB] [ESP32-C6]     │ ← USB Port, Main Chip
│    (Power)   (SoC)         │
│                             │
│  ◎ ◎ ◎ ◎ ◎ ◎ ◎ ◎ ◎ ◎ ◎ ◎  │ ← Right Pin Header (Pins 13-19+GND)
└─────────────────────────────┘

Pin Header Pin Numbers (Left Side):
Pin 1:  GND
Pin 2:  GPIO 3
Pin 3:  GPIO 2
Pin 4:  GPIO 1
Pin 5:  GPIO 0
Pin 6:  GPIO 5
Pin 7:  GPIO 6
Pin 8:  GPIO 7
Pin 9:  GPIO 8  ← WS2812 RGB LED (onboard)
Pin 10: GPIO 9
Pin 11: GPIO 10 ← ONE-WIRE DATA
Pin 12: GPIO 4

Pin Header Pin Numbers (Right Side):
Pin 13: GPIO 18
Pin 14: GPIO 19
Pin 15: GPIO 20
Pin 16: GPIO 21
Pin 17: 3.3V   ← POWER
Pin 18: 5V
Pin 19: GND

Micro USB: Connected to buck converter 5V USB output
```

## Wiring Checklist

- [ ] **ESP32 USB Port** ← Buck Converter USB (5V)
- [ ] **ESP32 Pin 1 (GND)** ← Common GND from 24V supply
- [ ] **ESP32 Pin 17 (3.3V)** ← INA219 VCC
- [ ] **ESP32 Pin 17 (3.3V)** ← DS18B20 VCC
- [ ] **ESP32 Pin 19 (GND)** ← INA219 GND + DS18B20 GND (shared)
- [ ] **ESP32 GPIO 20 (Pin 15)** ← INA219 SDA (I2C data)
- [ ] **ESP32 GPIO 21 (Pin 16)** ← INA219 SCL (I2C clock)
- [ ] **ESP32 GPIO 10 (Pin 11)** ← DS18B20 × 3 data (with 4.7kΩ pull-up to Pin 17)
- [ ] **24V Supply GND** ← Common GND (tied to ESP32 GND)
- [ ] **24V Supply +** ← Water Sensor VCC

## Important Notes

### Pin 17 (3.3V) Power Limitations
- Provides 3.3V output from onboard regulator
- Max current: ~200mA typical
- Your project uses:
  - INA219: ~5-10mA
  - DS18B20 × 3: ~2-5mA each (~10mA total)
  - **Total: ~20mA (Safe)**

### GPIO 20 & 21 (I2C Pins)
- Assigned to INA219 in this project to keep GPIO8 available for onboard LED
- Frequency: 400kHz standard (hardware supports up to 1MHz)
- Internal pull-ups: ~20-50kΩ
- May need external 4.7kΩ pull-ups for reliable I2C

### GPIO 10 (One-Wire)
- Must have external 4.7kΩ pull-up resistor
- **Connect between Pin 17 (3.3V) and Pin 11 (GPIO 10)**
- Critical for 3m cable runs

### USB Power
- Micro USB port on bottom of board
- Provides 5V when connected to buck converter
- Supplies onboard regulator (produces 3.3V for GPIO)
- Also charges internal capacitors

## Connecting Sensors to ESP32

### INA219 (I2C Current Sensor)
```
INA219 Pin    ESP32 Pin    Function
──────────────────────────────────
VCC        →  Pin 17      3.3V Power
GND        →  Pin 1 or 19 Ground
SDA        →  Pin 15      I2C Data
SCL        →  Pin 16      I2C Clock
```

### DS18B20 (One-Wire Temperature Sensor)
```
DS18B20 Pin    ESP32 Pin       Function
──────────────────────────────────────────
VCC (Red)   →  Pin 17         3.3V Power
DQ (Yellow) →  Pin 11 (with 4.7k pull-up to Pin 17)
GND (Black) →  Pin 1 or 19    Ground
```

**All 3 DS18B20 sensors share the same data pin (Pin 11)**

## ESP32-C6 Specifications

| Spec | Value |
|------|-------|
| Processor | RISC-V single-core 160MHz |
| RAM | 320KB SRAM |
| Flash | 4MB Quad SPI |
| WiFi | 802.11b/g/n 2.4GHz |
| GPIO | 22 total (19 usable) |
| I2C | 1 hardware interface |
| SPI | 2 hardware interfaces |
| UART | 2 hardware interfaces |
| ADC | 7 channels, 12-bit |
| USB | 1 × Micro USB (Serial + Power) |
| Voltage | 3.3V logic, 5V tolerant on most pins |

## Temperature Operating Range
- **Storage**: -40°C to +85°C
- **Operating**: -40°C to +85°C
- Suitable for outdoor pond monitoring

## Further Reading

- [ESP32-C6 Datasheet](https://www.espressif.com/sites/default/files/documentation/esp32-c6_datasheet_en.pdf)
- [WaveShare ESP32-C6 Zero Manual](https://www.waveshare.com/wiki/ESP32-C6_Zero)
- Pinout images are available in the WaveShare wiki above
