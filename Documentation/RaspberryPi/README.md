# Raspberry Pi Documentation

Table of Contents

- [Setup](#setup)
- [Install RaspAP](#install-raspap)
- [Source Files](#source-files)
- [RFM95 Wiring](#rfm95-wiring)

# Setup

1. Use the RaspberryPi Imager to load the OS onto the microSD card if not done already.
   - Choose the lightweight images as the raspberry pi 2 is not as powerful as the newer ones.
   - !!! Enable SSH !!!
1. Connect Keyboard, Mouse, and Display to the Raspberry Pi
1. Connect to the wifi network (or directly connect via ethernet to your pc)
1. SSH into the raspberry pi from your pc

> Or just use the raspberry pi via peripherals

## Install RaspAP

Follow instructions [here](https://raspap.com/#quick) to install raspAP. From there, setup a hotspot so that you can access (SSH into) the raspberry pi at remote locations by simply connecting to the AP hosted by the raspberry pi.

## Source Files

- Clone the [github](https://github.com/eiharun/SP25-20.git) or unzip given the source files to your specified location. (Preferably `/home/{user}/`)
- If you choose another location besides `/home/{user}/`, you must update launchgui.sh and launchtui.sh to match the RaspberyPi directory.

You can run launchgui.sh and launchtui.sh to launch the gui and tui respectively.

If you would like a Desktop shortcut to the GUI (useful while 'in the field'), copy [GUI.desktop](/RaspberryPi/GUI.desktop) to the Desktop dir (`/home/{user}/Desktop`)

### GUI

The GUI will be the default entrypoint in communicating with the balloon. It's easy to use and quick to set up making it the ideal option for ground station members.

### TUI

The TUI (Texual User Interface), or the Command Line Interface (CLI), on the other hand requrires a seperate laptop to ssh into the raspberry pi and launch the cli where commands can be typed. This provides more flexibility as well as giving support for custom packets that can be used later on for testing new commands/protocols/etc.

## RFM95 Wiring

| RFM95 Pin | Raspberry Pi Pin |
| --------- | ---------------- |
| Vin       | 3.3V             |
| GND       | GND              |
| SCK       | GPIO 11 (SCLK)   |
| MISO      | GPIO 9 (MISO)    |
| MOSI      | GPIO 10 (MOSI)   |
| CS        | GPIO 20          |
| RST       | GPIO 19          |

![Raspberry Pi 2 Model B pinout](/RaspberryPi/RaspberryPi2Pinout.PNG)

The Cutdown function doesn't do anything currently since we only had access to the motor. Reimplement with your way of cutting down the balloon.
