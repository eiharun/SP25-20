# Balloon Venting System

Table of Contents

1. [Set-up for Programming and Uploading Code](#programming-and-uploading-code)
2. [Balloon Code](#balloon-code)

## Programming and Uploading Code

> The balloon venting system uses an STM32 microcontroller and can be programmed using the Arduino IDE. Therefore, there are steps that need to be taken to set up the IDE with the STM32 MCU.

1. Install the [Arduino IDE 2](https://www.arduino.cc/en/software) (v2 is Required)
2. Install the [STM32 board package](https://github.com/stm32duino/Arduino_Core_STM32/wiki/Getting-Started):

   - Open the Arduino IDE
   - Go to File > Preferences
   - In the "Additional Board Manager URLs" field, add the following URL:
     - <https://github.com/stm32duino/BoardManagerFiles/raw/main/package_stmicroelectronics_index.json>
   - Click on "Tools" menu and then "Boards > Boards Manager"
   - Select "Contributed" and type stm and "STM32 MCU based boards" will show up. Install the latest version

     ![STM32BoardManager](ScreenShots/26-04-33.png)

3. Install the [STM32CubeProgrammer](https://www.st.com/en/development-tools/stm32cubeprog.html) in order to upload the code to the stm32 more effectively. (HIGHLY RECCOMENDED)

Now the STM32 can be programmed using the Arduino IDE, however there are things to consider when uploading code.

Under "Tools", make sure:

- **Board:** "Nucleo-32"
- **Board part number:** "Nucleo L412KB" or "Nucleo L412KC" depending on which is currently being used.
- **C Runtime Library:** "Newlib Nano + Float Printf"
  - If "float printf" is not enabled, logging will not log data values as expected. However this can be left default if logging is disabled in [Balloon.ino](/BalloonCode/ArduinoIDE_Sketches/Balloon/Balloon.ino)
- **Upload method:** "STM32CubeProgrammer (SWD)" - Requires STM32CubeProgrammer to be installed
  - This option yielded the best results when uploading, "Mass Storage" seemed to have issues. Feel free to experiment with different methods. One thing to note, there seems to be an issue with programming a device when multiple stm boards are connected. So for now, only connect the board you are programming when the code is uploading to the board.

<img src="ScreenShots/26-03-29.png" width="500">

## Balloon Code

> "Servo.h" may cause some problems after installing STM32duino board manager. The best workaround is to change the Servo folder and Servo.h file name in the arduino library to something different "e.g. Servo_ardu.h"
