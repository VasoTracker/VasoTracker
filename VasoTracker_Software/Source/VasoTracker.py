##################################################
## VasoTracker Pressure Myograph Software
## 
## This software provides diameter measurements (inner and outer) of pressurised blood vessels
## Designed to work with Thorlabs DCC1545M
## For additional info see www.vasostracker.com and https://github.com/kaelome/VasoTracker
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
## Version: 1.0.2
## Maintainer: Calum Wilson
## Email: vasotracker@gmail.com
## Status: Production
## Last updated: 20181221
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
import numpy as np
import cv2
import csv
from skimage import io
import skimage
from skimage import measure
import serial
import win32com.client
import webbrowser

# Import Vasotracker functions
import VTutils

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


class GuiPart(tk.Frame):

    #Initialisation function
    def __init__(self, master, queue, endCommand, *args, **kwargs):
        tk.Frame.__init__(self, *args, **kwargs)
        self.queue = queue
        self.endApplication = endCommand

    #Set up the GUI
        self.grid(sticky=N+S+E+W)
        top = self.winfo_toplevel()
        top.rowconfigure(0, weight=1)
        top.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self.columnconfigure(0, weight=1)
        self.filename = self.get_file_name()
        print self.filename        
        self.Arduino = Arduino(self)
        self.ports = self.Arduino.getports()
        self.timeit = TimeIt()
        self.timeit2 = TimeIt2()
        self.OD = None

    # Scale setting
        global multiplication_factor
        multiplication_factor = 1
        self.multiplication_factor = multiplication_factor

    # Exposure setting
        global exposure
        exposure = 500
        self.exposure = exposure

    # Acquisition rate setting
        global acq_rate
        acq_rate = 0
        self.acq_rate = acq_rate

    # Record interval setting
        global rec_interval
        rec_interval = 1
        self.rec_interval = rec_interval

    # Data acquisition lines setting
        global number
        num_lines = 20
        self.num_lines = num_lines

        self.initUI(endCommand)

    # Open the csv file and then clear it
        f = open(self.filename.name, "w+")
        f.close()

    # Add the headers
        with open((self.filename.name), 'ab') as f:
            w=csv.writer(f, quoting=csv.QUOTE_ALL)
            w.writerow(("Time","Outer Diameter", "Inner Diameter", 'Temperature (oC)', 'Pressure 1 (mmHg)', 'Pressure 2 (mmHg)', 'Avg Pressure (mmHg)'))

    # Add the file for the outerdiameter profiles
        self.txt_file = os.path.splitext(self.filename.name)[0]
        print "tail = ", self.txt_file
        self.profile_file = self.txt_file + ' - ODProfiles' + '.csv'
        with open((self.profile_file), 'w+') as g:
            v=csv.writer(g, quoting=csv.QUOTE_ALL)
            column_headings = 'Time (s)', 'Profile 1', 'Profile 2', "Profile 3", "..."
            v.writerow(column_headings)

    # Add the file for the innerdiameter profiles
        self.profile_file2 = self.txt_file + ' - IDProfiles' + '.csv'
        with open((self.profile_file2), 'w+') as g:
            v=csv.writer(g, quoting=csv.QUOTE_ALL)
            column_headings = 'Time (s)', 'Profile 1', 'Profile 2', "Profile 3", "..."
            v.writerow(column_headings)

    # Add file for table
        self.txt_file = self.txt_file + ' - Table' + '.csv'
        g = open(self.txt_file, "w+")
        g.close()
        with open((self.txt_file), 'ab') as g:
                v=csv.writer(g, quoting=csv.QUOTE_ALL)
                column_headings = 'Time (s)', 'Label', 'Diameter', "P1", "P2", "max_percent"
                v.writerow(column_headings)

    # Function for getting the save file.
    def get_file_name(self):
        tmb.showinfo("", "Create a file to save output...")
        now = datetime.datetime.now()
        savename = now.strftime("%Y%m%d")
        f = tkFileDialog.asksaveasfile(mode='w', defaultextension=".csv", initialdir="Results\\", initialfile=savename)
        if f:
            print "f = ", f
            return(f)            
        else: # asksaveasfile return `None` if dialog closed with "cancel".
            if tmb.askquestion("No save file selected", "Do you want to quit VasoTracker?", icon='warning') == "yes":
                self.endApplication()
            else:
                f = self.get_file_name()
                return (f)

    # Function for writing to the save file
    def writeToFile(self,data):
        with open((self.filename.name), 'ab') as f:
            w=csv.writer(f, quoting=csv.QUOTE_ALL)
            w.writerow(data)

    # Function for writing to the save file
    def writeToFile2(self,data):
        with open((self.profile_file), 'ab') as f:
            w=csv.writer(f, quoting=csv.QUOTE_ALL)
            w.writerow(data)

    # Function for writing to the save file
    def writeToFile3(self,data):
        with open((self.profile_file2), 'ab') as f:
            w=csv.writer(f, quoting=csv.QUOTE_ALL)
            w.writerow(data)

    # Function for closing down
    def close_app(self):
        if tmb.askokcancel("Close", "Are you sure...?"):
            self.endApplication()

    # Function for defining an average checkbox ## Shouldbe in toolbar!
    def average_checkbox(self, window, text):
        avg_checkbox = ttk.Checkbutton(window, text=text)
        avg_checkbox.grid(row=0, columnspan=4, padx=3, pady=3)

    # Second Function for initialising the GUI
    def initUI(self,endCommand):

    # make Esc exit the program
        root.bind('<Escape>', lambda e: endCommand)

    # make the top right close button minimize (iconify) the main window
        root.protocol("WM_DELETE_WINDOW", self.close_app)

    # create a menu bar with an Exit command
        menubar = tk.Menu(root)
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="Exit", command=self.close_app)
        menubar.add_cascade(label="File", menu=filemenu)
        root.config(menu=menubar)
        self.pack(fill=BOTH, expand=1)

    # Make the toolbar along the top
        self.toolbar = ToolBar(self)#ttk.Frame(root, height=150)
        self.toolbar.grid(row=0, column=0,rowspan=1,columnspan=4, padx=ypadding, pady=ypadding, sticky=E+S+W+N)
        self.toolbar.grid(sticky='nswe')
        self.toolbar.rowconfigure(0, weight=1)
        self.toolbar.columnconfigure(0, weight=1)
        #self.toolbar.grid_propagate(0)

    # Make the status bar along the bottom
        def callback(event):
            webbrowser.open_new(r"http://www.vasotracker.com")
        self.status_bar = ttk.Label(text = 'Thank you for using VasoTracker. To support us, please cite VasoTracker (click here for the paper).', relief=SUNKEN, anchor='w')
        
        self.status_bar.pack(side=BOTTOM, fill=X)
        self.status_bar.bind("<Button-1>", callback)

    # Make the graph frame
        self.graphframe = GraphFrame(self)
        self.graphframe.grid(row=1, column=0, rowspan=4,columnspan=2, padx=ypadding, pady=ypadding, sticky=E+S+W+N)
        self.graphframe.grid(sticky='nswe')
        print "this is the height: ", self.graphframe.winfo_height()
        #self.graphframe.rowconfigure(0, weight=1)
        #self.graphframe.columnconfigure(0, weight=1)
        #self.graphframe.grid_propagate(0)
 
    # Make the table frame
        self.tableframe = TableFrame(self)
        self.tableframe.grid(row=1, column=3,rowspan=1,columnspan=1, padx=ypadding, pady=ypadding, sticky=E+S+W+N)
        self.tableframe.grid(sticky='nwe')
        #self.tableframe.rowconfigure(0, weight=1)
        #self.tableframe.columnconfigure(0, weight=1)
        #self.tableframe.grid_propagate(0)


    #Update everything so that the frames are all the correct size. We need to do this so we can size the graph/image before we place them.
        self.toolbar.update()
        self.status_bar.update()
        #self.graphframe.update()
        self.tableframe.update()
        self.toolbar.update()


    # Make the Camera Frame bottom right
        self.cameraframe = CameraFrame(self)
        self.cameraframe.grid(row=2, column=3,rowspan=1,columnspan=2, padx=ypadding, pady=ypadding, sticky=E+S+W+N)
        self.cameraframe.grid(sticky='nswe')
        #self.cameraframe.rowconfigure(0, weight=3)
        #self.cameraframe.columnconfigure(0, weight=2)
        #self.cameraframe.grid_propagate(0)

        print "this is the height: ", self.graphframe.winfo_height()
        print "this is the width: ", self.graphframe.winfo_width()
        self.graphframe.mainWidgets() # Now set up the graph

        #if self.toolbar.start_flag:
        #    mmc.startContinuousSequenceAcquisition(500)

    # Count function for reading in with FakeCamera
        self.count = 0   
    # Count function for resizing on first image acquisition
        self.count2 = 0      

    def sortdata(self,temppres):
        #print temppres
        #print "Length of the data = ", len(temppres)
        T = np.nan
        P1 = np.nan
        P2 = np.nan
        for i,data in enumerate(temppres):
            #print "length of data = ", len(data)#val = ser.readline().strip('\n\r').split(';')
            #print "this is what we are looking at",data
            if len(data) > 0:
                val = data[0].strip('\n\r').split(';')
                val = val[:-1]
                val = [el.split(':') for el in val]
                if val[0][0] == "Temperature":
                    temp = float(val[0][1])
                    print "this is a temp = ", temp
                    T = temp
                elif val[0][0] == "Pressure1":
                    pres1 = float(val[0][1])
                    pres2 = float(val[1][1])
                    print "this is a pressure = ", pres1
                    P1,P2 = pres1,pres2

        return P1,P2,T



    # This function will process all of the incoming images
    def processIncoming(self, outers, inners, timelist):
        """Handle all messages currently in the queue, if any."""
        while self.queue.qsize(  ):
            print "Queue size = ", self.queue.qsize(  )
            with self.timeit2("Total"):  # time for optimisation
                try:
                    if self.toolbar.record_flag:
                        if self.count == 0:
                            global start_time
                            start_time=time.time()
                        # This is for loading in a video as an example!
                        try:
                            mmc.setProperty('Focus', "Position", self.count)
                            #print "the count is this:", self.count
                            #print mmc.getProperty('Camera', 'Resolved path')
                        except:
                            pass


                        
                    #Get the image
                        msg = self.queue.get(0)


                    # Process the acquired image
                        timenow = time.time() - start_time #Get the time
                    # Get ROI
                        if self.toolbar.ROI_is_checked.get() == 1: # Get ROI
                            self.ROI = ((self.cameraframe.start_x,self.cameraframe.start_y), (self.cameraframe.end_x, self.cameraframe.end_y))
                        else: # Set ROI to image bounds
                            self.ROI = ((0,0),(int(msg.shape[1]),int(msg.shape[0])) )    
                    # Calculate diameter    
                        self.calculate_diameter = Calculate_Diameter(self,self.num_lines,self.multiplication_factor, self.ROI)
                        global OD
                        global ID, T, P1, P2
                        #with self.timeit("Calculate diameter"): # time for optimisation
                        outer_diameters1,outer_diameters2,inner_diameters1,inner_diameters2,OD,ID,start,diff, ODS_flag,IDS_flag,ODlist,IDlist = self.calculate_diameter.calc(msg, self.num_lines,self.multiplication_factor, self.ROI)

                        params = timenow,outer_diameters1,outer_diameters2,inner_diameters1,inner_diameters2,OD,start,diff,ODS_flag,IDS_flag, self.ROI
                        #with self.timeit("process queue!"): # time for optimisation
                        self.cameraframe.process_queue(params,msg,self.count2)
                        timelist.append(timenow)
                        #print timelist
                        outers.append(OD)
                        inners.append(ID)
                        #with self.timeit("plot the graph"): # time for optimisation
                        self.graphframe.plot(timelist,outers,inners,self.toolbar.xlims, self.toolbar.ylims, self.toolbar.xlims2, self.toolbar.ylims2)    
                        self.count += 1

                        # Get the arduino data
                        temppres = self.Arduino.getData()
                        P1,P2,T = self.sortdata(temppres)
                        self.toolbar.update_temp(T) #### CHANGE to T
                        self.toolbar.update_pressure(P1,P2, (P1+P2)/2)
                        self.toolbar.update_diam(OD,ID)
                        self.toolbar.update_time(timenow)
                        global acqrate
                        self.toolbar.update_acq_rate(acqrate)

                        savedata = timenow,OD,ID, T, P1, P2, (P1+P2)/2
                        savedata2 = [timenow]+ODlist
                        savedata3 = [timenow]+IDlist
                        self.writeToFile(savedata)
                        self.writeToFile2(savedata2)
                        self.writeToFile3(savedata3)

                        #Need to access the outer diameter from the toolbar
                        self.OD = OD
                        

                    else:
                        msg = self.queue.get(0)
                        params = 0,0,0,0,0,0,0,0,0,0,0
                        self.cameraframe.process_queue(params,msg,self.count2)  
                    
                    self.count2 += 1
                    #print self.count
                    return
                except Queue.Empty:
                    # just on general principles, although we don't expect this branch to be taken in this case
                    pass
                return



class setCamera(object):
    def __init__(self,camera_label):
        camera_label = camera_label
        self.DEVICE = None
    
    def set_exp(self,exposure):
        mmc.setExposure(exposure)
        return


    def set(self, camera_label):
        # Set up the camera
        mmc.reset()
        mmc.enableStderrLog(False)
        mmc.enableDebugLog(False)
        mmc.setCircularBufferMemoryFootprint(100)# (in case of memory problems)

        if camera_label == "Thorlabs":
            print "Camera Selected: ", camera_label
            DEVICE = ["ThorCam","ThorlabsUSBCamera","ThorCam"] #camera properties - micromanager creates these in a file
            mmc.loadDevice(*DEVICE)
            mmc.initializeDevice(DEVICE[0])
            mmc.setCameraDevice(DEVICE[0])
            mmc.setProperty(DEVICE[0], 'Binning', 1)
            mmc.setProperty(DEVICE[0], 'HardwareGain', 1)
            mmc.setProperty(DEVICE[0], 'PixelClockMHz', 5)
            mmc.setProperty(DEVICE[0], 'PixelType', '8bit')
            mmc.setExposure(exposure)

        if camera_label == "OpenCV":
            print "Camera Selected: ", camera_label
            mmc.loadSystemConfiguration3('OpenCV.cfg')
            print "loaded the config file."
            print "exposure is: ", exposure
            mmc.setProperty('OpenCVgrabber', 'PixelType', '8bit')
            mmc.setExposure(exposure)


        elif camera_label == "FakeCamera":
            print "Camera Selected: ", camera_label
            DEVICE = ['Camera', 'FakeCamera', 'FakeCamera'] #camera properties - micromanager creates these in a file
            mmc.loadDevice(*DEVICE)
            mmc.initializeDevice(DEVICE[0])
            mmc.setCameraDevice(DEVICE[0])
            print "exposure is: ", exposure
            mmc.setExposure(exposure)
            mmc.setProperty(DEVICE[0], 'PixelType', '8bit')
            mmc.setProperty(DEVICE[0], 'Path mask', 'SampleData\\TEST?{4.0}?.tif') #C:\\00-Code\\00 - VasoTracker\\
            # To load in a sequence 
            DEVICE2 = ['Focus', 'DemoCamera', 'DStage']
            mmc.loadDevice(*DEVICE2)
            mmc.initializeDevice(DEVICE2[0])
            mmc.setFocusDevice(DEVICE2[0])
            mmc.setProperty(DEVICE2[0], "Position", 0)
        elif camera_label == "":
            tmb.showinfo("Warning", "You need to select a camera source!")
            return
        
        # TODO SET BINNING PARAMETER
        '''
        try:
            mmc.setProperty(DEVICE[0], "Binning", "2")
        except:
            pass
        '''



# Class for the main toolbar
class ToolBar(tk.Frame):
    def __init__(self,parent):
        tk.Frame.__init__(self, parent, height = 150)#,  width=250, highlightthickness=2, highlightbackground="#111")
        self.parent = parent
        self.mainWidgets()
        self.set_camera = setCamera(self)
        self.ref_OD = None



    #Functions that do things in the toolbar
    def update_temp(self, temp):
        # Updates the temperature widget
        self.temp_entry.config(state='normal')
        self.temp_entry.delete(0, 'end')
        self.temp_entry.insert(0, '%.2f' % temp)
        self.temp_entry.config(state='DISABLED')

    def update_pressure(self, P1,P2,PAvg):
        # Update average pressure
        self.pressureavg_entry.config(state='normal')
        self.pressureavg_entry.delete(0, 'end')
        self.pressureavg_entry.insert(0, '%.2f' % PAvg)
        self.pressureavg_entry.config(state='DISABLED')

    def update_diam(self, OD, ID):
        # Update outer diameter
        self.outdiam_entry.config(state='normal')
        self.outdiam_entry.delete(0, 'end')
        self.outdiam_entry.insert(0, '%.2f' % OD)
        self.outdiam_entry.config(state='DISABLED')
        # Update outer diameter
        self.indiam_entry.config(state='normal')
        self.indiam_entry.delete(0, 'end')
        self.indiam_entry.insert(0, '%.2f' % ID)
        self.indiam_entry.config(state='DISABLED')
    
    def update_time(self, time):
        #Update the temperature widget
        self.time_entry.config(state='normal')
        self.time_entry.delete(0, 'end')
        timestring = str(datetime.timedelta(seconds=time))[:-4]
        self.time_entry.insert(0, timestring)
        self.time_entry.config(state='DISABLED')

    def update_acq_rate(self, acqrate):
        #Update the temperature widget
        self.acq_rate__entry.config(state='normal')
        self.acq_rate__entry.delete(0, 'end')
        acqratestring = str(acqrate)
        self.acq_rate__entry.insert(0, acqratestring)
        self.acq_rate__entry.config(state='DISABLED')
        
    # Function that changes the exposure on enter key
    def update_exposure(self,event):
        global prevcontents,exposure        
        try:
        # Check if the exposure is within a suitable range
            exp = self.contents.get()
            if exp < 10:
                exp = 10
            elif exp > 500:
                exp = 500
            self.exposure_entry.delete(0, 'end')
            self.exposure_entry.insert('0', exp) 
            if exp < 250:
                tmb.showinfo("Warning", "Except for ThorCam, we recommend an exposure between 250 ms and 500ms")

            print "Setting exposure to:", exp
            self.parent.exposure = int(exp)
            prevcontents = exp
            exposure = exp
        except: 
            print "Exposure remaining at:", prevcontents
            self.exposure_entry.delete(0, 'end')
            self.exposure_entry.insert('0', prevcontents)
            exposure = prevcontents
        self.set_camera.set_exp(exposure)

    def update_rec_interval(self,event):
        global rec_interval, rec_prevcontents
        try: # Should check contents for int rather than try and catch exception
            rec = self.rec_contents.get()
            self.rec_interval_entry.delete(0, 'end')
            self.rec_interval_entry.insert('0', rec) 
            self.parent.rec_interval = int(rec)
            rec_prevcontents = rec
            rec_interval = rec
        except: 
            print "Record interval remaining at:", rec_prevcontents
            self.rec_interval_entry.delete(0, 'end')
            self.rec_interval_entry.insert('0', rec_prevcontents)
            rec_interval = rec_prevcontents

    def update_num_lines(self,event):
        global num_lines, num_lines_prevcontents
        try: # Should check contents for int rather than try and catch exception
            num_lines = self.num_lines_contents.get()
            if num_lines < 5:
                num_lines = 5
            elif num_lines > 50:
                num_lines = 50
            self.num_lines_entry.delete(0, 'end')
            self.num_lines_entry.insert('0', num_lines) 
            self.parent.num_lines = int(num_lines)
            print "Setting number of lines to: ", self.parent.num_lines
            num_lines_prevcontents = num_lines
            num_lines = num_lines
            
        except: 
            print "Number of lines remaining at:", num_lines_prevcontents
            self.num_lines_entry.delete(0, 'end')
            self.num_lines_entry.insert('0', num_lines_prevcontents)
            num_lines = num_lines_prevcontents

        # TO DO MAKE SURE THIS WORKS
        # Function that changes the exposure on enter key
    def update_scale(self,event):
        global scale_prevcontents, multiplication_factor
        print "updating the scale..."
        try:
        # Check if the exposure is within a suitable range
            scale = self.scale_contents.get()
            print "the scale is:", scale
            self.scale_entry.delete(0, 'end')
            self.scale_entry.insert('0', scale) 
            print "Setting scale to:", scale
            self.parent.multiplication_factor = scale
            scale_prevcontents = scale
            multiplication_factor = scale
            
        except:
            print "Scale remaining at:", scale_prevcontents
            self.scale_entry.delete(0, 'end')
            self.scale_entry.insert('0', scale_prevcontents)
            multiplication_factor = scale_prevcontents


    def mainWidgets(self):
        self.toolbarview = ttk.Frame(root, relief=RIDGE)
        self.toolbarview.grid(row=2,column=3,rowspan=2,sticky=N+S+E+W, pady=0)

   # Tool bar groups
        source_group = ttk.LabelFrame(self, text='Source', height=150, width=150)
        source_group.pack(side=LEFT, anchor=N, padx=3, fill=Y)

        settings_group = ttk.LabelFrame(self, text='Acquisition Settings', height=150, width=150)
        settings_group.pack(side=LEFT, anchor=N, padx=3, fill=Y)

        ana_settings_group = ttk.LabelFrame(self, text='Analysis Settings', height=150, width=150)
        ana_settings_group.pack(side=LEFT, anchor=N, padx=3, fill=Y)

        outer_diameter_group = ttk.LabelFrame(self, text='Outer Diameter', height=150, width=150)
        outer_diameter_group.pack(side=LEFT, anchor=N, padx=3, fill=Y)

        inner_diameter_group = ttk.LabelFrame(self, text='Inner Diameter', height=150, width=150)
        inner_diameter_group.pack(side=LEFT, anchor=N, padx=3, fill=Y)

        acquisition_group = ttk.LabelFrame(self, text='Data acquisition', height=150, width=150)
        acquisition_group.pack(side=LEFT, anchor=N, padx=3, fill=Y)

        start_group = ttk.LabelFrame(self, text='Start/Stop', height=150, width=150)
        start_group.pack(side=LEFT, anchor=N, padx=3, fill=Y)

    # Source group (e.g. camera and files)
        camera_label = ttk.Label(source_group, text = 'Camera:')
        camera_label.grid(row=0, column=0, sticky=E)

        path_label = ttk.Label(source_group, text = 'Path:')
        path_label.grid(row=1, column=0, sticky=E)

        save_label = ttk.Label(source_group, text = 'File:')
        save_label.grid(row=2, column=0, sticky=E)

        # Flag Start/stop group
        self.start_flag = False
        def set_cam(self):
            if self.start_flag == False:
                camera_label = variable.get()
                self.set_camera.set(camera_label)
                return
            else:
                print "You can't change the camera whilst acquiring images!"
                return

        self.camoptions = ["...","Thorlabs","OpenCV", "FakeCamera"]
        variable = StringVar()
        variable.set(self.camoptions[0])
        self.camera_entry = ttk.OptionMenu(source_group, variable,self.camoptions[0], *self.camoptions, command= lambda _: set_cam(self))
        self.camera_entry.grid(row=0, column=1, pady=5)

        global head, tail
        head,tail = os.path.split(self.parent.filename.name)

        path_entry = ttk.Entry(source_group, width=20)
        path_entry.insert(0, head)
        path_entry.config(state=DISABLED)
        path_entry.grid(row=1, column=1, pady=5)

        save_entry = ttk.Entry(source_group, width=20)
        save_entry.insert(0, tail)
        save_entry.config(state=DISABLED)
        save_entry.grid(row=2, column=1, pady=5)


    # Settings group (e.g. camera and files)
        scale_label = ttk.Label(settings_group, text = 'um/pixel:')
        scale_label.grid(row=0, column=0, sticky=E)

        exposure_label = ttk.Label(settings_group, text = 'Exp (s):')
        exposure_label.grid(row=1, column=0, sticky=E)

        acqrate_label = ttk.Label(settings_group, text = 'Acq rate (Hz):')
        acqrate_label.grid(row=2, column=0, sticky=E)

        rec_interval_label = ttk.Label(settings_group, text = 'Rec intvl (frames):')
        rec_interval_label.grid(row=3, column=0, sticky=E)

        # Scale settings
        scale = self.parent.multiplication_factor
        scalefloat = "%3.0f" % scale
        self.scale_contents = DoubleVar()
        self.scale_contents.set(scalefloat)
        global scale_contents
        scale_prevcontents = self.scale_contents.get()
        self.scale_entry = ttk.Entry(settings_group, textvariable = self.scale_contents,width=20)
        self.scale_entry.grid(row=0, column=1, pady=5)
        self.scale_entry.bind('<Return>', self.update_scale)

        # Exposure settings
        exp = self.parent.exposure
        expfloat = "%3.0f" % exp
        self.contents = IntVar()
        self.contents.set(int(exp))
        global prevcontents
        prevcontents = self.contents.get()
        self.exposure_entry = ttk.Entry(settings_group, textvariable = self.contents,width=20)
        self.exposure_entry.grid(row=1, column=1, pady=5)
        self.exposure_entry.bind('<Return>', self.update_exposure)
                
        # Acquisition rate settings
        acq_rate = self.parent.acq_rate
        acq_rate = "%3.0f" % acq_rate
        self.acq_rate_contents = IntVar()
        self.acq_rate_contents.set(int(acq_rate))
        global acq_rate_prevcontents
        acq_rate_prevcontents = self.acq_rate_contents.get()
        self.acq_rate__entry = ttk.Entry(settings_group, textvariable = self.acq_rate_contents,width=20)
        self.acq_rate__entry.grid(row=2, column=1, pady=5)
        self.acq_rate__entry.configure(state="disabled")
        #self.acq_rate_entry.bind('<Return>', self.acq_rate_exposure)

        # Record interval settings
        rec_interval = self.parent.rec_interval
        self.rec_contents = IntVar()
        self.rec_contents.set(int(rec_interval))
        global rec_prevcontents
        rec_prevcontents = self.rec_contents.get()
        self.rec_interval_entry = ttk.Entry(settings_group, textvariable = self.rec_contents,width=20)
        self.rec_interval_entry.grid(row=3, column=1, pady=5)
        self.rec_interval_entry.bind('<Return>', self.update_rec_interval)


    # Analysis Settings group (e.g. camera and files)
        numlines_label = ttk.Label(ana_settings_group, text = '# of lines:')
        numlines_label.grid(row=0, column=0, sticky=E)

        ROI_label = ttk.Label(ana_settings_group, text = 'ROI:')
        ROI_label.grid(row=1, column=0, sticky=E)

        ref_diam_label = ttk.Label(ana_settings_group, text = 'Ref diameter:')
        ref_diam_label.grid(row=2, column=0, sticky=E)

        # Num lines settings
        num_lines = self.parent.num_lines
        self.num_lines_contents = IntVar()
        self.num_lines_contents.set(int(num_lines))
        global num_lines_prevcontents
        num_lines_prevcontents = self.num_lines_contents.get()
        self.num_lines_entry = ttk.Entry(ana_settings_group, textvariable = self.num_lines_contents,width=20)
        self.num_lines_entry.grid(row=0, column=1, pady=0)
        self.num_lines_entry.bind('<Return>', self.update_num_lines)




        # ROI Settings
        self.set_roi = False
        def ROIset_button_function(get_coords):
            self.set_roi = True
            print "Set ROI = ", self.set_roi
            self.ROI_checkBox.configure(state="enabled")
            stop_acq()
            return self.set_roi
        
        ROI_set_button = ttk.Button(ana_settings_group, text='Set ROI', command= lambda: ROIset_button_function(get_coords=True))
        ROI_set_button.grid(row=1,column=1, columnspan=1, pady=0)

        # ROI Settings
        def refdiam_set_button_function(get_coords):
            #### TODO SORT THIS
            self.ref_OD = self.parent.OD
            print "set ref button pressed = , ", self.ref_OD
            return self.ref_OD


        refdiam_set_button = ttk.Button(ana_settings_group, text='Set ref', command= lambda: refdiam_set_button_function(get_coords=True))
        refdiam_set_button.grid(row=2,column=1, columnspan=1, pady=0)

        self.filter_is_checked = IntVar()

        filter_checkBox = ttk.Checkbutton(ana_settings_group, text='Filter readings', onvalue=1, offvalue=0, variable=self.filter_is_checked)
        filter_checkBox.grid(row=3, columnspan=2, padx=5, pady=3, sticky=W)

        self.ROI_is_checked = IntVar()

        self.ROI_checkBox = ttk.Checkbutton(ana_settings_group, text='Use ROI', onvalue=1, offvalue=0, variable=self.ROI_is_checked)
        self.ROI_checkBox.grid(row=4, columnspan=2, padx=5, pady=3, sticky=W)
        self.ROI_checkBox.configure(state="disabled")
        

    # Outer diameter group
    # Function for the labels
        def coord_label(window, text, row, column):
            label=ttk.Label(window, text=text)
            label.grid(row=row, column=column, padx = 1, sticky=E)
    # Function for the labels 2
        def coord_entry(window, row, column, coord_label):
            entry = ttk.Entry(window, width=8, textvariable=coord_label)

            entry.config(state=NORMAL)
            entry.grid(row=row, column=column, padx=1, sticky=E)
            root.focus_set()
            entry.focus_set()
            root.focus_force()
            return entry
            

        def set_button(window):
            set_button = ttk.Button(window, text='Set', command= lambda: coord_limits(get_coords=True, default = False))
            set_button.grid(row=3, columnspan=4, pady=5)

        def set_button_function(get_coords):
            if get_coords == True:
                self.coord_limits()
                self.parent.graphframe.mainWidgets()
            if get_coords == False:
                pass

        def coord_limits(get_coords, default):
            if get_coords == True:
                if default:
                    self.xlims = (self.x_min_default, self.x_max_default)
                    self.ylims = (self.y_min_default, self.y_max_default)
                    outer_xmin_entry.delete(0, END), outer_xmax_entry.delete(0, END)
                    outer_xmin_entry.insert('0', self.x_min_default), outer_xmax_entry.insert('0', self.x_max_default)
                    outer_ymin_entry.delete(0, END), outer_ymax_entry.delete(0, END)
                    outer_ymin_entry.insert('0', self.y_min_default), outer_ymax_entry.insert('0', self.y_max_default)
                    self.parent.graphframe.update_scale()
                    print "it did it"
                else:
                    self.xlims = (self.x_min_label.get(),self.x_max_label.get())
                    self.ylims = (self.y_min_label.get(),self.y_max_label.get())
                    self.parent.graphframe.update_scale()
                    print "it did it"
                return self.xlims, self.ylims
                get_coords = False
            else:
                pass


    # Set the initial xlimit values
        self.x_min_label, self.x_max_label = IntVar(value=-600), IntVar(value=0)
        self.x_min_default, self.x_max_default = self.x_min_label.get(),self.x_max_label.get()
    # Set the initial xlimit values
        self.y_min_label, self.y_max_label = IntVar(value=100), IntVar(value=250)
        self.y_min_default, self.y_max_default = self.y_min_label.get(),self.y_max_label.get()
    # Get the x and y limits
        self.xlims = (self.x_min_label.get(),self.x_max_label.get())
        self.ylims = (self.y_min_label.get(),self.y_max_label.get())

        outer_xmin_label = coord_label(outer_diameter_group, 'X-Min:', 1, 0)
        outer_xmax_label = coord_label(outer_diameter_group, 'X-Max:', 2, 0)
        outer_ymin_label = coord_label(outer_diameter_group, 'Y-Min:', 1, 2)
        outer_ymax_label = coord_label(outer_diameter_group, 'Y-Max:', 2, 2)


        outer_xmin_entry = coord_entry(outer_diameter_group, 1, 1, self.x_min_label)
        outer_xmax_entry = coord_entry(outer_diameter_group, 2, 1, self.x_max_label)
        outer_ymin_entry = coord_entry(outer_diameter_group, 1, 3, self.y_min_label)
        outer_ymax_entry = coord_entry(outer_diameter_group, 2, 3, self.y_max_label)

        outer_set_button = set_button(outer_diameter_group)     

    # Button to set the axis limits to the default values 
        set_button = ttk.Button(outer_diameter_group, text='Default', command= lambda: coord_limits(get_coords=True, default = True))
        set_button.grid(row=4, columnspan=4, pady=5) 


        #********** Inner Diameter Group **********

        def set_button2(window):
            set_button = ttk.Button(window, text='Set', command= lambda: coord_limits2(get_coords=True, default = False))
            set_button.grid(row=3, columnspan=4, pady=5)

        def set_button_function(get_coords):
            if get_coords == True:
                self.coord_limits2()
            if get_coords == False:
                pass



        def coord_limits2(get_coords, default):
            if get_coords == True:
                if default:
                    self.xlims2 = (self.x_min_default2, self.x_max_default2)
                    self.ylims2 = (self.y_min_default2, self.y_max_default2)
                    inner_xmin_entry.delete(0, END), inner_xmax_entry.delete(0, END)
                    inner_xmin_entry.insert('0', self.x_min_default2), inner_xmax_entry.insert('0', self.x_max_default2)
                    inner_ymin_entry.delete(0, END), inner_ymax_entry.delete(0, END)
                    inner_ymin_entry.insert('0', self.y_min_default2), inner_ymax_entry.insert('0', self.y_max_default2)
                else:
                    self.xlims2 = (self.x_min_label2.get(),self.x_max_label2.get())
                    self.ylims2 = (self.y_min_label2.get(),self.y_max_label2.get())
                return self.xlims2, self.ylims2
                get_coords = False
            else:
                pass
    # Set the initial xlimit values
        self.x_min_label2, self.x_max_label2 = IntVar(value=-600), IntVar(value=0)
        self.x_min_default2, self.x_max_default2 = self.x_min_label2.get(),self.x_max_label2.get()
    # Set the initial xlimit values
        self.y_min_label2, self.y_max_label2 = IntVar(value=50), IntVar(value=200)
        self.y_min_default2, self.y_max_default2 = self.y_min_label2.get(),self.y_max_label2.get()
    # Get the x and y limits
        self.xlims2 = (self.x_min_label2.get(),self.x_max_label2.get())
        self.ylims2 = (self.y_min_label2.get(),self.y_max_label2.get())


        inner_xmin_label = coord_label(inner_diameter_group, 'X-Min:', 1, 0)
        inner_xmax_label = coord_label(inner_diameter_group, 'X-Max:', 2, 0)
        inner_ymin_label = coord_label(inner_diameter_group, 'Y-Min:', 1, 2)
        inner_ymax_label = coord_label(inner_diameter_group, 'Y-Max:', 2, 2)


        inner_xmin_entry = coord_entry(inner_diameter_group, 1, 1, self.x_min_label2)
        inner_xmax_entry = coord_entry(inner_diameter_group, 2, 1, self.x_max_label2)
        inner_ymin_entry = coord_entry(inner_diameter_group, 1, 3, self.y_min_label2)
        inner_ymax_entry = coord_entry(inner_diameter_group, 2, 3, self.y_max_label2)

        inner_set_button = set_button2(inner_diameter_group)

    # Button to set the axis limits to the default values 
        set_button = ttk.Button(inner_diameter_group, text='Default', command= lambda: coord_limits2(get_coords=True, default = True))
        set_button.grid(row=4, columnspan=4, pady=5) 


    # acquisition_group
        def coord_label(window, text, row, column):
            label=ttk.Label(window, text=text)
            label.grid(row=row, column=column, padx = 1, sticky=E)

        temp_label = ttk.Label(acquisition_group, text = 'Temp (oC):')
        temp_label.grid(row=0, column=0, sticky=E)

        pressureavg_label = ttk.Label(acquisition_group, text = 'Avg Pressure (mmHg):')
        pressureavg_label.grid(row=1, column=0, sticky=E)

        outdiam_label = ttk.Label(acquisition_group, text = 'Outer diameter (um):')
        outdiam_label.grid(row=2, column=0, sticky=E)

        indiam_label = ttk.Label(acquisition_group, text = 'Inner diameter (um):')
        indiam_label.grid(row=3, column=0, sticky=E)

        time_label = ttk.Label(acquisition_group, text = 'Time (hr:min:sec:msec):')
        time_label.grid(row=4, column=0, sticky=E)

        self.temp_entry = ttk.Entry(acquisition_group, width=10)
        self.temp_entry.insert(0, "N/A")
        self.temp_entry.config(state=DISABLED)
        self.temp_entry.grid(row=0, column=1, pady=0)

        self.pressureavg_entry = ttk.Entry(acquisition_group, width=10)
        self.pressureavg_entry.insert(0, "N/A")
        self.pressureavg_entry.config(state=DISABLED)
        self.pressureavg_entry.grid(row=1, column=1, pady=0)

        self.outdiam_entry = ttk.Entry(acquisition_group, width=10)
        self.outdiam_entry.insert(0, "N/A")
        self.outdiam_entry.config(state=DISABLED)
        self.outdiam_entry.grid(row=2, column=1, pady=0)

        self.indiam_entry = ttk.Entry(acquisition_group, width=10)
        self.indiam_entry.insert(0, "N/A")
        self.indiam_entry.config(state=DISABLED)
        self.indiam_entry.grid(row=3, column=1, pady=0)

        self.time_entry = ttk.Entry(acquisition_group, width=10)
        self.time_entry.insert(0, "N/A")
        self.time_entry.config(state=DISABLED)
        self.time_entry.grid(row=4, column=1, pady=0)




    # Function that will start the image acquisition
        def start_acq():
            if variable.get() == "...":
                tmb.showwarning(title="Warning", message = "You need to select a camera source!")
                self.start_flag = False
            else:
                self.camera_entry.configure(state="disabled")
                self.exposure_entry.configure(state="disabled")
                self.scale_entry.configure(state="disabled")
                self.rec_interval_entry.configure(state="disabled")
                self.num_lines_entry.configure(state="disabled")
                self.start_flag = True
                self.record_video_checkBox.configure(state="disabled")
                mmc.startContinuousSequenceAcquisition(0)
            return self.start_flag
    # Function that will stop the image acquisition
        def stop_acq():
            self.camera_entry.configure(state="enabled")
            self.exposure_entry.configure(state="enabled")
            self.scale_entry.configure(state="enabled")
            self.rec_interval_entry.configure(state="enabled")
            self.num_lines_entry.configure(state="enabled")
            self.start_flag = False
            self.record_video_checkBox.configure(state="enabled")
            mmc.stopSequenceAcquisition()
            self.record_flag = False
            return self.start_flag,self.record_flag

    # Function that will start the data acquisition
        self.record_flag = False
        def record_data():
            if self.start_flag == True:
                self.record_flag = True
                mmc.clearCircularBuffer()
            print "Just set the record flag to: ", self.record_flag
            return self.record_flag
        '''
        def stop_record_data():
            self.record_flag = False
            print "Just set the record flag to: ", self.record_flag
            return self.record_flag
        '''
        def snapshot():
            self.snapshot_flag = True
            return self.snapshot_flag


        start_button = ttk.Button(start_group, text='Start', command= lambda: start_acq())
        start_button.grid(row=0, column=0, pady=0, sticky=N+S+E+W) 
        #console = tk.Button(master, text='Exit', command=self.close_app)
        #console.pack(  )
        live_button = ttk.Button(start_group, text='Stop', command= lambda: stop_acq())
        live_button.grid(row=1, column=0, pady=0, sticky=N+S+E+W) 

        record_button = ttk.Button(start_group, text='Track', command= lambda: record_data())
        record_button.grid(row=3, column=0, pady=0, sticky=N+S+E+W) 
        
        self.snapshot_flag = False
        snapshot_button = ttk.Button(start_group, text='Snapshot', command= lambda: snapshot())
        snapshot_button.grid(row=4, column=0, pady=0, sticky=N+S+E+W) 

        #stop_record_button = ttk.Button(start_group, text='Stop tracking', command= lambda: stop_record_data())
        #stop_record_button.grid(row=4, column=0, pady=5, sticky=N+S+E+W) 

        self.record_is_checked = IntVar()

        self.record_video_label = ttk.Label(settings_group, text = 'Record video?')
        self.record_video_label.grid(row=4, column=0, sticky=E)
        self.record_video_checkBox = ttk.Checkbutton(settings_group, onvalue=1, offvalue=0, variable=self.record_is_checked)
        self.record_video_checkBox.grid(row=4, column=1, columnspan=1, padx=5, pady=3, sticky=W)



class GraphFrame(tk.Frame):

    min_x = 0
    max_x = 10
    def __init__(self,parent):
        tk.Frame.__init__(self, parent, bg = "yellow")#, highlightthickness=2, highlightbackground="#111")
        self.parent = parent
        self.top = Frame()
        self.top.update_idletasks()
        self.n_points = 1000
        self.xlim1 = self.parent.toolbar.x_min_default # Outer
        self.xlim2 = self.parent.toolbar.x_max_default # Outer
        self.ylim1 = self.parent.toolbar.y_min_default # Outer
        self.ylim2 = self.parent.toolbar.y_max_default # Outer


        self.xlim3 = self.parent.toolbar.x_min_default2 # Inner
        self.xlim4 = self.parent.toolbar.x_max_default2 # Inner
        self.ylim3 = self.parent.toolbar.y_min_default2 # Inner
        self.ylim4 = self.parent.toolbar.y_max_default2 # Inner

        self.delta_i = 1
        self.n_data = 100000000
        self.update = 1
        #self.mainWidgets()
        
    def update_scale(self, blit=True): #### NEE
        print "attempting to update a blitted axis"
        self.graphview.ax1.set_xlim(self.parent.toolbar.xlims[0],self.parent.toolbar.xlims[1]) # Outer diameter
        self.graphview.ax1.set_ylim(self.parent.toolbar.ylims[0],self.parent.toolbar.ylims[1]) # Outer diameter

        self.graphview.figure.canvas.draw()

    
 


    def mainWidgets(self,blit=True):  
        #
        # We want to explicitly set the size of the graph so that we can blit
        print "this is the height: ", self.parent.graphframe.winfo_height()
        print "this is the width: ", self.parent.graphframe.winfo_width()

        self.graphview = tk.Label(self)
        #print "Graph width: ", self.graphview.winfo_width()
        #print "Graph height: ", self.parent.graphframe.winfo_height()
        default_figsize = (plt.rcParams.get('figure.figsize'))
        print "default fig size = ", default_figsize
        other_figsize = [self.parent.graphframe.winfo_width()/100,self.parent.graphframe.winfo_height()/100]
        print other_figsize
        self.graphview.figure,(self.graphview.ax1,self.graphview.ax2) = plt.subplots(2,1, figsize=other_figsize)
        #self.graphview.figure = pyplot.figure()
        #self.graphview.ax1 = self.graphview.figure.add_subplot(211)
        #self.graphview.ax2 = self.graphview.figure.add_subplot(212)
        self.graphview.line, = self.graphview.ax1.plot([],[]) # initialize line to be drawn
        self.graphview.line2, = self.graphview.ax2.plot([],[])

        self.graphview.ax1.set_xlim(self.xlim1,self.xlim2) # Outer
        self.graphview.ax2.set_xlim(self.xlim3,self.xlim4) # Inner
        self.graphview.ax1.set_ylim(self.ylim1,self.ylim2) # Outer
        self.graphview.ax2.set_ylim(self.ylim3,self.ylim4) # Inner

        #self.graphview.ax1.set_xlabel('Time (s)', fontsize=14) # Outer diameter labels
        self.graphview.ax1.set_ylabel('Outer diameter (um)', fontsize=14) # Outer diameter labels

        self.graphview.ax2.set_xlabel('Time (s)', fontsize=14) # Inner diameter labels
        self.graphview.ax2.set_ylabel('Lumen diameter (um)', fontsize=14) # Inner diameter labels



        self.graphview.figure.canvas = FigureCanvasTkAgg(self.graphview.figure, self)
        self.graphview.figure.canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=None, expand=False) ##### THIS IS THE PROBLEM WITH BLITTING HERE. WE NEED TO EXPLICITLY STATE THE FIGURE SIZE ABOVE!!
        print "Graph width: ", self.graphview.figure.canvas.get_tk_widget().winfo_width()
        self.graphview.figure.canvas.draw()
        print "Graph width: ", self.graphview.figure.canvas.get_tk_widget().winfo_width()

        if blit:
        # Get the background
            self.ax1background = self.graphview.figure.canvas.copy_from_bbox(self.graphview.ax1.bbox)
            self.ax2background = self.graphview.figure.canvas.copy_from_bbox(self.graphview.ax2.bbox)

            print "bounding box = ", self.graphview.ax1.bbox.get_points()
            bbarrray = self.graphview.ax1.bbox.get_points()
            from matplotlib.transforms import Bbox

            my_blit_box = Bbox(bbarrray)
            #my_blit_box = Bbox(np.array([[x0,y0],[x1,y1]]))
            my_blit_box = Bbox.from_bounds(bbarrray[0][0], bbarrray[0][1], (bbarrray[1][0]-bbarrray[0][0])*1.5, bbarrray[1][1]-bbarrray[0][1])
            print "bounding box = ", my_blit_box.get_points()
            self.ax1background = self.graphview.figure.canvas.copy_from_bbox(my_blit_box)
        





    def on_running(self, xdata, ydata1,ydata2,xlims,ylims, xlims2,ylims2,blit=True):
    # Set the axis values
        self.graphview.ax1.set_xlim(xlims[0],xlims[1]) # Outer diameter
        self.graphview.ax1.set_ylim(ylims[0],ylims[1]) # Outer diameter

        self.graphview.ax2.set_xlim(xlims2[0],xlims2[1]) # Inner diameter
        self.graphview.ax2.set_ylim(ylims2[0],ylims2[1]) # Inner diameter

    # Subtract off the latest time point, so that the current time is t = 0
        xdata = [el-xdata[-1] for el in xdata]

    # Make every 7th point different so we can see when plotting
        #ydata1 = [t if k%7 else t-10 for k,t in enumerate(ydata1)]
        #ydata2 = [t if k%7 else t-10 for k,t in enumerate(ydata2)]  
    
    # Get the xdata points that fit within the axis limits
        xdata3 = [el for el in xdata if el > xlims[0]]
        xdata4 = [el for el in xdata if el > xlims2[0]]
    
    # Get the corresponding ydata points
        ydata1A = ydata1[::-1]
        ydata1B = ydata1A[0:len(xdata3)]
        ydata1C = ydata1B[::-1]

        ydata2A = ydata2[::-1]
        ydata2B = ydata2A[0:len(xdata4)]
        ydata2C = ydata2B[::-1]

        #ydata1 = [el2 for (el1,el2) in zip(xdata,ydata1) if el1 > self.xlim1-5] # For some reason this did not work
        #ydata2 = [el2 for (el1,el2) in zip(xdata,ydata2) if el1 > self.xlim1-5] # For some reason this did not work


        # If there are many data points, it is a waste of time to plot all
        #   of them once the screen resolution is reached,
        #   so when the maximum number of points is reached,
        #   halve the number of points plotted. This is repeated
        #   every time the number of data points has doubled.
        
        self.i = int(len(xdata3))
        self.i2 = int(len(xdata4))
        '''
        if self.i == self.n_points :
            self.n_points *= 2
            # frequency of plotted points
            self.delta_i *= self.n_points/self.i
            self.update = max(self.delta_i, self.update)
            print("updating n_rescale = ",\
                self.n_points, self.update, self.delta_i)
        '''
        # drawing the canvas takes most of the CPU time, so only update plot
        #   every so often
        if blit == False:
            if self.i == self.n_data-1 or not (self.i % self.update)  :

                self.graphview.ax1.lines.remove(self.graphview.line)
                self.graphview.ax2.lines.remove(self.graphview.line2)

                self.graphview.line, = self.graphview.ax1.plot(
                                            xdata3[::-1][0::int(self.delta_i)][::-1],
                                                ydata1C[::-1][0::int(self.delta_i)][::-1],
                                                color="blue", linewidth = 3)

                self.graphview.line2, = self.graphview.ax2.plot(
                                            xdata4[::-1][0::int(self.delta_i)][::-1],
                                                ydata2C[::-1][0::int(self.delta_i)][::-1],
                                                color="red", linewidth = 3)


            self.graphview.figure.canvas.draw()
            self.graphview.figure.canvas.get_tk_widget().update_idletasks()
            #self.after(2,self.plotter)
            #self.graphview.figure.canvas.flush_events()
        if blit == True:
            self.graphview.figure.canvas.restore_region(self.ax1background)
            self.graphview.figure.canvas.restore_region(self.ax2background)

            try:
                self.graphview.ax1.lines.remove(self.graphview.line)
                self.graphview.ax2.lines.remove(self.graphview.line2)
            except:
                pass



            self.graphview.line.set_xdata(xdata3[::-1][0::int(self.delta_i)][::-1])
            self.graphview.line.set_ydata(ydata1C[::-1][0::int(self.delta_i)][::-1])
            self.graphview.line.set_color('blue')


            self.graphview.line2.set_xdata(xdata4[::-1][0::int(self.delta_i)][::-1])
            self.graphview.line2.set_ydata(ydata2C[::-1][0::int(self.delta_i)][::-1])
            self.graphview.line2.set_color('red')

            # redraw just the points
            self.graphview.ax1.draw_artist(self.graphview.line)
            self.graphview.ax2.draw_artist(self.graphview.line2)

            # fill in the axes rectangle
            self.graphview.figure.canvas.blit(self.graphview.ax1.bbox)
            self.graphview.figure.canvas.blit(self.graphview.ax2.bbox)

            #self.graphview.figure.canvas.draw_idle()
            #self.graphview.figure.canvas.flush_events()

            #self.graphview.figure.canvas.update()
            #self.graphview.figure.canvas.flush_events()
            #self.graphview.figure.canvas.get_tk_widget().update_idletasks()




        #Example
    def plot(self, timelist, outers, inners,xlims,ylims, xlims2, ylims2):
    # Get the data
        xdata = timelist # Time
        ydata1 = outers # Outer diameter
        ydata2 = inners # Inner diameter
        xlims = xlims # Outer diameter
        ylims = ylims # Outer Diameter
        xlims2 = xlims2 # Inner diameter
        ylims2 = ylims2 # Inner diameter

        if len(xdata)>1:
            self.on_running(xdata, ydata1,ydata2,xlims,ylims,xlims2,ylims2)
        return

# Class for timing processes
'''
class TimeIt():
    from datetime import datetime
    def __enter__(self):
        self.tic = self.datetime.now()
    def __exit__(self, *args, **kwargs):
        print('plot graph runtime: {}'.format(self.datetime.now() - self.tic))

class TimeIt2():
    from datetime import datetime
    def __enter__(self):
        self.tic = self.datetime.now()
    def __exit__(self, *args, **kwargs):
        print('process queue runtime: {}'.format(self.datetime.now() - self.tic))
'''

class TimeIt():
    from datetime import datetime
    def __init__(self):
        self.name = None
    def __call__(self, name):
        self.name = name
        return self
    def __enter__(self):
        self.tic = self.datetime.now()
        return self
    def __exit__(self,name, *args, **kwargs):
        print('process ' + self.name + ' runtime: {}'.format(self.datetime.now() - self.tic))##]]

class TimeIt2():
    from datetime import datetime
    def __init__(self):
        self.name = None
    def __call__(self, name):
        self.name = name
        return self
    def __enter__(self):
        self.tic = self.datetime.now()
        return self
    def __exit__(self,name, *args, **kwargs):
        print('process ' + self.name + ' runtime: {}'.format(self.datetime.now() - self.tic))##]]





class TableFrame(tk.Frame):
    def __init__(self,parent):
        tk.Frame.__init__(self, parent)#,highlightthickness=2,highlightbackground="#111")#, width=250, height = 300)#, highlightthickness=2, highlightbackground="#111")
        self.parent = parent
        self.mainWidgets()
              
    def mainWidgets(self):
        self.tableview = ttk.Frame(self)
        self.tableview.grid(row=1, column=3, sticky=N+S+E+W)

        try:
            OutDiam = float(self.parent.processIncoming.OD)
            InDiam = float(self.parent.processIncoming.ID)
        except:
            pass
        


        def add_row():
            try:
                OutDiam = float(OD)
                InDiam = float(ID)
                Label = table_text_entry.get()
                Time = (time.time() - start_time)
                Time = float(Time)
                Time = round(Time, 1)
                mxDiastring = StringVar()
                max_diameter_text.set(str(self.parent.toolbar.ref_OD))
                max_diameter = self.parent.toolbar.ref_OD
                #max_diameter = max_diameter_text.set()
                #max_diameter = int(max_diameter)
                if max_diameter > 0:
                    max_diameter = float(max_diameter)
                    max_percent = ((float(OutDiam/max_diameter))*100)
                    max_percent = round(max_percent, 1)
                    table_1.insert('', 'end', values=(Time, Label, OutDiam, 60,60, max_percent)) #P1, P2
                    hello = ((Time, Label, OutDiam, P1, P2, max_percent))
                
                else:
                    max_percent = '-'
                    table_1.insert('', 'end', values=(Time, Label, OutDiam, 60,60, max_percent)) #P1, P2
                    hello = ((Time, Label, OutDiam, P1, P2, max_percent))
                
                table_1.yview_moveto(1)

            except ValueError:
                max_percent = '-'
                table_1.insert('', 'end', values=(Time, Label, OutDiam, P1, P2, max_percent))
                hello = ((Time, Label, OutDiam, P1, P2))
            save_table(hello)

        table_text_entry = StringVar()
        max_diameter_text = StringVar()


        def save_table(hello):
            with open((self.parent.txt_file), 'ab') as g:
                w=csv.writer(g, quoting=csv.QUOTE_ALL)
                w.writerow(hello)


        table_text_entry = StringVar()
        max_diameter_text = StringVar()


        table_2 = tk.Frame(self.tableview)
        table_2.grid(row=0, column=0, columnspan=5, sticky=N+S+E+W)

        table_label = ttk.Label(table_2, text = 'Label:')
        table_label.grid(row=0, column=0)
        table_entry = ttk.Entry(table_2, width=30, textvariable=table_text_entry )
        table_entry.grid(row=0, column=1)        
        add_button = ttk.Button(table_2, text='Add', command=add_row)
        add_button.grid(row=0, column=2)
        max_diameter_label = ttk.Label(table_2, text='Reference Diameter:')
        max_diameter_label.grid(row=0, column=3)
        max_diameter_entry = ttk.Entry(table_2, width=5, textvariable=max_diameter_text )
        max_diameter_entry.grid(row=0, column=4)

       
        
        table_1 = ttk.Treeview(self.tableview, show= 'headings')
        table_1["columns"] = ('Time', 'Label', 'Outer Diameter', 'Pressure 1', 'Pressure 2', '% Ref')

        table_1.column('#0', width=30)
        table_1.column('Time', width=100, stretch=True)
        table_1.column('Label', width=150)
        table_1.column('Outer Diameter', width=100)
        table_1.column('Pressure 1', width=100)
        table_1.column('Pressure 2', width=100)
        table_1.column('% Ref', width=50)

        table_1.heading('#1', text = 'Time')
        table_1.heading('#2', text = 'Label')
        table_1.heading('#3', text = 'Outer Diameter')
        table_1.heading('#4', text = 'Pressure 1')
        table_1.heading('#5', text = 'Pressure 2')
        table_1.heading('#6', text = '% Ref')


        scrollbar = Scrollbar(self.tableview)
        scrollbar.grid(row=1,column=2, sticky=NS)
        scrollbar.config( command = table_1.yview )
        table_1.grid(row=1, column=1, sticky=N+S+E+W)



class CameraFrame(tk.Frame):
    def __init__(self,parent):
        tk.Frame.__init__(self, parent)#, width=1000, height = 600)#, highlightthickness=2, highlightbackground="#111")
        self.parent = parent
        self.mainWidgets()
              
    def mainWidgets(self):
        # Get the max dimensions that the Canvas can be
        self.maxheight = self.parent.graphframe.winfo_height() - self.parent.tableframe.winfo_height() - self.parent.status_bar.winfo_height()
        self.maxwidth = self.parent.status_bar.winfo_width() -  self.parent.graphframe.winfo_width()
        # Set up the Canvas that we will show the image on
        self.cameraview = tk.Canvas(self, width=self.maxwidth, height=self.maxheight, background='white')
        self.cameraview.grid(row=2,column=2,sticky=N+S+E+W, pady=ypadding)

        # ROI rectangle initialisation
        self.rect = None
        self.start_x = None
        self.start_y = None
        self.end_x = None
        self.end_y = None
        # Factors for scaling ROI to original image (which is scaled to fit canvas)
        self.delta_width = None
        self.delta_height = None
        self.scale_factor = None

        # Bind events to mouse
        self.cameraview.bind("<ButtonPress-1>",self.on_button_press)
        self.cameraview.bind("<B1-Motion>",self.on_move_press)
        self.cameraview.bind("<ButtonRelease-1>",self.on_button_release)


    # Define functions for mouse actions
    def on_button_press(self, event):
        if self.parent.toolbar.set_roi == True: # Only enable if we have just pressed the button
            # Delete any old ROIs
            found = event.widget.find_all()
            for iid in found:
                if event.widget.type(iid) == 'rectangle':
                    event.widget.delete(iid)
            # Create the rectangle ROI
            self.start_x = event.x
            self.start_y = event.y
            self.rect = self.cameraview.create_rectangle(self.start_x, self.start_y, self.start_x, self.start_y)

    def on_move_press(self, event):
        #Update the ROI when the mouse is dragged
        if self.parent.toolbar.set_roi == True:
            curX, curY = (event.x, event.y)
            self.cameraview.coords(self.rect, self.start_x, self.start_y, curX, curY)


    def on_button_release(self, event):
        if self.parent.toolbar.set_roi == True: # Only enable if we have just pressed the button
            self.end_x =  event.x
            self.end_y =  event.y
            self.parent.toolbar.set_roi = False
            self.parent.toolbar.ROI_checkBox.state(['selected'])
            self.parent.toolbar.ROI_is_checked.set(1)
            pass  

    def rescale_frame(self,frame):
        # Scaling a rectangle to fit inside another rectangle.
        # works out destinationwidth/sourcewidth and destinationheight/sourceheight
        # and scaled by the smaller of the two ratios
        width = frame.shape[1]
        height = frame.shape[0]

        #print "INFO"
        #print width, height
        #print self.maxwidth, self.maxheight

        widthfactor = self.maxwidth / width
        heightfactor = self.maxheight / height

        if widthfactor < heightfactor:
            self.scale_factor = widthfactor
        else:
            self.scale_factor = heightfactor

        global scale_factor
        scale_factor = self.scale_factor

        #print scale_factor

        width = int(frame.shape[1] * self.scale_factor)
        height = int(frame.shape[0] * self.scale_factor)

        #print "NEWDIMS"
        #print  width, height

        self.delta_width = int((self.maxwidth - width)/2)
        self.delta_height = int((self.maxheight - height)/2)

        global delta_height
        delta_height = self.delta_height

        return cv2.resize(frame, (width, height), interpolation = cv2.INTER_AREA)
     
    def process_queue(self,params,img,count):

        try:
            img = img
            imgc = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)

            '''
            # TODO FIGURE OUT CODECS FOR AVI FILE
            if count == 0:
                # Add file for avi output
                global out
                aviPath = os.path.join(head, '%s.avi' % os.path.splitext(tail)[0])
                out = cv2.VideoWriter(aviPath,-1, 10,(int(imgc.shape[1]),int(imgc.shape[0])))
            '''
            
            timenow,OD1,OD2,ID1,ID2,OuterD,start,diff,ODS_flag,IDS_flag, ROI = params

            if self.parent.toolbar.record_flag:
                
                # Draw the diameters:
                for m,OD in enumerate(OD1):
                    if self.parent.toolbar.filter_is_checked.get() == 0:
                        C1 = (255,0,0) # blue
                        C2 = (0,0,255) #red
                    else:
                        if ODS_flag[m] == 1:
                            C1 = (255,0,0) # blue
                        else:
                            C1 = (0,0,0) #black
                        if IDS_flag[m] == 1:
                            C2 = (0,0,255) #red
                        else:
                            C2 = (0,0,0) #black

                    pos = m*diff+start
                    #Horizontal lines
                    imgc = cv2.line(imgc,(OD1[m],pos),(OD2[m],pos),C1,4) #in opencv rgb is bgr
                    imgc = cv2.line(imgc,(ID2[m],pos),(ID1[m],pos),C2,2) #in opencv rgb is bgr
                    #Vertical lines
                    imgc = cv2.line(imgc,(OD2[m],pos-5),(OD2[m],pos+5),C1,4) #in opencv rgb is bgr
                    imgc = cv2.line(imgc,(OD1[m],pos-5),(OD1[m],pos+5),C1,4) #in opencv rgb is bgr
                    imgc = cv2.line(imgc,(ID2[m],pos-5),(ID2[m],pos+5),C2,2) #in opencv rgb is bgr
                    imgc = cv2.line(imgc,(ID1[m],pos-5),(ID1[m],pos+5),C2,2) #in opencv rgb is bgr

                # Adding ROI to the image.
                # There is a problem here.
                # The RECTANGLE function uses coordinates from a box drawn on a scaled image
                # We then plot these directly onto the original image, and then scale it again
                # I need to transform the rectangle coordinates and subtract these off.
                heightdiff = self.maxheight - imgc.shape[0]
                widthdiff = self.maxwidth - imgc.shape[1]

                # This is drawing on the region of interest
                Cwhite = (0,0,0)
                # First one is horizontal line
                if self.rect and self.parent.toolbar.ROI_is_checked.get() == 1:
                    rx0 = int((ROI[0][0]  - self.delta_width)/self.scale_factor)#
                    rx1 = int((ROI[1][0]  - self.delta_width)/self.scale_factor)#
                    ry0 = int((ROI[0][1]  - self.delta_height)/self.scale_factor) #
                    ry1 = int((ROI[1][1]  - self.delta_height)/self.scale_factor)#


                    #print "height = ", imgc.shape[0]
                    #print "maxheight  = ", self.maxheight
                    #print "width = ", imgc.shape[1]
                    #print "maxwidth  = ", self.maxwidth
                    #print self.delta_width, self.delta_height
                    #print "scale factor = ", self.scale_factor
                else:
                    #print "Using this ROI"
                    rx0 = ROI[0][0]#int((ROI[0][0]  - self.delta_width)/self.scale_factor)
                    rx1 = ROI[1][0]#int((ROI[1][0]  - self.delta_width)/self.scale_factor)
                    ry0 = ROI[0][1]#int((ROI[0][1]  - self.delta_height)/self.scale_factor)
                    ry1 = ROI[1][1]#int((ROI[1][1]  - self.delta_height)/self.scale_factor)


                imgc = cv2.line(imgc,(rx0,ry0),(rx1,ry0),Cwhite,1) #in opencv rgb is bgr
                imgc = cv2.line(imgc,(rx0,ry1),(rx1,ry1),Cwhite,1) #in opencv rgb is bgr
                imgc = cv2.line(imgc,(rx0,ry0),(rx0,ry1),Cwhite,1) #in opencv rgb is bgr
                imgc = cv2.line(imgc,(rx1,ry0),(rx1,ry1),Cwhite,1) #in opencv rgb is bgr
                
                     

                #cv2.putText(imgc, 't=%.2f s' %timenow,(30,30), cv2.FONT_HERSHEY_SIMPLEX, 1,(255,255,255),2,cv2.LINE_AA)
                if self.parent.toolbar.record_is_checked.get() == 1:# and self.parent.count%self.parent.rec_interval == 0:
                        timenow2 = int(timenow)
                        directory = os.path.join(head, 'Tiff\\')
                        if not os.path.exists(directory):
                            os.makedirs(directory)
                        gfxPath = os.path.join(directory, '%s_f=%s_Result.tiff' % (os.path.splitext(tail)[0],str(self.parent.count).zfill(6))) 
                        cv2.imwrite(gfxPath,imgc)
                        #out.write(imgc) # For writing to AVI file.
                else:
                    pass

                if self.parent.toolbar.snapshot_flag == True:
                    print "Snapshot pressed"
                    timenow2 = int(timenow)
                    gfxPath = os.path.join(head, '%s_t=%ss_Result SNAPSHOT.tiff' % (os.path.splitext(tail)[0],timenow2)) 
                    cv2.imwrite(gfxPath,imgc)
                    self.parent.toolbar.snapshot_flag = False
                else:
                    pass

           

            #Rescale the image so it doesnt take over the screen
            imgc = self.rescale_frame(imgc)


            
            imgc = cv2.cvtColor(imgc, cv2.COLOR_BGR2RGBA)
            prevImg = Image.fromarray(imgc)
            imgtk = ImageTk.PhotoImage(image=prevImg)
            #Show the image
            self.imgtk = imgtk
            self.image_on_canvas_ = self.cameraview.create_image(self.maxwidth/2, self.maxheight/2, anchor=CENTER,image=self.imgtk)


        except:
            pass


class Arduino:
    def __init__(self, PORTS):
        # Open the serial ports
        self.PORTS = PORTS

        ### Finds COM port that the Arduino is on (assumes only one Arduino is connected)
        wmi = win32com.client.GetObject("winmgmts:")
        ArduinoComs = []
        for port in wmi.InstancesOf("Win32_SerialPort"):
            #print port.Name #port.DeviceID, port.Name
            if "Arduino" in port.Name:
                comPort = port.DeviceID
                ArduinoComs.append(comPort)
                #print comPort, "is Arduino"

        self.PORTS = []
        for i,comPort in enumerate(ArduinoComs):
            print comPort
            GLOBAL_PORT = serial.Serial(comPort, baudrate=9600, dsrdtr=True)
            #GLOBAL_PORT.setDTR(True)

            self.PORTS.append (GLOBAL_PORT)
            #print self.PORTS

    def getports(self):
        return self.PORTS




    def getData(self):
        data = [[] for i in range(2)]
        for i,GLOBAL_PORT in enumerate(self.PORTS):
            try:
                print GLOBAL_PORT
                GLOBAL_PORT.flushInput();GLOBAL_PORT.flushOutput()
                GLOBAL_PORT.write('.')

                startMarker = ord("<")
                endMarker = ord(">")

                ck = ""
                x = "z" # any value that is not an end- or startMarker
                byteCount = -1 # to allow for the fact that the last increment will be one too many

                # wait for the start character
                while  ord(x) != startMarker: 
                    x = GLOBAL_PORT.read()

                # save data until the end marker is found
                while ord(x) != endMarker:
                    if ord(x) != startMarker:
                        ck = ck + x 
                        byteCount += 1
                    x = GLOBAL_PORT.read()
                "print data received = ", ck
            except:
                ck = "Nodata:0;Nodata2:0"
            data[i].append(ck)
        return data



class Calculate_Diameter(object):

    def __init__(self,image,num_lines, multiplication_factor, ROI):
        image = image
        self.timeit2 = TimeIt2()
        
        #print "working out the diameter"
        
    def calc(self,image,num_lines, multiplication_factor, ROI):
    # Set up some parameters
        global delta_height, scale_factor
        ny,nx = image.shape

        start_x, start_y = ROI[0]
        end_x, end_y = ROI[1]

        #print "END"
        #print end_x,end_y
        #print nx,ny
        number,navg = num_lines,20
        if end_x == nx and end_y == ny:
            start = int(np.floor(ny/(number+1)))
            diff = int(np.floor(ny/(number+1)))
            end = (number+1)*diff
            thresh = 0
        else:
            start_y = int((start_y - delta_height)/scale_factor)
            end_y = int((end_y - delta_height)/scale_factor)
            ny = end_y - start_y
            diff = int(np.floor(ny/(number+1)))
            start = start_y + diff
            end = int(start_y + (number+1)*diff)
            thresh = 0

    # The multiplication factor
        scale = multiplication_factor
    # Slice the image
        data = [np.average(image[y-int(navg/2):y+int(navg/2),:], axis=0) for y in  range(start,end,diff)]
        data2 = np.array(data)
    #Smooth the datums
        window = np.ones(21,'d')
        smoothed = [np.convolve(window / window.sum(), sig, mode = 'same') for sig in data2]
    #Differentiate the datums

    # This if the original function used to differentiate
        #with self.timeit2("Differentiate 1"): 
        #    ddts = [VTutils.diff(sig, 1) for sig in smoothed]
    # But this one is much faster!
        ddts = [VTutils.diff2(sig, 1) for sig in smoothed]
        window = np.ones(11,'d')
        ddts = [np.convolve(window / window.sum(), sig, mode = 'same') for sig in ddts]
        #with self.timeit2("Differentiate 3"): 
        #    ddts = [VTutils.diff3(sig, 1) for sig in smoothed]
    # Loop through each derivative 
        outer_diameters1,outer_diameters2,inner_diameters1,inner_diameters2,OD,ID, ODS_flag,IDS_flag,ODlist, IDlist = VTutils.process_ddts(ddts,thresh,nx,scale)
    #Return the data
        return(outer_diameters1,outer_diameters2,inner_diameters1,inner_diameters2,OD,ID,start,diff,ODS_flag,IDS_flag,ODlist, IDlist)



##################################################
## Threaded client, check if there are images and process the images in seperate threads
##################################################
class ThreadedClient:
    """
    Launch the main part of the GUI and the worker thread. periodicCall and
    endApplication could reside in the GUI part, but putting them here
    means that you have all the thread controls in a single place.
    """
    def __init__(self, master):
        """
        Start the GUI and the asynchronous threads. We are in the main
        (original) thread of the application, which will later be used by
        the GUI as well. We spawn a new thread for the worker (I/O).
        """
        #threading.Thread.daemon = True # Make sure the thread terminates on exit
        self.master = master
        # Create the queue
        self.queue = Queue.Queue(  )
        # Set up the GUI part
        self.gui = GuiPart(master, self.queue, self.endApplication)

        # Set up the thread to do asynchronous I/O
        # More threads can also be created and used, if necessary
        self.running = 1
        self.thread1 = threading.Thread(target=self.workerThread1)
        #self.thread1.deamon = True
        self.thread1.start(  )

        # Start the periodic call in the GUI to check if the queue contains
        # anything
        self.outers = []
        self.inners = []
        self.timelist = []
        self.periodicCall(  )

        self.acqrate = None

    def periodicCall(self):
        """
        Check every 10 ms if there is something new in the queue.
        """
        if self.running:
            self.gui.processIncoming( self.timelist, self.inners, self.outers )
            self.master.after(10, self.periodicCall)
        if not self.running:
            # This is the brutal stop of the system. You may want to do
            # some cleanup before actually shutting it down.
            sys.exit(1)
            

    def workerThread1(self):
        """
        This is where we handle the asynchronous I/O. For example, it may be
        a 'select(  )'. One important thing to remember is that the thread has
        to yield control pretty regularly, by select or otherwise.
        """
        self.timenow = 0
        while self.running:
            if(self.queue.empty()):
                try: # Catch exception on closing the window!
                # Check if there is an image in the buffer, or an image acuisition in progress
                    #print "image remaining count = ", mmc.getRemainingImageCount()
                    if (mmc.getRemainingImageCount() > 0 or mmc.isSequenceRunning()):
                    #Check if there is an image in the buffer
                        #if mmc.getRemainingImageCount > 1:
                        #    mmc.clearCircularBuffer()
                        if mmc.getRemainingImageCount() > 0:
                            
                            timenow = time.time() - start_time #Get the time
                            global acqrate
                            acqrate = 1/(timenow - self.timenow)
                            self.timenow = timenow
                            img = mmc.popNextImage() #mmc.getLastImage()## Get the next image. 

                            # Binning
                            '''
                            new_shape = tuple(ti/2 for ti in img.shape)
                            def rebin(arr, new_shape):
                                #"""Rebin 2D array arr to shape new_shape by averaging."""
                                shape = (int(new_shape[0]), int(arr.shape[0] // new_shape[0]),int(new_shape[1]), int(arr.shape[1] // new_shape[1]))
                                return arr.reshape(shape).mean(-1).mean(1).astype(int)
                            img = rebin(img, new_shape)
                            img = np.array(img, dtype=np.uint8)
                            '''

                            self.queue.put(img) # Put the image in the queue

                            # Save raw image:
                            if self.gui.toolbar.record_is_checked.get() == 1:# and self.count%self.rec_interval == 0:
                                timenow2 = int(timenow)
                                directory = os.path.join(head, 'RawTiff\\')
                                if not os.path.exists(directory):
                                    os.makedirs(directory)
                                gfxPath = os.path.join(directory, '%s_f=%s.tiff' % (os.path.splitext(tail)[0],str(self.gui.count).zfill(6))) 
                                skimage.io.imsave(gfxPath, img)

                except:
                    pass
    """
     This is a function that cleans up on
    exit. It should kill all processes properly.
    """
    def endApplication(self):
        try:
            mmc.stopSequenceAcquisition() # stop uManager acquisition
            mmc.reset() # reset uManager
        except:
            pass
        self.running = 0
        #sys.exit()
        root.quit()
        root.destroy()

##################################################
## Splash screen
##################################################
rootsplash = tk.Tk()
rootsplash.overrideredirect(True)
width, height = rootsplash.winfo_screenwidth(), rootsplash.winfo_screenheight()

#print "Screen height is = ", height
#print "Screen width is = ", width

#Load in the splash screen image
image_file = "Splash.gif" 
image = Image.open(image_file)
image2 = PhotoImage(file=image_file)

# Scale to half screen, centered
imagewidth, imageheight = image2.width(), image2.height()
newimagewidth, newimageheight = int(np.floor(width*0.5)),  int(np.floor(height*0.5))
image = image.resize((newimagewidth,newimageheight), Image.ANTIALIAS)
image = ImageTk.PhotoImage(image)

# Create and show for 3 seconds
rootsplash.geometry('%dx%d+%d+%d' % (newimagewidth, newimageheight, width/2 - newimagewidth/2, height/2 - newimageheight/2))
canvas = tk.Canvas(rootsplash, height=height, width=width, bg="darkgrey")
canvas.create_image(width/2 - newimagewidth/2, height/2 - newimageheight/2, image=image)
canvas.pack()
rootsplash.after(3000, rootsplash.destroy)
rootsplash.mainloop()


##################################################
## Main application loop
##################################################

if __name__ == "__main__":
    global start_time
    start_time=time.time()
    
# Set up the camera
    mmc = MMCorePy.CMMCore()

# Create the main window
    rand = random.Random(  )
    root = tk.Tk(  )
    root.iconbitmap('ICON.ICO')
    root.attributes('-topmost',True)
    root.after_idle(root.attributes,'-topmost',False)
    root.wm_title("VasoTracker") #Makes the title that will appear in the top left
    root.state("zoomed")
    root.resizable(0,0) # Remove ability to resize
    #w, h = root.winfo_screenwidth(), root.winfo_screenheight() # Can set the window size using the screenwidth if we wish
    #root.geometry("%dx%d+0+0" % (w, h))
    #root.overrideredirect(1) #hides max min buttons and the big x
    #root.wm_attributes('-fullscreen', 1)
# Go go go!
    client = ThreadedClient(root)
    root.mainloop(  )


