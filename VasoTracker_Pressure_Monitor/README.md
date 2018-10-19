VasoTracker Pressure Monitor
======
<img src="https://github.com/kaelome/VasoTracker/blob/master/Splash.gif" width="400" align="right">

An Arduino-based pressure monitor for the VasoTracker myograph system.

## Features

* **Reads and displays pressure sensed by two in-line pressure transducers**

* **Writes data to serial port for acquisition and display by the VasoTracker GUI**

## Building the VasoTracker Pressure Monitor:

The VasoTracker pressure monitor (with two inline pressure transducers) can be built for under £120. Here is a table of the components required:

**Parts**|**Supplier**|**Part #**|**Qty**|**£/unit**|**Total (£)**
:-----:|:-----:|:-----:|:-----:|:-----:|:-----:
Arduino Uno|Arduino|A000066 |1|20.7|20.7
Wheatstone Amplifier Shield|RobotShop|RB-Onl-38|1|15.11|15.11
LCD Shield|iTead Studio|1602 LCD|1|3.98|3.98
Flow through pressure transducers|Honeywell|26PCDFG5G|2|36.72|73.44
12" 4-Pin Jumper Wire|Sparkfun Electronics|PRT-10374|2|1.48|2.96
Arduino R3 Stackable Headers|Sparkfun Electronics|PRT-10007|1|1.14|1.14
LEGO™ Encolsure|LEGO|-|-|-|-
 | | | | |Subtotal|117.33


To build the temperature controller, all that is required it to connect the components together:

1.	Stack 2-channel Wheatstone Amplifier Shield on top of the Arduino Uno (see Figure 1A-B below)
2.	Connect the two pressure transducers to the amplifier shield using the 12” jumper wires. Ensure the pins are connected in the correct order (see Figure 1B-D below).
3.	Place stackable headers on top of the Wheatstone Amplifier Shield (these are required to allow clearance for the pressure transducer connections and bend the A0 pin1 on the stackable header so that it does not connect to the Arduino Uno board (see Figure 1E below).
4.	Stack the LCD Shield on top of the stackable headers (see Figure 1F below).
5.	Use a female 1-pin jumper cable to connect the disconnected pin on the stackable header to the A5 pin on top of the LCD shield.
6.	 Wrap one end of a wire around the Arduino reset pin and another around Vin (5V)2.
7.	 Stack the LCD shield on top of the Arduino.
8.	 Connect a power supply to the ARDUINO device to switch the unit on (see Figure 1G below). To do this either connect the device to a USB port/wall plug using the USB cable that is included with the Arduino, or use an external power supply.
9.	 Optionally, the device may be placed in an enclosure. We chose to build one from Lego® blocks because of their versatility (see Figure 1H below).


<img src=https://github.com/kaelome/VasoTracker/blob/master/VasoTracker_Pressure_Monitor/Images/Pressure%20Monitor%20Construction.gif>

**Figure 1 – Step-by-step guide to constructing the pressure monitor.**
A) Arduino Uno board. B) Wheatstone Amplifier Shield stacked on top of Arduino board. The pin layout of the connectors on the amplifier shield are shown.  C) Front view of 4-pin, flow-through pressure transducer D) Reverse view of pressure transducer with pin layout shown. .E) Stackable header pins, used to provide clearance for the cables. The pin connecting to A0 is bent to allow a connection to be rerouted. A jumper cable is used to connect the reset pin on the Arduino to the 5V Vin pin (to prevent the Arduino resetting). F) The LCD shield is stacked on top of the header pins, and the bent AO header pin is routed to A5 on the LCD shield using a female jumper wire. G) The complete device powered on. H) The device may be placed in an enclosure. Because of its versatility, we chose to make one using Lego Bricks.

**Notes:**
1. For measurement of pressures above 140 mmHg, the gain resistors on the Amplifier Shield need changed. See the documentation here:
https://www.robotshop.com/media/files/zip2/strain_gage_load_cells_shield_documentation_v1.2.zip
2. The LCD shield uses the A0 pin for buttons. However, the Wheatstone amplifier shield uses A0 and A1 for the Wheatstone bride inputs. By bending the A0 pin on the stackable header and connecting it to A5 on the LCD shield, we are rerouting A0 on the LCD shield to A5. This is coded into the Arduino in “strain_gauge_shield_and_lcd_support_functions.h”.
3. Should prevent accidental resetting of the Arduino (which would be annoying if it occurred during an experiment)... connect reset pin to 5V via 120 ohm resistor



## Programming the VasoTracker Pressure Monitor

   * Download VasoTracker as a zip file and extract all files (if you don't have it already) from here: https://github.com/kaelome/VasoTracker
   * Download and install the Aruino IDE: <https://www.arduino.cc/en/Guide/Windows#toc1>
   * Download and install the RobotShop WheatstoneBridge library <https://www.arduino.cc/en/Guide/Windows#toc1>
      * 1 -	Download the zip file from here: https://github.com/RobotShop/Wheatstone-Bridge-Amplifier-Shield/archive/master.zip
      * 2 -	In Arduino IDE:
        * Sketch -> Include Library -> Add .ZIP library... then locate the zip file.
   * Copy strain_gauge_shield_and_lcd_arduino_uno_code.ino and strain_gauge_shield_and_lcd__support_functions.cpp from
   **Wheatstone-Bridge-Amplifier-Shield-master\Examples\strain_gauge_shield_and_lcd_arduino_uno_code** to **VasoTracker\VasoTracker_Pressure_Monitor\VasoTracker_Pressure_Monitor_Code**
   * Open VasoTracker/VasoTracker_Pressure_Monitor/VasoTracker_Pressure_Monitor_Code/VasoTracker_Pressure_Monitor_Code.ino in Arduino IDE
   *	Upload code to the Arduino by clicking the upload button: <img src="https://github.com/kaelome/VasoTracker/blob/master/VasoTracker_Pressure_Monitor/Images/Arduino%20Upload%20Button.png" width="400" align="center">




### Setting up the pressure monitor

  Each time VasoTracker Pressure Monitor is to be used, it needs to be calibrated.

  To calibrate the pressure monitor:



# Acknowledgements

Special thanks to Sébastien Parent-Charette and RobotShop who generously provide the Wheatstone bridge library and support function that we make use of.
