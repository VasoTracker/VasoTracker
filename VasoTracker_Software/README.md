VasoTracker diameter tracking software
======
<img src="https://github.com/VasoTracker/VasoTracker/blob/master/VasoTracker_Software/Resources/Screenshot.gif" width="800" align="center">

VasoTracker/VasoTracker_Software/Resources/Screenshot.gif

Software for automatic diameter tracking in pressure myography experiments.

Written in [Python 2.7](https://www.python.org/ "Python 2.7"), and making use of [μManager](https://micro-manager.org/) camera control libraries

## Features

* **Acquires diameter measurements from pressurised blood vessels**

* **Live graphing of both outer and inner blood vessel diameter**

* **Diameter indicators overlaid on live image feed**

* **Synchronised data collection records and displays diameter, pressure, and temperature readings**

* **Record diameter measurements from up to 50 scan lines (you can examine propagated dilations)**

* **Line averaging: each scan line is integrated over 25 pixel lines to minimise errors introduced by contrast variances, the average diameter at each scanline is calculated and plotted**

* **Limit diameter tracking to a region of interest**

* **Filter of diameter measurements to exclude outlier data points**

* **Record and save image data throughout the experiment: VasoTracker outputs raw .tiff files, and .tiff files with diameter indicators overlaid**

* **All data is conveniently and automatically exported to .csv format**

* **Use with your own hardware! So long as your camera works with [μManager](https://micro-manager.org/), it can work with VasoTracker**


## Installing the VasoTracker Software:

A handy single-file installer and instructions for using the VasoTracker software is available to download at our [VasoTracker](http://www.vasotracker.com/downloads/) website.
