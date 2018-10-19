VasoTracker Vessel Chamber
======
<img src="https://github.com/kaelome/VasoTracker/blob/master/VasoTracker_Vessel_Chamber/Images/MANN7249.JPG">

A cheap but effective vessel chamber for pressure myography. This repository contains the source files required to manufacture the Vessel Chamber.

These contents of this repository were designed using Creo Parametric 4.0. You'll need a copy of Creo if you want to make any changes to the .prt files. PTC offer a free student edition: https://www.ptc.com/en/academic-program/products/free-software. However, if you only are happy with the chamber as it is then the .step files are all you need.

## Features

* **Designed for use on upright and inverted microscopes**

* **Precise alignment of cannula via 3-axis manipulators**

* **Compatible with Built-in heating system:** (https://github.com/kaelome/VasoTracker/tree/master/VasoTracker_Temperature_Controller)

* **Magnetic mounts for perfusion plumbing and oxygenation**


## Building the VasoTracker Pressure Monitor:

The VasoTracker pressure monitor (with two inline pressure transducers) can be built for ~ £1500. Many of the components may be readily available in research laboratories and the main chamber is a custom design that can be machined from PMMA/aluminium. Should you have access the components or a mechanical workshop, then the system will be much cheaper. Here is a table of the components required:

**Parts**| |**Supplier**|**Part #**|**Qty**|**£/unit**|**Total (£)**
:-----:|:-----:|:-----:|:-----:|:-----:|:-----:|:-----:
**Imaging Chamber** |Chamber base|Protolabs|-|1|174.39|174.39
 |Chamber insert|Protolabs|-|1|144.21|144.21
 |Tubing anchors|Protolabs|-|2|123.94|247.88
 |3-axis translation stage|Thorlabs|DT12XYZ/M|2|231.80|463.60
 |Screw thread adapter|Thorlabs|AP4M3M|4|1.48|5.92
 |13 mm metal rod|Thorlabs|MS05R/M|2|4.51|9.02
 |38 mm metal rod|Thorlabs|MS1.5R/M|2|4.93|9.86
 |75 mm metal rod|Thorlabs|MS3R/M|2|5.97|11.94
 |90 degree rod clamp|Thorlabs|MSRA90|2|12.62|25.24
 |90 degree rod clamp|Thorlabs|ER90B/M|2|10.71|21.42
 |Cannula holder|Siskiyou|MSC-1 M|2|21.00|42.00
 |Neodynium disc magnets (In a pack of 10)|RS|792-4559|4|4.15|16.6
 |Magnetic Clamp for suction tubes|Warner Instruments|MAG-2|4|45.00|180.00
 |25mm diameter cover glass (100 pieces)|Scientific Lab Supplies|MIC3320|1|18.66|18.66
**Tubing & Connectors** |Female luer  (threaded 1/16" barb; pack of 25)|Cole-Palmer|GY-45502-30|1|8.53|8.53
 |M3 thumb screws (Come in a pack of 10)|RS|664-4637|1|4.7|4.7
 |Masterflex 1.22 ID tubing (100 ft roll)|Cole-Palmer|WZ-06460-31|1|96|96
 |Female luer (1/16" barb; pack of 25)|Cole-Palmer|GY-45502-00|1|6.36|6.36
 |Male luer (1/16" barb; pack of 25)|Cole-Palmer|GY-45505-00|1|6.46|6.46
 |Luer stopcock (pack of 10)|Cole-Palmer|WZ-30600-02|1|16.94|16.94
 |1.5 mm OD glass capillary glass (225 pieces)|Harvard Apparatus|300058| | |
 | | | | |**Subtotal**|**1509.73**

 To build the temperature controller, all that is required it to connect the components together:

 1.	Seal the bottom of the chamber insert by securing a 25mm coverslip to the through-hole using superglue or vacuum grease.
 2.	Place the chamber insert in the chamber base and secure using 2 of the M3 thumb screws.
 3.	Secure the tubing anchors to the chamber base using M3 screws.
 4.	Secure 10 mm diameter magnets into the holes on the chamber base using superglue. You may want to ensure that the polarity of all of the magnets is the same.
 5.	Secure the mounts for the 3-axis positioning stages to the base using the included M6 screws. Then mount the 3-axis positioning stages.
 6. Screw each of the cannula holders onto a 38 mm rod and couple to the 3-axis manipulators as shown here:

 <img src="https://github.com/kaelome/VasoTracker/blob/master/VasoTracker_Vessel_Chamber/Images/vasotracker_assembly.gif">

 7.	Mount glass cannula (pulled with pipette puller) onto cannula holder.
 8. Screw a threaded female luer (1/16" barb) into each of the tubing holders.
 9. Connected cannula to luer connector via tubing.
 10. Connect luer stopcock to each of the leur connectors to enable 3-way control of input and output.
 11. The chamber is now ready to be filled with physiological saline solution and have an artery mounted between the two cannula!
