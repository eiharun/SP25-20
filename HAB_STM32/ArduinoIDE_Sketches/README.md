# STM32 Wiring Diagram

> NC - Not Connected

| RFM95W | STM32 |
| ------ | ----- |
| Vin    | 3v3   |
| GND    | GND   |
| EN     | NC    |
| G0     | D0    |
| SCK    | D13   |
| MISO   | D12   |
| MOSI   | D11   |
| CS     | D3    |
| RST    | D2    |
| G1     | NC    |
| G2     | NC    |
| G3     | NC    |
| G4     | NC    |
| G5     | NC    |

| Servo | STM32 |
| ----- | ----- |
| PWM   | D9    |
| Vin   | 3v3   |
| GND   | GND  |

| GPS  | STM32 |
| ---- | ----- |
| TX   |  D4   |
| RX   |  D5   |
| VCC  |  3v3  |
| GND  |  GND  |
| PPS  |  NC   |

| SD   | STM32 |
| ---- | ----- |
| VDD  |  3v3  |
| GND  |  GND  |
| DI   |  D12  |
| DO   |  D11  |
| SCLK |  D13  |
| CS   |  D6   |
| Other Pins | NC |

To program:

Follow instructions [here](https://github.com/stm32duino/Arduino_Core_STM32)

Boards Manager -> STM32 MCU based boards -> Install

Install [STM32CubeProgrammer](https://www.st.com/en/development-tools/stm32cubeprog.html)

Connect Nucleo board and select Nucleo32 and L412KB (or Nucleo L432KC) if it gives you the option

Tools->Board Part Number->Nucleo L412KB (or Nucleo L432KC)
Tools->Upload Method->STM32CubeProgrammer (SWD) [Preffered not required]
Tools->U(S)ART Support->Enabled (generic "Serial")
