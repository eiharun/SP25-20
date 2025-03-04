# STM32 Wiring Diagram

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
| RST    | D4    |
| G1     | NC    |
| G2     | NC    |
| G3     | NC    |
| G4     | NC    |
| G5     | NC    |

To program:

Follow instructions [here](https://github.com/stm32duino/Arduino_Core_STM32)

Boards Manager -> STM32 MCU based boards -> Install

Install [STM32CubeProgrammer](https://www.st.com/en/development-tools/stm32cubeprog.html)

Connect Nucleo board and select Nucleo32 and L412KB (or Nucleo L432KC) if it gives you the option

Tools->Board Part Number->Nucleo L412KB (or Nucleo L432KC)
Tools->Upload Method->STM32CubeProgrammer (SWD) [Preffered not required]
Tools->U(S)ART Support->Enabled (generic "Serial")
