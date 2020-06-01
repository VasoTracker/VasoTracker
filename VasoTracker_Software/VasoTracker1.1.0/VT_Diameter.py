##################################################
## VasoTracker Pressure Myograph Software
## 
## This software provides diameter measurements (inner and outer) of pressurised blood vessels
## Designed to work with Thorlabs DCC1545M
## For additional info see www.vasostracker.com and https://github.com/VasoTracker/VasoTracker
## 
##################################################
## 
## BSD 3-Clause License
## 
## Copyright (c) 2018, VasoTracker
## All rights reserved.
## 
## Redistribution and use in source and binary forms, with or without
## modification, are permitted provided that the following conditions are met:
## 
## ## * Redistributions of source code must retain the above copyright notice, this
##   list of conditions and the following disclaimer.
## 
## * Redistributions in binary form must reproduce the above copyright notice,
##   this list of conditions and the following disclaimer in the documentation
##   and/or other materials provided with the distribution.
## 
## * Neither the name of the copyright holder nor the names of its
##   contributors may be used to endorse or promote products derived from
##   this software without specific prior written permission.
## 
## THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
## AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
## IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
## DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
## FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
## DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
## SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
## CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
## OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
## OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
## 
##################################################
## 
## Author: Penelope F Lawton, Matthew D Lee, and Calum Wilson
## Copyright: Copyright 2018, VasoTracker
## Credits: Penelope F Lawton, Matthew D Lee, and Calum Wilson
## License: BSD 3-Clause License
## Version: 1.1.0
## Maintainer: Calum Wilson
## Email: vasotracker@gmail.com
## Status: Production
## Last updated: 20191117
## 
##################################################

## We found the following to be useful:
## https://www.safaribooksonline.com/library/view/python-cookbook/0596001673/ch09s07.html
## http://code.activestate.com/recipes/82965-threads-tkinter-and-asynchronous-io/
## https://www.physics.utoronto.ca/~phy326/python/Live_Plot.py
## http://forum.arduino.cc/index.php?topic=225329.msg1810764#msg1810764
## https://stackoverflow.com/questions/9917280/using-draw-in-pil-tkinter
## https://stackoverflow.com/questions/37334106/opening-image-on-canvas-cropping-the-image-and-update-the-canvas

from __future__ import division
import numpy as np
# Tkinter imports
import Tkinter as tk
from Tkinter import *
import tkSimpleDialog
import tkMessageBox as tmb
import tkFileDialog
import ttk
from PIL import Image, ImageTk #convert cv2 image to tkinter
E = tk.E
W = tk.W
N = tk.N
S = tk.S
ypadding = 1.5 #ypadding just to save time - used for both x and y

# Other imports
import os
import sys
import time
import datetime
import threading
import random
import Queue

import cv2
import csv
from skimage import io
import skimage
from skimage import measure
import serial
import win32com.client
import webbrowser

# Add MicroManager to path
import sys
MM_PATH = os.path.join('C:', os.path.sep, 'Program Files','Micro-Manager-1.4')
sys.path.append(MM_PATH)
os.environ['PATH'] = MM_PATH + ';' + os.environ['PATH']
import MMCorePy
'''
import sys
sys.path.append('C:\Program Files\Micro-Manager-1.4')
import MMCorePy
'''
#import PyQt5
# matplotlib imports
import matplotlib
#matplotlib.use('Qt5Agg') 
#matplotlib.use('Qt4Agg', warn=True)
import matplotlib.backends.tkagg as tkagg
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
import matplotlib.pyplot as plt
from matplotlib.backends import backend_qt4agg
from matplotlib import pyplot

# Import Vasotracker functions
import VTutils


class Calculate_Diameter(object):

    def __init__(self,image,num_lines, multiplication_factor, smooth_factor, thresh_factor, integration_factor, ROI, ID_mode_selection):
        image = image
        #self.timeit2 = TimeIt2()
        self.num_lines = num_lines
        self.multiplication_factor = multiplication_factor
        self.smooth_factor = smooth_factor
        self.thresh_factor = thresh_factor
        self.integration_factor = integration_factor
        self.ROI = ROI
        self.ID_mode_selection = ID_mode_selection
        self.OD = None
        self.ID = None
        #print "working out the diameter"
        
    def calc(self,image, delta_height, delta_width, scale_factor):
    # Set up some parameters
        ny,nx = image.shape

        start_x, start_y = self.ROI[0]
        end_x, end_y = self.ROI[1]

        ID_mode = self.ID_mode_selection.get()

        #print "END"
        #print end_x,end_y
        #print nx,ny
        
        # Number of lines of pixels to average for each scanline
        navg = self.integration_factor

        if end_x == nx and end_y == ny:
            start = int(np.floor(ny/(self.num_lines+1)))
            diff = int(np.floor(ny/(self.num_lines+1)))
            end = (self.num_lines+1)*diff
            thresh = 0
        else:
            start_y = int((start_y - delta_height)/scale_factor)
            end_y = int((end_y - delta_height)/scale_factor)
            ny = end_y - start_y
            diff = int(np.floor(ny/(self.num_lines+1)))
            start = start_y + diff
            end = int(start_y + (self.num_lines+1)*diff)
            thresh = 0

            start_x = int((start_x - delta_width)/scale_factor)
            end_x = int((end_x - delta_width)/scale_factor)


    # The multiplication factor
        scale = self.multiplication_factor
    # Slice the image
        data = [np.average(image[y-int(navg/2):y+int(navg/2),:], axis=0) for y in  range(start,end,diff)]#[:,start_x:end_x] #[:,start_x:end_x]  to limit to ROI in x
        data2 = np.array(data)
        data2 = data2[:,int(start_x):int(end_x)]
    #Smooth the datums
        window = np.ones(self.smooth_factor,'d')
        smoothed = [np.convolve(window / window.sum(), sig, mode = 'same') for sig in data2]
    #Differentiate the datums. There are other methods in VTutils...
    # But this one is much faster!
        ddts = [VTutils.diff2(sig, 1) for sig in smoothed] # Was 1 \\\\\ ULTRASOUND
        window = np.ones(self.smooth_factor,'d') # THIS WAS 11 \\\\\ ULTRASOUND 21
        ddts = [np.convolve(window / window.sum(), sig, mode = 'same') for sig in ddts]
    # Loop through each derivative 
        outer_diameters1,outer_diameters2,inner_diameters1,inner_diameters2,self.OD,self.ID, ODS_flag,IDS_flag,ODlist, IDlist = VTutils.process_ddts(ddts,self.thresh_factor,thresh,nx,scale, start_x, ID_mode) # \\\\\ ULTRASOUND  # VTutils.process_ddts_US(ddts,thresh,nx,scale,start_x)
    #Return the data
        return(outer_diameters1,outer_diameters2,inner_diameters1,inner_diameters2,start,diff,ODS_flag,IDS_flag,ODlist, IDlist)

