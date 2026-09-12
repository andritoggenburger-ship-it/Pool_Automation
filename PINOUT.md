# ESP32-WROOM-32U (38-pin) Pinout Reference

## Quick Reference: Pins Used in This Project

| GPIO | Function | Connected To | Wire Color (Suggested) |
|------|----------|--------------|----------------------|
| 3.3V | Power | INA219 VCC, DS18B20 VCC × 2 | Red |
| GND | Ground | INA219 GND, DS18B20 GND × 2, 24V GND | Black |
| GPIO 19 | One-Wire Data | DS18B20 deep + skimmer data lines | Yellow |
| GPIO 21 | I2C SDA | INA219 SDA | Green |
| GPIO 22 | I2C SCL | INA219 SCL | Blue |
| USB / 5V | Power | Buck Converter 5V USB output | Red/Black |

## Pond Deep Sensor Last-Meter Cable Mapping

For the final 1m segment to the deep DS18B20 sensor, this project uses an Ethernet twisted-pair cable with the following mapping:

- DS18B20 data (yellow) -> Ethernet green
- DS18B20 ground -> Ethernet green/white
- DS18B20 3.3V -> Ethernet blue

Keep this mapping unchanged unless rewiring is documented and tested.

## Board Layout (Generic 38-pin ESP32-WROOM-32U DevKit)

```
Left header (top to bottom):      Right header (top to bottom):
CLK   (internal flash, unusable)  5V
D0    (internal flash, unusable)  CMD  (internal flash, unusable)
D1    (internal flash, unusable)  D3   (internal flash, unusable)
GPIO 15                           D2   (internal flash, unusable)
GPIO 2                            GPIO 13
GPIO 0                            GND
GPIO 4  ← STATUS LED              GPIO 14
GPIO 16                           GPIO 27
GPIO 12                           GPIO 26
GPIO 5                            GPIO 25
GPIO 18                           GPIO 33
GPIO 19 ← ONE-WIRE DATA           GPIO 32
GND                               GPIO 35 (input only)
GPIO 21 ← I2C SDA                 GPIO 34 (input only)
RX (GPIO3)                        VN (GPIO39, input only)
TX (GPIO1)                        VP (GPIO36, input only)
GPIO 22 ← I2C SCL                 EN
GND                               3V3
```

Notes:
- `CLK`, `D0`, `D1`, `D2`, `D3`, `CMD` pins are wired to the module's internal SPI flash and must never be used for external wiring.
- `GPIO 34/35/36/39` are input-only (no internal pull-up/down, cannot drive outputs).
- `GPIO 0`, `2`, `12`, `15` are strapping pins sampled at boot — avoid connecting pull-down/pull-up loads that could force the board into download mode or brown out flash voltage.

## Detailed Pin Descriptions

### Power Pins

| Pin | Name | Voltage | Usage | Status |
|-----|------|---------|-------|--------|
| 3V3 | 3.3V | 3.3V | Sensor power (INA219, DS18B20) | **Used** ✅ |
| 5V | 5V | 5V | Onboard 5V rail (from USB/DC jack) | Not used directly |
| USB-C / DC jack | 5V | 5V | Main power from buck converter | **Used** ✅ |
| GND | GND | 0V | Ground reference | **Used** ✅ (shared) |

### GPIO Pins - Used

| GPIO | I/O | Special Function | Project Use | Status |
|------|-----|------------------|------------|--------|
| 19 | I/O | General purpose | One-Wire Data (DS18B20) | **Used** ✅ |
| 21 | I/O | Default I2C SDA | I2C SDA (INA219) | **Used** ✅ |
| 22 | I/O | Default I2C SCL | I2C SCL (INA219) | **Used** ✅ |

### GPIO Pins - Available for Future Use

| GPIO | I/O | Special Function | Status |
|------|-----|------------------|--------|
| 13 | I/O | GPIO | Available |
| 14 | I/O | GPIO, ADC | Available |
| 16 | I/O | GPIO | Available |
| 18 | I/O | GPIO, SPI | Available |
| 25 | I/O | GPIO, ADC, DAC | Available |
| 26 | I/O | GPIO, ADC, DAC | Available |
| 27 | I/O | GPIO, ADC | Available |
| 32 | I/O | GPIO, ADC | Available |
| 33 | I/O | GPIO, ADC | Available |
| 34, 35, 36, 39 | Input only | ADC only, no output/pull-up | Available for sensing only |

### GPIO Pins - Reserved / Avoid

| GPIO | Reason |
|------|--------|
| 0, 2, 12, 15 | Strapping pins sampled at boot |
| 1 (TX0), 3 (RX0) | Used for USB/serial console |
| 6, 7, 8, 9, 10, 11 (CLK/D0/D1/D2/D3/CMD) | Wired to internal SPI flash, not usable |

## Wiring Checklist

- [ ] **ESP32 USB/DC Power** ← Buck Converter output (5V)
- [ ] **ESP32 3.3V** ← INA219 VCC
- [ ] **ESP32 3.3V** ← DS18B20 Deep VCC + DS18B20 Skimmer VCC
- [ ] **ESP32 GND** ← INA219 GND + both DS18B20 grounds
- [ ] **ESP32 GPIO 21** ← INA219 SDA (I2C data)
- [ ] **ESP32 GPIO 22** ← INA219 SCL (I2C clock)
- [ ] **ESP32 GPIO 19** ← DS18B20 deep + skimmer data (with 4.7kΩ pull-up to 3.3V)
- [ ] **24V Supply GND** ← Common GND (tied to ESP32 GND)
- [ ] **24V Supply +** ← Water Sensor VCC

## Important Notes

### 3.3V Power Limitations
- Onboard regulator typically supports a few hundred mA
- Your project uses:
  - INA219: ~5-10mA
  - DS18B20 × 2: ~2-5mA each (~7mA total typical)
  - **Total: ~20mA (Safe)**

### GPIO 21 & 22 (I2C Pins)
- These are the default hardware I2C pins on classic ESP32 boards
- Frequency: 100kHz configured (hardware supports up to 1MHz)
- Internal pull-ups are weak; external 4.7kΩ pull-ups recommended for reliable I2C

### GPIO 19 (One-Wire)
- Must have external 4.7kΩ pull-up resistor
- **Connect between 3.3V and GPIO 19**
- Critical for 3m cable runs

## Connecting Sensors to ESP32

### INA219 (I2C Current Sensor)
```
INA219 Pin    ESP32 Pin    Function
──────────────────────────────────
VCC        →  3.3V        3.3V Power
GND        →  GND         Ground
SDA        →  GPIO 21     I2C Data
SCL        →  GPIO 22     I2C Clock
```

### DS18B20 (One-Wire Temperature Sensor)
```
DS18B20 Pin    ESP32 Pin       Function
──────────────────────────────────────────
VCC (Red)   →  3.3V           3.3V Power
DQ (Yellow) →  GPIO 19 (with 4.7k pull-up to 3.3V)
GND (Black) →  GND            Ground
```

**Both DS18B20 sensors share the same data pin (GPIO 19)**

## ESP32-WROOM-32U Specifications

| Spec | Value |
|------|-------|
| Processor | Xtensa dual-core 32-bit LX6, up to 240MHz |
| RAM | 520KB SRAM |
| Flash | Typically 4MB Quad SPI |
| WiFi | 802.11b/g/n 2.4GHz |
| Bluetooth | Classic + BLE |
| GPIO | 38-pin board, ~25 usable GPIOs (see reserved list above) |
| I2C | 2 hardware interfaces |
| SPI | 4 hardware interfaces (2 usable, others reserved for flash) |
| UART | 3 hardware interfaces |
| ADC | 2 × 12-bit SAR ADC (ADC2 shared with WiFi) |
| Antenna | External via U.FL connector (the "U" in WROOM-32U) |
| Voltage | 3.3V logic, NOT 5V tolerant |

## Temperature Operating Range
- **Storage**: -40°C to +85°C (module dependent)
- **Operating**: -40°C to +85°C
- Suitable for outdoor pond monitoring

## Further Reading

- [ESP32 Series Datasheet](https://www.espressif.com/sites/default/files/documentation/esp32_datasheet_en.pdf)
- [ESP32-WROOM-32U Datasheet](https://www.espressif.com/sites/default/files/documentation/esp32-wroom-32u_datasheet_en.pdf)
- Pinout images are available in the WaveShare wiki above
