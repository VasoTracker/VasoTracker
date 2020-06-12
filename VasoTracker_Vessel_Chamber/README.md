VasoTracker Vessel Chamber
======
<img src="https://github.com/VasoTracker/VasoTracker/blob/master/VasoTracker_Vessel_Chamber/Images/vasotracker_rev2_v2.jpg">

THIS IS VERSION 2 OF THE  VASOTRACKER CHAMBER. WE MAY HAVE MORE UPDATES - CHECKOUT THE VASOTRACKER WEBSITE:
http://www.vasotracker.com/downloads/pressure-myograph-hardware/

A cheap but effective vessel chamber for pressure myography. This repository contains the source files required to manufacture the Vessel Chamber.

We provide Creo (.prt), Fusion 360 (.f3d), STEP, and STL files. However, our parts were designed using Creo Parametric 4.0.  You'd be best to get a copy of Creo if you want to make any changes to the .prt files. PTC offer a free student edition: https://www.ptc.com/en/academic-program/products/free-software. However, if you only are happy with the chamber as it is then the .step files are all you need.

## Features

* **Designed for use on upright and inverted microscopes**

* **Precise alignment of cannula via 3-axis manipulators**

* **Magnetic mounts for perfusion plumbing and oxygenation**


## Building the VasoTracker Chamber:

The VasoTracker chamber can be built for less than £1500. The main chamber parts were custom designed and can be machined/3D-printed by in-house workshops or via commercial manufacturing services (e.g. Protolabs). Obviously, if you have access to a mechanical workshop, the system will be much cheaper than the price quoted below.

Here is a table of the custom components required:

  **Custom Imaging Chamber Parts**| **Material** |**Supplier**|**Part #**|**Qty**|**£/unit**|**Total (£)**
  :-----:|:-----:|:-----:|:-----:|:-----:|:-----:|:-----:
  ||||||
  Chamber base | POM-C/Delrin | Workshop / Protolabs | - | 1 |178.62|178.62
  Chamber insert | POM-C/Delrin ** | Workshop / Protolabs | - | 1 |95.48|95.48
  Leur connector blocks | POM-C/Delrin | Workshop / Protolabs | - | 2 |136.52|273.04
  Cannula fixture A | PETG/PLA | 3D Print | - | 2 | - | -
  Cannula fixture B | PETG/PLA | 3D Print | - | 2 | - | -
  Cannula Lateral Bottom | PETG/PLA | 3D Print | - | 2 | - | -
  Cannula Lateral Top | PETG/PLA | 3D Print | - | 2 | - | -
  Magnetic plumbing holders | SS or Delrin ** | Workshop / Protolabs | - | 2 | - | -
   ||||||
   | | | | |**Subtotal**|**442.54**

* Prices correct June 2020. Obviously they aresubject to change.



Here are the other required components:

| Parts                                          | Supplier                | Part #      | Qty | £/unit   | Total (£) |
|------------------------------------------------|-------------------------|-------------|-----|----------|-----------|
|                                                |                         |             |     |          |           |
| Imaging Chamber                                |                         |             |     |          |           |
| 25mm diameter cover glass (100   pieces)       | Scientific Lab Supplies | MIC3320     | 1   | 18.66    | 18.66     |
| M3 thumb screws (Come in a   pack of 10)       | RS                      | 664-4637    | 1   | 4.7      | 4.7       |
|                                                |                         |             |     |          |           |
| Perfusion attachments                          |                         |             |     |          |           |
| Neodynium disc magnets (In a   pack of 10)     | RS                      | 792-4559    | 4   | 4.15     | 16.6      |
| Magnetic Clamp for suction   tubes             | Warner Instruments      | MAG-2       | 4   | 45.00    | 180.00    |
|                                                |                         |             |     |          |           |
| Cannula holders                                |                         |             |     |          |           |
| 3-axis translation stage                       | Thorlabs                | DT12XYZ/M   | 2   | 231.80   | 463.60    |
| Screw thread adapter                           | Thorlabs                | AP4M3M      | 4   | 1.48     | 5.92      |
| 13 mm metal rod                                | Thorlabs                | MS05R/M     | 2   | 4.51     | 9.02      |
| 38 mm metal rod                                | Thorlabs                | MS1.5R/M    | 2   | 4.93     | 9.86      |
| 75 mm metal rod                                | Thorlabs                | MS3R/M      | 2   | 5.97     | 11.94     |
| 90 degree rod clamp                            | Thorlabs                | MSRA90      | 2   | 12.62    | 25.24     |
| 90 degree rod clamp                            | Thorlabs                | ER90B/M     | 2   | 10.71    | 21.42     |
| Cannula holder                                 | Siskiyou                | MSC-1 M     | 2   | 21.00    | 42.00     |
| 1.5 mm OD glass capillary   glass (225 pieces) | Harvard Apparatus       | 300058      |     |          |           |
|                                                |                         |             |     |          |           |
| Tubing & Connectors                            |                         |             |     |          |           |
| Female luer  (threaded 1/16" barb; pack of 25) | Cole-Palmer             | GY-45502-30 | 1   | 8.53     | 8.53      |
| Masterflex 1.22 ID tubing (100   ft roll)      | Cole-Palmer             | WZ-06460-31 | 1   | 96       | 96        |
| Female luer (1/16" barb;   pack of 25)         | Cole-Palmer             | GY-45502-00 | 1   | 6.36     | 6.36      |
| Male luer (1/16" barb;   pack of 25)           | Cole-Palmer             | GY-45505-00 | 1   | 6.46     | 6.46      |
| Luer stopcock (pack of 10)                     | Cole-Palmer             | WZ-30600-02 | 1   | 16.94    | 16.94     |
|                                                |                         |             |     |          |           |
|                                                |                         |             |     | Subtotal | 943.25    |

 To build the VasoTracker chamber, all that is required it to connect the components together:

 1.	Seal the bottom of the chamber insert by securing a 25mm coverslip to the through-hole using superglue or vacuum grease.
 2.	Place the chamber insert in the chamber base and secure using 2 of the M3 thumb screws.
 3.	Secure the tubing anchors to the chamber base using M3 screws.
 4.	Secure 10 mm diameter magnets into the holes on the chamber base using superglue. You may want to ensure that the polarity of all of the magnets is the same.
 5.	Secure the mounts for the 3-axis positioning stages to the base using the included M6 screws. Then mount the 3-axis positioning stages.
 6. Screw each of the cannula holders onto a 38 mm rod and couple to the 3-axis manipulators as shown below:
 7.	Mount glass cannula (pulled with pipette puller) onto cannula holder.
 8. Screw a threaded female luer (1/16" barb) into each of the tubing holders.
 9. Connected cannula to luer connector via tubing.
 10. Connect luer stopcock to each of the leur connectors to enable 3-way control of input and output.
 11. The chamber is now ready to be filled with physiological saline solution and have an artery mounted between the two cannula!

 <img src="https://github.com/kaelome/VasoTracker/blob/master/VasoTracker_Vessel_Chamber/Images/vasotracker_assembly.gif">
