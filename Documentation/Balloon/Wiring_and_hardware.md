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

| Status LED  | 3k Resistor | STM32 |
| ----------- | ----------- | ----- |
| Cathode (-) | NC          | GND   |
| Anode (+)   | Pin 1       | NC    |
| NC          | Pin 2       | A5    |

| Servo | STM32 |
| ----- | ----- |
| PWM   | D9    |
| Vin   | 3v3   |
| GND   | GND   |

| GPS | STM32 |
| --- | ----- |
| TX  | D4    |
| RX  | D5    |
| VCC | 3v3   |
| GND | GND   |
| PPS | NC    |

| SD         | STM32 |
| ---------- | ----- |
| VDD        | 3v3   |
| GND        | GND   |
| DI         | D12   |
| DO         | D11   |
| SCLK       | D13   |
| CS         | D6    |
| Other Pins | NC    |

Optional (With LED macro defined)

| RX_LED LED  | 3k Resistor | STM32 |
| ----------- | ----------- | ----- |
| Cathode (-) | NC          | GND   |
| Anode (+)   | Pin 1       | NC    |
| NC          | Pin 2       | A6    |
