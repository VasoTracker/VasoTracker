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
## Copyright (c) 2020, VasoTracker
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
## Version: 1.3.0
## Maintainer: Calum Wilson
## Email: vasotracker@gmail.com
## Status: Production
## Last updated: 20200816
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
from ConfigParser import SafeConfigParser
from collections import deque
from math import hypot

# Import Vasotracker functions
import VTutils
from VT_Arduino import Arduino
from VT_Diameter import Calculate_Diameter

# Add MicroManager to path
import sys
MM_PATH = os.path.join('C:', os.path.sep, 'Program Files','Micro-Manager-1.4')
sys.path.append(MM_PATH)
os.environ['PATH'] = MM_PATH + ';' + os.environ['PATH']
import MMCorePy

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
from matplotlib.transforms import Bbox

# Import nidaqmx
import nidaqmx
import PyDAQmx
from PyDAQmx import Task


#Disable garbage collection
import gc
gc.disable()


##################################################
## GUI main application 
##################################################
class GuiPart(tk.Frame):

    #Initialisation function
    def __init__(self, master, queue,endCommand, *args, **kwargs):
        tk.Frame.__init__(self, *args, **kwargs)
        self.master = master #this is root
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

    # Arduino       
        self.Arduino = Arduino(self)
        self.ports = self.Arduino.getports()
    
    # Timing functions
        self.timeit = TimeIt()
        self.timeit2 = TimeIt2()

    # Load the config file
        parser = SafeConfigParser()
        parser.read('default_settings.ini')

    # Initial Values
        self.OD = None
        self.ID = None

    # Scale setting
        try:
            self.multiplication_factor = float(parser.get('Acquisition', 'Scale'))# 1 # Scale setting
        except:
            self.multiplication_factor = 1
        self.init_multiplication_factor = self.multiplication_factor

    # Exposure setting
        try:
            self.exposure = float(parser.get('Acquisition', 'Exposure'))# 1 # Scale setting
        except:
            self.exposure = 250
        self.init_exposure = self.exposure

    # Pixel clock setting
        global pix_clock
        try:
            pix_clock = float(parser.get('Acquisition', 'Pixel_clock'))# 1 # Scale setting
        except:
            pix_clock = 10
        self.pix_clock = pix_clock
        self.init_pix_clock = pix_clock

    #  Minimum frame rate setting
        global Force_min_interval 
        try:
            Force_min_interval  = float(parser.get('Acquisition', 'Force_min_interval'))# 1 # Scale setting
        except:
            Force_min_interval  = 0.250
        self.Force_min_interval  = Force_min_interval 

    # Minimum frame rate setting
        global Force_faster_interval  
        try:
            Force_faster_interval   = float(parser.get('Acquisition', 'Force_min_interval'))# 1 # Scale setting
        except:
            Force_faster_interval   = 0.125
        self.Force_faster_interval   = Force_faster_interval  

    # Record interval setting
        global rec_interval
        try:
            rec_interval = float(parser.get('Acquisition', 'Recording_interval'))# 1 # Scale setting
        except:
            rec_interval = 240
        self.rec_interval = rec_interval
        self.init_rec_interval = rec_interval

    # Data acquisition lines setting
        try:
            self.num_lines = float(parser.get('Analysis', '#_of_lines'))# 1 # Scale setting
        except:
            self.num_lines = 10

     # Smoothing setting
        try:
            self.smooth_factor = int(parser.get('Analysis', 'Smooth'))# 1 # Scale setting
        except:
            self.smooth_factor = 21

     # Set pressure setting
        try:
            self.set_pressure = int(parser.get('Pressure_Control', 'default_pressure'))# 1 # Scale setting
            self.pressure_time_interval = int(parser.get('Pressure_Control', 'time_interval')) #minute
            self.start_presure = int(parser.get('Pressure_Control', 'start_presure')) # mmHg
            self.stop_pressure = int(parser.get('Pressure_Control', 'stop_pressure')) # mmHg
            self.pressure_interval = int(parser.get('Pressure_Control', 'pressure_interval'))  # mmHg
        
        except:
            self.set_pressure = 0
            self.pressure_time_interval = 1
            self.start_presure = 20
            self.stop_pressure = 200
            self.pressure_interval = 20

    # Integration setting
        try:
            self.integration_factor = int(parser.get('Analysis', 'Integration'))# 1 # Scale setting
        except:
            self.integration_factor = 20

    # Threshold setting
        try:
            self.thresh_factor = float(parser.get('Analysis', 'Threshold'))# 1 # Scale setting
        except:
            self.thresh_factor = 3.5

    # Graph settings
        try:
            self.x_min_default = int(parser.get('Graph axes', 'x-min'))
            self.x_max_default = int(parser.get('Graph axes', 'x-max'))
            self.y_min_default = int(parser.get('Graph axes', 'y-min'))
            self.y_min_default2 = self.y_min_default
            self.y_max_default = int(parser.get('Graph axes', 'y-max'))
            self.y_max_default2 = self.y_max_default
        except:
            self.x_min_default = -600
            self.x_max_default = 0
            self.y_min_default = 0
            self.y_min_default2 = self.y_min_default
            self.y_max_default = 250
            self.y_max_default2 = self.y_max_default

    # Memory settings
        try:
            self.n_plot_points = float(parser.get('Memory', 'n_plot_points '))# 1 # Scale setting
        except:
            self.n_plot_points = 1200 #300
        
        try:
            self.n_data_points = float(parser.get('Memory', 'n_data_points '))# 1 # Scale setting
        except:
            self.n_data_points = 15000 #300


    # Acquisition rate setting
        self.acq_rate = np.nan

        self.initUI(self.endApplication)

    # Open the csv file and then clear it
        f = open(self.filename.name, "w+")
        f.close()

    # Add the headers
        with open((self.filename.name), 'ab') as f:
            w=csv.writer(f, quoting=csv.QUOTE_ALL)
            w.writerow(("Time","Outer Diameter", "Inner Diameter", 'Temperature (oC)', 'Pressure 1 (mmHg)', 'Pressure 2 (mmHg)', 'Avg Pressure (mmHg)', 'Caliper length'))

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

    # Add the file for the outerdiameter flags
        self.flag_file1 = self.txt_file + ' - ODFlags' + '.csv'
        with open((self.flag_file1), 'w+') as g:
            v=csv.writer(g, quoting=csv.QUOTE_ALL)
            column_headings = 'Time (s)', 'Profile 1', 'Profile 2', "Profile 3", "..."
            v.writerow(column_headings)

    # Add the file for the outerdiameter flags
        self.flag_file2 = self.txt_file + ' - IDFlags' + '.csv'
        with open((self.flag_file2), 'w+') as g:
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

    def writeToFile4(self,data):
        with open((self.flag_file1), 'ab') as f:
            w=csv.writer(f, quoting=csv.QUOTE_ALL)
            w.writerow(data)

    def writeToFile5(self,data):
        with open((self.flag_file2), 'ab') as f:
            w=csv.writer(f, quoting=csv.QUOTE_ALL)
            w.writerow(data)

    # Function for closing down
    def close_app(self):
        if tmb.askokcancel("Close", "Are you sure...?"):
            self.endApplication()

    def gotouserguide(self):
        tmb.showinfo("Hope you are connected to the internet", "Opening in your browser...")
        webbrowser.open_new(r"http://www.vasotracker.com/sdm_downloads/vasotracker-acquisition-software-manual/")

    def gotocontact(self):
        tmb.showinfo("We would hate to hear from you", "Because it probably means there is a problem. Despite our feelings, we will do our best to help. Our contact details should pop up in your web browser...")
        webbrowser.open_new(r"http://www.vasotracker.com/about/contact-us/")

    def launchabout(self):
        webbrowser.open_new(r"http://www.vasotracker.com/about/")

    def launchupdate(self):
        tmb.showinfo("We are not that clever", "So you will have to see if their is an update to download yourself... the download page should pop up in your web browser...")
        webbrowser.open_new(r"http://www.vasotracker.com/downloads/acquisition-software/")

    def launchsnake(self):
        tmb.showinfo("We did warn you.", "Any hope of this being a productive day have just went out the window...")
        import spaceinvaders

    def launchmusic(self):
        tmb.showinfo("We like dancing in the shower", "Whether in the lab or in the shower, these songs make us boogie...")
        webbrowser.open_new(r"https://open.spotify.com/playlist/5isnlNKb6Xtm975J9rxxT0?si=U5qpBEeHTKW9S0mLe70rKQ")


    # Function for defining an average checkbox ## Shouldbe in toolbar!
    def average_checkbox(self, window, text):
        avg_checkbox = ttk.Checkbutton(window, text=text)
        avg_checkbox.grid(row=0, columnspan=4, padx=3, pady=3)

    # Second Function for initialising the GUI
    def initUI(self,endCommand):

    # make Esc exit the program
        self.master.bind('<Escape>', lambda e: endCommand)

    # make the top right close button minimize (iconify) the main window
        self.master.protocol("WM_DELETE_WINDOW", self.close_app)

    # create a menu bar with an Exit command
        menubar = tk.Menu(self.master)
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="Exit", command=self.close_app)

    # Create a help menu
        self.helpmenu = tk.Menu(menubar, tearoff=0)
        self.helpmenu.add_command(label='Boogie woogie', command = self.launchmusic)
        self.helpmenu.add_separator()
        self.helpmenu.add_command(label='User Guide', command = self.gotouserguide)
        self.helpmenu.add_command(label='Contact', command = self.gotocontact)
        self.helpmenu.add_command(label='About', command = self.launchabout)
        self.helpmenu.add_command(label='Update', command = self.launchupdate)
        self.helpmenu.add_separator()
        self.helpmenu.add_command(label='Do not click here...', command = self.launchsnake)

        menubar.add_cascade(label="File", menu=filemenu)
        menubar.add_cascade(label="Help", menu=self.helpmenu)
        self.master.config(menu=menubar)
        self.pack(fill=BOTH, expand=1)

    # Make the toolbar along the top
        self.toolbar = ToolBar(self)#ttk.Frame(root, height=150)
        self.toolbar.grid(row=0, column=0,rowspan=1,columnspan=4, padx=ypadding, pady=ypadding, sticky=E+S+W+N)
        self.toolbar.grid(sticky='nswe')
        self.toolbar.rowconfigure(0, weight=1)
        self.toolbar.columnconfigure(0, weight=1)

    # Make the status bar along the bottom
        def callback(event):
            webbrowser.open_new(r"https://doi.org/10.3389/fphys.2019.00099")
        self.status_bar = ttk.Label(text = 'Thank you for using VasoTracker. To support us, please cite VasoTracker (click here for the paper).', relief=SUNKEN, anchor='w')
        
        self.status_bar.pack(side=BOTTOM, fill=X)
        self.status_bar.bind("<Button-1>", callback)

    # Make the graph frame
        self.graphframe = GraphFrame(self)
        self.graphframe.grid(row=1, column=0, rowspan=4,columnspan=2, padx=ypadding, pady=ypadding, sticky=E+S+W+N)
        self.graphframe.grid(sticky='nswe')
 
    # Make the table frame
        self.tableframe = TableFrame(self)
        self.tableframe.grid(row=1, column=3,rowspan=1,columnspan=1, padx=ypadding, pady=ypadding, sticky=E+S+W+N)
        self.tableframe.grid(sticky='nwe')

    #Update everything so that the frames are all the correct size. We need to do this so we can size the graph/image before we place them.
        self.toolbar.update()
        self.status_bar.update()
        self.tableframe.update()
        self.toolbar.update()

    # Make the Camera Frame bottom right
        self.cameraframe = CameraFrame(self)
        self.cameraframe.grid(row=2, column=3,rowspan=1,columnspan=2, padx=ypadding, pady=ypadding, sticky=E+S+W+N)
        self.cameraframe.grid(sticky='nswe')
        #print "this is the height: ", self.graphframe.winfo_height()
        #print "this is the width: ", self.graphframe.winfo_width()
        
        # Now set up the graph
        self.graphframe.mainWidgets() 

    # Count function for reading in with FakeCamera
        self.count = 0   
    # Count function for resizing on first image acquisition
        self.count2 = 0  
    # Count function for pressure protocol
        self.count3 = 0    
    # Time Multiplier for pressure protocol
        self.multiplier = 1

    # For storing data
        self.P1 = np.nan
        self.P2 = np.nan
        self.T = np.nan
        self.start_time = 0
        self.pressure_start_time = 0
        self.prev_time = 0
        self.timelist = []
        self.outers = []
        self.inners = []
        self.delta_i = 1
        self.delta_i2 = 1

    # Function for processing the Arduino data
    def sortdata(self,temppres):
    
        # Initialize variables
        temp = np.nan
        pres1 = np.nan
        pres2 = np.nan

        # Loop through the data from the two Arduinos (tempres contains dummy data if < 2 connected)
        for data in temppres:
            if len(data) > 0:

                # Split the data by Arduino
                val = data[0].strip('\n\r').split(';')
                val = val[:-1]
                val = [el.split(':') for el in val]

                # Get the temperature value
                if val[0][0] == "T1":
                    try:
                        temp = float(val[0][1])
                    except:

                        temp = np.nan
                    #set_temp = float(val[1][1])

                # Get the pressure value
                elif val[0][0] == "P1":
                    try:
                        pres1 = float(val[0][1])
                        pres2 = float(val[1][1])
                    except:
                        pres1 = np.nan
                        pres2 = np.nan

                else:
                    pass
            else:
                pass

        return pres1,pres2,temp

    # This function will process all of the incoming images
    def processIncoming(self):
        """Handle all messages currently in the queue, if any."""
        while self.queue.qsize(  ):
        #print "Queue size = ", self.queue.qsize(  )
        #with self.timeit2("Total"):  # time for optimisation
            try:
            #Get the image
                msg = self.queue.get(0)
                got_image = True
            except:
                got_image = False

            if got_image == True:

            # On first loop, reset the time
                if self.toolbar.record_flag:
                    if self.count == 0:
                        self.start_time=time.time()
                    # This is for loading in the example data!
                    try:
                        mmc.setProperty('Focus', "Position", self.count%500)
                    except:
                        pass


                    # Check if this is the first loop through with pressure protocol flag set
                    if self.toolbar.pressure_protocol_flag:
                        if self.count3 == 0:
                            print "This done first time round"
                            self.set_pressure = self.start_presure
                            self.toolbar.set_pressure_contents.set(self.set_pressure)
                            self.toolbar.update_set_pressure(1, table=False)

                            self.pressure_start_time=time.time()


                        # Add line to the table
                            self.tableframe.table_text_entry.set("START     Pressure protocol (" + str(self.pressure_interval) + "mmHg/" + str(self.pressure_time_interval) +"s):") 
                            self.tableframe.add_row()
                        # Add line to the table
                            self.tableframe.table_text_entry.set(str(self.set_pressure) + " mmHg")
                            self.tableframe.add_row()

                        self.pressure_timenow = int(time.time() - self.pressure_start_time+1)
                        print "time now = ", time.time()
                        print "Pressure start time = ", self.pressure_start_time
                        print "Pressure time now = ", self.pressure_timenow

                        # Increase pressure when time interval elapses
                        
                        self.seconds_interval = int(self.pressure_time_interval*self.multiplier)
                        print "seconds_interval = ", self.seconds_interval
                        self.count3 += 1
                        if self.pressure_timenow%self.seconds_interval == 0:
                            
                            # End on last pressure value
                            if self.set_pressure < self.stop_pressure:
                                self.set_pressure = self.set_pressure + self.pressure_interval
                                self.toolbar.set_pressure_contents.set(self.set_pressure)
                                self.toolbar.update_set_pressure(1, table=False)
                                self.multiplier += 1

                             # Add line to the table
                                self.tableframe.table_text_entry.set(str(self.set_pressure) + " mmHg")
                                self.tableframe.add_row()
                                

                            elif self.set_pressure == self.stop_pressure:
                                self.set_pressure = self.start_presure
                                self.toolbar.set_pressure_contents.set(self.set_pressure)
                                self.toolbar.update_set_pressure(1, table=False)

                                self.toolbar.stop_pressure_protocol()

                            # Add line to the table
                                self.tableframe.table_text_entry.set("END Pressure protocol")
                                self.tableframe.add_row()
                            # Add line to the table
                                self.tableframe.table_text_entry.set(str(self.set_pressure) + " mmHg")
                                self.tableframe.add_row()

                            print "the new pressure is thisL :", self.set_pressure
                        
                            '''
                            self.set_pressure = 0
                            self.time_interval = 1
                            self.start_presure = 20
                            self.stop_pressure = 200
                            self.pressure_interval = 20
                            '''
                        


                # Get the arduino data
                    #with self.timeit("Get Arduino"): # time for optimisation
                    temppres = self.Arduino.getData()
                    self.P1,self.P2,self.T = self.sortdata(temppres)

                # Save raw image:
                    if self.toolbar.record_is_checked.get() == 1 and self.count%self.rec_interval == 0:
                        directory = os.path.join(head, self.filename.name[:-4]+'\\RawTiff\\')
                        
                        if not os.path.exists(directory):
                            os.makedirs(directory)
                        else:
                            pass
                        gfxPath = os.path.join(directory, '%s_f=%s.tiff' % (os.path.splitext(tail)[0],str(int(self.count/self.rec_interval)).zfill(6))) 
                        skimage.io.imsave(gfxPath, msg)
                    else:
                        pass

                # Process the acquired image
                    self.timenow = time.time() - self.start_time #Get the time

                #Get acquisition rate
                    try:
                        self.acq_rate = 1/(self.timenow - self.prev_time)
                    except:
                        pass
                    self.prev_time = self.timenow

                # Get ROI
                    if self.toolbar.ROI_is_checked.get() == 1: # Get ROI
                        self.ROI = ((self.cameraframe.start_x,self.cameraframe.start_y), (self.cameraframe.end_x, self.cameraframe.end_y))
                    else: # Set ROI to image bounds
                        self.ROI = ((0,0),(int(msg.shape[1]),int(msg.shape[0])) )    

                # Calculate diameter    
                    self.diam = Calculate_Diameter(self,self.num_lines,self.multiplication_factor,self.smooth_factor, self.thresh_factor,
                                                        self.integration_factor,self.ROI, self.toolbar.ID_is_checked, self.toolbar.org_is_checked)

                    #with self.timeit("Calculate diameter"): # time for optimisation
                    outer_diameters1,outer_diameters2,inner_diameters1,inner_diameters2,start,diff, ODS_flag,IDS_flag,ODlist,IDlist = self.diam.calc(msg,  self.cameraframe.delta_height, self.cameraframe.delta_width, self.cameraframe.scale_factor)

                    params = outer_diameters1,outer_diameters2,inner_diameters1,inner_diameters2,start,diff,ODS_flag,IDS_flag, self.ROI
                    
                    #with self.timeit("process queue!"): # time for optimisation
                    self.cameraframe.process_queue(params,msg,self.count2)
                    
                    #with self.timeit("append"):

                    # Only add every delta_i data point to the lists
                    if self.count%self.delta_i == 0:
                        self.timelist.append(self.timenow)
                        self.outers.append(self.diam.OD) # Full list
                        self.inners.append(self.diam.ID) # Full list
                    else:
                        pass
                    
                    # When we reach the list length limit, subsample the data. (And only add every delta_i data point to the list above)
                    self.i = int(len(self.timelist))
                    if self.i == self.n_data_points :
                        self.delta_i *= 2
                        # frequency of plotted points
                        self.timelist = self.timelist[0::2]
                        self.outers = self.outers[0::2]
                        self.inners = self.inners[0::2]
                    else:
                        pass
                    
                # Subtract off the latest time point, so that the current time is t = 0
                    xdata = map(lambda x: x - self.timelist[-1], self.timelist)

                # Get the xdata points that fit within the axis limits
                    xdata3 = filter(lambda x: x >= xdata[-1]-abs(self.toolbar.xlims[0]), xdata)
                    xdata4 = filter(lambda x: x >= xdata[-1]-abs(self.toolbar.xlims[0]), xdata)

                    # Get the corresponding ydata points
                    ydata1 = self.outers[len(self.outers)-len(xdata3)::]#[0::10]
                    ydata2 = self.inners[len(self.outers)-len(xdata4)::]#[0::10]    

                    # Subsample plotted dat
                    self.i2 = int(len(xdata3))
                        
                    if self.i2 > self.n_plot_points :
                        self.delta_i2 = np.ceil(self.i2/self.n_plot_points)
                    else:
                        self.delta_i2 = 1
                    
                    xdata3 = xdata3[0::int(self.delta_i2)]
                    ydata1 = ydata1[0::int(self.delta_i2)]
                    ydata2 = ydata2[0::int(self.delta_i2)]

                    #with self.timeit("plot the graph"): # time for optimisation
                    self.graphframe.plot(xdata3,ydata1,ydata2,self.toolbar.xlims, self.toolbar.ylims, self.toolbar.ylims2)    
                    self.count += 1


                    # Update the tkinter widgets
                    self.toolbar.update_acq_rate(self.acq_rate)
                    self.toolbar.update_time(self.timenow)
                    self.toolbar.update_temp(self.T) #### CHANGE to T
                    self.toolbar.update_pressure(self.P1,self.P2, (self.P1+self.P2)/2)
                    self.toolbar.update_diam(self.diam.OD,self.diam.ID)
  
                    # Write data to file
                    savedata = self.timenow,self.diam.OD,self.diam.ID, self.T, self.P1, self.P2, (self.P1+self.P2)/2, self.cameraframe.calibrated_caliper_distance
                    savedata2 = [self.timenow]+ODlist
                    savedata3 = [self.timenow]+IDlist
                    savedata4 = [self.timenow]+ODS_flag
                    savedata5 = [self.timenow]+IDS_flag
                    self.writeToFile(savedata)
                    self.writeToFile2(savedata2)
                    self.writeToFile3(savedata3)
                    self.writeToFile4(savedata4)
                    self.writeToFile5(savedata5)
                    
                    #Need to access the outer diameter from the toolbar
                    self.OD = self.diam.OD
                    self.ID = self.diam.ID
                    
                else:
                    params = 0,0,0,0,0,0,0,0,0
                    self.cameraframe.process_queue(params,msg,self.count2)  
                self.count2 += 1
                

            else:
                pass


##################################################
## Camera setup
##################################################
class setCamera(object):
    def __init__(self,parent, camera_label):
        self.parent = parent
        camera_label = camera_label
        self.DEVICE = None

        # Factors for scaling ROI to original image (which is scaled to fit canvas)
        self.delta_width = 0
        self.delta_height = 0
        self.scale_factor = 1

    def set_exp(self,exposure):
        mmc.setExposure(exposure)
        return
    def set_pix_clock(self,pix_clock):
        mmc.setProperty(self.device[0], 'PixelClockMHz', pix_clock)
        return

    def set(self, camera_label):
        # Set up the camera
        global pix_clock
        mmc.reset()
        mmc.enableStderrLog(False)
        mmc.enableDebugLog(False)
        mmc.setCircularBufferMemoryFootprint(100)# (in case of memory problems)

        if camera_label == "Thorlabs":
            try:
                DEVICE = ["ThorCam","ThorlabsUSBCamera","ThorCam"] #camera properties - micromanager creates these in a file
                self.device = DEVICE
                mmc.loadDevice(*DEVICE)
                mmc.initializeDevice(DEVICE[0])
                mmc.setCameraDevice(DEVICE[0])
                #mmc.setProperty(DEVICE[0], 'Binning', 2)
                mmc.setProperty(DEVICE[0], 'HardwareGain', 1)
                mmc.setProperty(DEVICE[0], 'PixelClockMHz', pix_clock)#5
                mmc.setProperty(DEVICE[0], 'PixelType', '8bit')
                mmc.setExposure(self.parent.parent.exposure)
            except:
                tmb.showinfo("Warning", "Cannot connect to camera!")

        if camera_label == "OpenCV":
            try:
                mmc.loadSystemConfiguration('OpenCV.cfg')
                mmc.setProperty('OpenCVgrabber', 'PixelType', '8bit')
                mmc.setExposure(self.parent.parent.exposure)
            except:
                tmb.showinfo("Warning", "Cannot connect to camera!")

        if camera_label == "uManagerCam":
            config_loaded = False
            try:
                mmc.loadSystemConfiguration('MMConfig.cfg')
                config_loaded = True
            except:
                tmb.showinfo("Warning", "MMConfig.cfg not found in home directory!")

            if config_loaded:
                camera = mmc.getLoadedDevicesOfType(2)[0]
                mmc.getDevicePropertyNames(camera) # camera_properties = 
                mmc.setProperty(mmc.getLoadedDevicesOfType(2)[0], 'PixelType', '8bit')
                mmc.setExposure(self.parent.parent.exposure)


        elif camera_label == "FakeCamera":
                DEVICE = ['Camera', 'FakeCamera', 'FakeCamera'] #camera properties - micromanager creates these in a file
                mmc.loadDevice(*DEVICE)
                mmc.initializeDevice(DEVICE[0])
                mmc.setCameraDevice(DEVICE[0])
                mmc.setExposure(self.parent.parent.exposure)
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


##################################################
## Main toolbar
##################################################
class ToolBar(tk.Frame):
    def __init__(self,parent):
        tk.Frame.__init__(self, parent, height = 150)#,  width=250, highlightthickness=2, highlightbackground="#111")
        self.parent = parent
        self.caliper_length = np.nan
        self.mainWidgets()
        self.set_camera = setCamera(self,self.parent )
        self.ref_OD = None
        self.task = Task()

    #Functions that do things in the toolbar
    def update_temp(self, temp):
        # Updates the temperature widget
        tempstring = str(round(temp,2))
        self.temp_contents.set(tempstring)

    def update_pressure(self, P1,P2,PAvg):
        # Update average pressure
        pressurestring = str(round(PAvg,2))
        self.pressure_contents.set(pressurestring)

    def update_diam(self, OD, ID):
        # Update outer diameter
        OD_string = str(round(OD,2))
        self.outdiam_contents.set(OD_string)
        try:
            OD_pcnt_string = str(round(((OD/self.parent.toolbar.ref_OD)*100),2))
            self.outdiam_pcnt_contents.set(OD_pcnt_string)
        except:
            pass
        
        # Update inner diameter
        ID_string = str(round(ID,2))
        self.indiam_contents.set(ID_string)
    
    def update_time(self, time):
        #Update the time widget
        timestring = str(datetime.timedelta(seconds=time))[:-4]
        self.time_contents.set(timestring)

    def update_acq_rate(self, acqrate):
        #Update the acq_rate widget
        self.acq_rate_contents.set(str(round(acqrate,2)))
        
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
            if exp < 100:
                tmb.showinfo("Warning", "Except for ThorCam, we recommend an exposure between 100 ms and 500ms")
            self.parent.exposure = int(exp)
            prevcontents = exp
            exposure = exp
        except: 
            self.exposure_entry.delete(0, 'end')
            self.exposure_entry.insert('0', prevcontents)
            exposure = prevcontents

        self.set_camera.set_exp(exposure)
        self.exposure_entry.delete(0, 'end')
        self.exposure_entry.insert('0', mmc.getExposure()) 

    def update_pix_clock(self,event):
            global pix_clock_prevcontents, pix_clock 
            try:
            # Check if the exposure is within a suitable range
                pix_clock = self.pix_clock_contents.get()
                self.pix_clock_entry.delete(0, 'end')
                self.pix_clock_entry.insert('0', pix_clock) 
                self.set_camera.set_pix_clock(pix_clock)
                self.parent.pix_clock = int(pix_clock)
                pix_clock_prevcontents = pix_clock
                pix_clock = pix_clock
            except: 
                self.pix_clock_entry.delete(0, 'end')
                self.pix_clock_entry.insert('0', pix_clock_prevcontents)
                pix_clock = prevcontents

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
            num_lines_prevcontents = num_lines
            num_lines = num_lines
            
        except: 
            self.num_lines_entry.delete(0, 'end')
            self.num_lines_entry.insert('0', num_lines_prevcontents)
            num_lines = num_lines_prevcontents

    def update_scale(self,event):
        try:
        # Check if the exposure is within a suitable range
            scale = self.scale_contents.get()
            self.scale_entry.delete(0, 'end')
            self.scale_entry.insert('0', scale) 
            self.parent.multiplication_factor = scale
            self.scale_prevcontents = scale
            
        except:
            self.scale_entry.delete(0, 'end')
            self.scale_entry.insert('0', self.scale_prevcontents)
            self.parent.multiplication_factor = self.scale_prevcontents

    def update_smooth(self,event):
        #global smooth_prevcontents, smooth_factor
        try:
        # Check if the exposure is within a suitable range
            smooth = self.smooth_contents.get()
            self.smooth_entry.delete(0, 'end')
            self.smooth_entry.insert('0', smooth) 
            self.parent.smooth_factor = smooth
            self.smooth_prevcontents = smooth
            try:
                self.parent.videoframe.update_image(self.parent.videoframe.slider.get())
            except:
                pass
        except:
            self.smooth_entry.delete(0, 'end')
            self.smooth_entry.insert('0', self.smooth_prevcontents)
            self.parent.smooth_factor = smooth_prevcontents

    def update_integration(self,event):
        try:
        # Check if the exposure is within a suitable range
            integration = self.integration_contents.get()
            if integration < 5:
                integration = 5
            elif integration > 50:
                integration = 50
            self.integration_entry.delete(0, 'end')
            self.integration_entry.insert('0', integration) 
            self.parent.integration_factor = integration
            self.integration_prevcontents = integration
            try:
                self.parent.videoframe.update_image(self.parent.videoframe.slider.get())
            except:
                pass
        except:
            self.integration_entry.delete(0, 'end')
            self.integration_entry.insert('0', self.integration_prevcontents)
            self.parent.integration_factor = integration_prevcontents

    def update_thresh(self,event):
        try:
        # Check if the exposure is within a suitable range
            thresh = self.thresh_contents.get()
            self.thresh_entry.delete(0, 'end')
            self.thresh_entry.insert('0', thresh) 
            self.parent.thresh_factor = thresh
            self.thresh_prevcontents = thresh
            try:
                self.parent.videoframe.update_image(self.parent.videoframe.slider.get())
            except:
                pass
        except:
            self.thresh_entry.delete(0, 'end')
            self.thresh_entry.insert('0', self.thresh_prevcontents)
            self.parent.thresh_factor = thresh_prevcontents    

    def update_camera_width(self,width):
        width_string = str(width)
        self.camera_width_contents.set(width_string)

    def update_camera_height(self,height):
        height_string = str(height)
        self.camera_height_contents.set(height_string)

    def update_FOV_width(self,width):
        width_string = str(width)
        self.FOV_width_contents.set(width_string)

    def update_FOV_height(self,height):
        height_string = str(height)
        self.FOV_height_contents.set(height_string)

    def start_acq(self):
        if self.variable.get() == "...":
            tmb.showwarning(title="Warning", message = "You need to select a camera source!")
            self.start_flag = False
        else:

            self.standard_settings.configure(state="disabled")
            self.mm_settings.configure(state="disabled")
            
            self.camera_entry.configure(state="disabled")
            self.scale_entry.configure(state="disabled")
            self.exposure_entry.configure(state="disabled")
            self.pix_clock_entry.configure(state="disabled")
            self.rec_interval_entry.configure(state="disabled")
            self.num_lines_entry.configure(state="disabled")
            self.start_flag = True
            self.record_video_checkBox.configure(state="disabled")
            self.standard_settings.configure(state="disabled")
            
            mmc.startContinuousSequenceAcquisition(0)

            for radio_button in self.FOV_buttons:
                radio_button.configure(state="active")

        return self.start_flag

    def start_pressure_protocol(self):
        if self.start_flag:
            print "this is doing something"
            self.pressure_protocol_flag = True

    def stop_pressure_protocol(self):
        if self.start_flag:
            print "this is doing something"
            self.pressure_protocol_flag = False
            self.parent.multiplier = 1
            self.parent.count3 = 0


    def record_data(self):
        if self.start_flag == True:
            self.record_flag = True
            mmc.clearCircularBuffer()
        return self.record_flag

    def update_calipervalue(self, caliper_length):
        self.caliper_length = caliper_length
        # Update the frames used for calculating data
        self.caliper_contents.set(str(round(caliper_length,2)))

    def update_set_pressure(self,event, table=True):
        try:
        # Check if the exposure is within a suitable range
            set_pressure = self.set_pressure_contents.get()
            set_pressure = max(min(200, set_pressure), 0)

            print "Set pressure is: ", set_pressure

            self.set_pressure_entry.delete(0, 'end')
            self.set_pressure_entry.insert('0', set_pressure) 
            self.parent.set_pressure = set_pressure
            self.set_pressure_prevcontents = set_pressure


            self.task.WriteAnalogScalarF64(1,10.0,set_pressure/100,None)


            # Add line to the table
            if table:
                self.parent.tableframe.table_text_entry.set("Set pressure = " + str(set_pressure) + " mmHg")
                self.parent.tableframe.add_row()

        except:
            self.set_pressure_entry.delete(0, 'end')
            self.set_pressure_entry.insert('0', self.set_pressure_prevcontents)
            self.parent.set_pressure = set_pressure_prevcontents    




    def mainWidgets(self):
        self.toolbarview = ttk.Frame(self.parent.master, relief=RIDGE)
        self.toolbarview.grid(row=2,column=3,rowspan=2,sticky=N+S+E+W, pady=0)

   # Tool bar groups
        source_group = ttk.LabelFrame(self, text='Source', height=150, width=150)
        source_group.pack(side=LEFT, anchor=N, padx=3, fill=Y)

        settings_group = ttk.LabelFrame(self, text='Acquisition Settings', height=150, width=150)
        settings_group.pack(side=LEFT, anchor=N, padx=3, fill=Y)

        ana_settings_group = ttk.LabelFrame(self, text='Analysis Settings', height=150, width=150)
        ana_settings_group.pack(side=LEFT, anchor=N, padx=3, fill=Y)

        outer_diameter_group = ttk.LabelFrame(self, text='Graph', height=150, width=150)
        outer_diameter_group.pack(side=LEFT, anchor=N, padx=3, fill=Y)

        acquisition_group = ttk.LabelFrame(self, text='Data acquisition', height=150, width=150)
        acquisition_group.pack(side=LEFT, anchor=N, padx=3, fill=Y)

        start_group = ttk.LabelFrame(self, text='Start/Stop', height=150, width=150)
        start_group.pack(side=LEFT, anchor=N, padx=3, fill=Y)

        image_size_group = ttk.LabelFrame(self, text='Image dimensions', height=150, width=150)
        image_size_group.pack(side=LEFT, anchor=N, padx=3, fill=Y)

        
        caliper_group = ttk.LabelFrame(self, text='Caliper', height=150, width=150)
        caliper_group.pack(side=LEFT, anchor=N, padx=3, fill=Y)


        servo_group = ttk.LabelFrame(self, text='Pressure control', height=150, width=150)
        servo_group.pack(side=LEFT, anchor=N, padx=3, fill=Y)


        # Camera width box
        camera_width_label = ttk.Label(image_size_group, text = 'Camera width:')
        camera_width_label.grid(row=0, column=0, sticky=E)

        self.camera_width_contents = IntVar()
        self.camera_width_contents.set(0)
        self.camera_width_prevcontents = self.camera_width_contents.get()
        self.camera_width_entry = ttk.Entry(image_size_group, textvariable = self.camera_width_contents,width=10)
        self.camera_width_entry.config(state=DISABLED)
        self.camera_width_entry.grid(row=0, column=1, pady=0)
        self.camera_width_entry.bind('<Return>', self.update_camera_width)

        # Camera heigth box
        camera_height_label = ttk.Label(image_size_group, text = 'Camera height:')
        camera_height_label.grid(row=1, column=0, sticky=E)

        self.camera_height_contents = IntVar()
        self.camera_height_contents.set(0)
        self.camera_height_prevcontents = self.camera_height_contents.get()
        self.camera_height_entry = ttk.Entry(image_size_group, textvariable = self.camera_height_contents,width=10)
        self.camera_height_entry.config(state=DISABLED)
        self.camera_height_entry.grid(row=1, column=1, pady=0)
        self.camera_height_entry.bind('<Return>', self.update_camera_height)


        # FOV width box
        FOV_width_label = ttk.Label(image_size_group, text = 'FOV width:')
        FOV_width_label.grid(row=2, column=0, sticky=E)

        self.FOV_width_contents = IntVar()
        self.FOV_width_contents.set(0)
        self.FOV_width_prevcontents = self.FOV_width_contents.get()
        self.FOV_width_entry = ttk.Entry(image_size_group, textvariable = self.FOV_width_contents,width=10)
        self.FOV_width_entry.config(state=DISABLED)
        self.FOV_width_entry.grid(row=2, column=1, pady=0)
        self.FOV_width_entry.bind('<Return>', self.update_FOV_width)

        # FOV heigth box
        FOV_height_label = ttk.Label(image_size_group, text = 'FOV height:')
        FOV_height_label.grid(row=3, column=0, sticky=E)

        self.FOV_height_contents = IntVar()
        self.FOV_height_contents.set(0)
        self.FOV_height_prevcontents = self.FOV_height_contents.get()
        self.FOV_height_entry = ttk.Entry(image_size_group, textvariable = self.FOV_height_contents,width=10)
        self.FOV_height_entry.config(state=DISABLED)
        self.FOV_height_entry.grid(row=3, column=1, pady=0)
        self.FOV_height_entry.bind('<Return>', self.update_FOV_height)

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
                camera_label = self.variable.get()
                self.set_camera.set(camera_label)

                self.cam_x_dim = mmc.getImageWidth()
                self.cam_y_dim = mmc.getImageHeight()

                self.update_camera_width(self.cam_x_dim)
                self.update_camera_height(self.cam_y_dim)

                self.update_FOV_width(self.cam_x_dim)
                self.update_FOV_height(self.cam_y_dim)
                
                return
            else:
                print "You can't change the camera whilst acquiring images!"
                return


        self.camoptions = ["...","Thorlabs","OpenCV", "FakeCamera", "uManagerCam"]

        self.variable = StringVar()
        self.variable.set(self.camoptions[0])
        self.camera_entry = ttk.OptionMenu(source_group, self.variable,self.camoptions[0], *self.camoptions, command= lambda _: set_cam(self))
        self.camera_entry.grid(row=0, column=1, pady=0)

        global head, tail
        head,tail = os.path.split(self.parent.filename.name)
        print head, tail

        path_entry = ttk.Entry(source_group, width=15)
        path_entry.insert(0, head)
        path_entry.config(state=DISABLED)
        path_entry.grid(row=1, column=1, pady=0)

        save_entry = ttk.Entry(source_group, width=15)
        save_entry.insert(0, tail)
        save_entry.config(state=DISABLED)
        save_entry.grid(row=2, column=1, pady=0)


        # Create radio buttons for the field of view
        self.FOV_selection = IntVar(value=1)  # initializing the choice, i.e. Python
        self.FOV_modes = [("w x h",1), ("w/2 x h/2",2)]

        FOV_modes_label = ttk.Label(source_group, text = 'FOV:')
        FOV_modes_label.grid(row=3, column=0, sticky=E)

        self.test = 0
        def ShowChoice():
            if self.test == 0:
                self.cam_x_dim = mmc.getImageWidth()
                self.cam_y_dim = mmc.getImageHeight()
                self.test = self.test + 1

            mmc.stopSequenceAcquisition()

            # Need to get the dimensions of the image.
            if self.FOV_modes[self.FOV_selection.get()-1][1] == 1:
                try:
                    mmc.setROI(0, 0, self.cam_x_dim, self.cam_y_dim)
                    mmc.startContinuousSequenceAcquisition(0)

                    self.update_FOV_width(self.cam_x_dim)
                    self.update_FOV_height(self.cam_y_dim)
                except:
                    self.FOV_selection.set(1)
                    mmc.startContinuousSequenceAcquisition(0)
                    tmb.showwarning(title="Oh this is unfortunate...", message = "It seems that this camera does not support this function!")
               
            elif self.FOV_modes[self.FOV_selection.get()-1][1] == 2:
                try:
                    mmc.setROI(int(self.cam_x_dim/4), int(self.cam_y_dim/4), int(self.cam_x_dim/2), int(self.cam_y_dim/2))
                    mmc.startContinuousSequenceAcquisition(0)

                    self.update_FOV_width(int(self.cam_x_dim/2))
                    self.update_FOV_height(int(self.cam_y_dim/2))
                except:
                    self.FOV_selection.set(1)
                    mmc.startContinuousSequenceAcquisition(0)
                    tmb.showwarning(title="Oh this is unfortunate...", message = "It seems that this camera does not support this function!")

        self.FOV_buttons = []
        for (mode, val) in self.FOV_modes:
            rb = tk.Radiobutton(source_group, 
                        text=mode,
                        indicatoron = 0,
                        width = 10,
                        padx = 0, pady = 0,
                        variable=self.FOV_selection, command = ShowChoice,
                        value=val)

            rb.grid(row=2+val, column=1, pady=0)
            self.FOV_buttons.append(rb)

        for radio_button in self.FOV_buttons:
            radio_button.configure(state = DISABLED)

    # Settings group (e.g. camera and files)

        # Scale settings
        scale_label = ttk.Label(settings_group, text = "Scale ("+u"\u03bcm/px:)") 
        scale_label.grid(row=0, column=0, sticky=E)

        scale = self.parent.multiplication_factor
        scalefloat = "%3.0f" % scale
        self.scale_contents = DoubleVar()
        self.scale_contents.set(scalefloat)
        global scale_contents
        self.scale_prevcontents = self.scale_contents.get()
        self.scale_entry = ttk.Entry(settings_group, textvariable = self.scale_contents,width=10)
        self.scale_entry.grid(row=0, column=1, pady=0)
        self.scale_entry.bind('<Return>', self.update_scale)
        self.scale_entry.configure(state="disabled")

        # Exposure settings
        exposure_label = ttk.Label(settings_group, text = 'Exp (ms)')
        exposure_label.grid(row=1, column=0, sticky=E)

        exp = self.parent.exposure
        self.contents = IntVar()
        self.contents.set(int(exp))
        global prevcontents
        prevcontents = self.contents.get()
        self.exposure_entry = ttk.Entry(settings_group, textvariable = self.contents,width=10)
        self.exposure_entry.grid(row=1, column=1, pady=0)
        self.exposure_entry.bind('<Return>', self.update_exposure)
        self.exposure_entry.configure(state="disabled")
                
        # Pixel clock settings
        pixelclock_label = ttk.Label(settings_group, text = 'Pix Clk (MHz):')
        pixelclock_label.grid(row=2, column=0, sticky=E)

        pix_clock = self.parent.pix_clock
        self.pix_clock_contents = IntVar()
        self.pix_clock_contents.set(int(pix_clock))
        global pix_clock_prevcontents
        pix_clock_prevcontents = self.pix_clock_contents.get()
        self.pix_clock_entry = ttk.Entry(settings_group, textvariable = self.pix_clock_contents,width=10)
        self.pix_clock_entry.grid(row=2, column=1, pady=0)
        self.pix_clock_entry.bind('<Return>', self.update_pix_clock)
        self.pix_clock_entry.configure(state="disabled")

        # Acquisition rate settings
        
        acqrate_label = ttk.Label(settings_group, text = 'Acq rate (Hz):')
        acqrate_label.grid(row=3, column=0, sticky=E)

        self.acq_rate_contents = DoubleVar()
        self.acq_rate_contents.set("%3.0f" % self.parent.acq_rate)
        self.acq_rate__entry = ttk.Entry(settings_group, textvariable = self.acq_rate_contents, width=10)
        self.acq_rate__entry.config(state=DISABLED)
        self.acq_rate__entry.grid(row=3, column=1, pady=0)

        # Record interval settings
        rec_interval_label = ttk.Label(settings_group, text = 'Rec intvl (f):')
        rec_interval_label.grid(row=4, column=0, sticky=E)

        rec_interval = self.parent.rec_interval
        self.rec_contents = IntVar()
        self.rec_contents.set(int(rec_interval))
        global rec_prevcontents
        rec_prevcontents = self.rec_contents.get()
        self.rec_interval_entry = ttk.Entry(settings_group, textvariable = self.rec_contents,width=10)
        self.rec_interval_entry.grid(row=4, column=1, pady=0)
        self.rec_interval_entry.bind('<Return>', self.update_rec_interval)
        self.rec_interval_entry.configure(state="disabled")

        # Default settings checkbox
        self.standard_settings = IntVar()
        self.standard_settings.set(1)

        def cb(self, event=None):
            global rec_interval, exposure, pix_clock
            if self.standard_settings_val.get() == 1:

                try:
                    self.rec_contents.set(int(self.parent.init_rec_interval))
                    rec_interval = self.parent.init_rec_interval
                    self.update_rec_interval(event=True)
                except:
                    pass

                try:
                    self.pix_clock_contents.set(int(self.parent.init_pix_clock))
                    pix_clock = self.parent.init_pix_clock
                    self.update_pix_clock(event=True)
                except:
                    pass

                try:
                    self.contents.set(int(self.parent.init_exposure))
                    exposure = self.parent.exposure
                    self.update_exposure(event=True)
                except:
                    pass

                self.scale_entry.configure(state="disabled")
                self.exposure_entry.configure(state="disabled")
                self.rec_interval_entry.configure(state="disabled")
                self.pix_clock_entry.configure(state="disabled")
                self.mm_settings.configure(state="disabled")

            else:
                self.scale_entry.configure(state="enabled")
                self.exposure_entry.configure(state="enabled")
                self.rec_interval_entry.configure(state="enabled") 
                self.pix_clock_entry.configure(state="enabled   ")
                self.mm_settings.configure(state="enabled")
            return      

        def cb2(self, event=None):
            if self.mm_settings_val.get() == 1:
                self.standard_settings_val.set(0)
                tmb.showwarning(title="Warning", message = "This might make things go faster, and it might make things crash. You were warned.")
            return           
        
        self.standard_settings_val = IntVar()
        self.standard_settings_val.set(1)
        self.standard_settings = ttk.Checkbutton(settings_group, text='Default', onvalue=1, offvalue=0, variable=self.standard_settings_val, command= lambda: cb(self))
        self.standard_settings.grid(row=5, column=0, padx=0, pady=0, sticky=W)
        self.standard_settings.configure(state="enabled")


        self.mm_settings_val = IntVar()
        self.mm_settings_val.set(0)
        self.mm_settings = ttk.Checkbutton(settings_group, text='Faster?', onvalue=1, offvalue=0, variable=self.mm_settings_val, command= lambda: cb2(self))
        self.mm_settings.grid(row=5, column=1, padx=0, pady=0, sticky=W)
        self.mm_settings.configure(state="disabled")

    # Analysis Settings group (e.g. camera and files)

        # Num lines settings
        numlines_label = ttk.Label(ana_settings_group, text = '# of lines:')
        numlines_label.grid(row=0, column=0, sticky=E)

        num_lines = self.parent.num_lines
        self.num_lines_contents = IntVar()
        self.num_lines_contents.set(int(num_lines))
        global num_lines_prevcontents
        num_lines_prevcontents = self.num_lines_contents.get()
        self.num_lines_entry = ttk.Entry(ana_settings_group, textvariable = self.num_lines_contents,width=10)
        self.num_lines_entry.grid(row=0, column=1, pady=0)
        self.num_lines_entry.bind('<Return>', self.update_num_lines)

        # Smooth settings
        smooth_label = ttk.Label(ana_settings_group, text = 'Smooth:')
        smooth_label.grid(row=1, column=0, sticky=E)

        smooth = self.parent.smooth_factor
        smoothfloat = int(smooth)
        self.smooth_contents = IntVar()
        self.smooth_contents.set(smoothfloat)
        global smooth_prevcontents
        smooth_prevcontents = self.smooth_contents.get()
        self.smooth_entry = ttk.Entry(ana_settings_group, textvariable = self.smooth_contents,width=10)
        self.smooth_entry.grid(row=1, column=1, pady=0)
        self.smooth_entry.bind('<Return>', self.update_smooth)

        # Integration settings
        integration_label = ttk.Label(ana_settings_group, text = 'Integration:')
        integration_label.grid(row=2, column=0, sticky=E)

        integration = self.parent.integration_factor
        integrationfloat = int(integration)
        self.integration_contents = IntVar()
        self.integration_contents.set(integrationfloat)
        global integration_prevcontents
        integration_prevcontents = self.integration_contents.get()
        self.integration_prevcontents = integration_prevcontents
        self.integration_entry = ttk.Entry(ana_settings_group, textvariable = self.integration_contents,width=10)
        self.integration_entry.grid(row=2, column=1, pady=0)
        self.integration_entry.bind('<Return>', self.update_integration)

        # Threshold settings
        thresh_label = ttk.Label(ana_settings_group, text = 'Threshold:')
        thresh_label.grid(row=3, column=0, sticky=E)

        thresh = self.parent.thresh_factor
        threshfloat = thresh
        self.thresh_contents = DoubleVar()
        self.thresh_contents.set(threshfloat)
        global thresh_prevcontents
        thresh_prevcontents = self.thresh_contents.get()
        self.thresh_prevcontents = thresh_prevcontents
        self.thresh_entry = ttk.Entry(ana_settings_group, textvariable = self.thresh_contents,width=10)
        self.thresh_entry.grid(row=3, column=1, pady=0)
        self.thresh_entry.bind('<Return>', self.update_thresh)

        # Filter setting
        self.filter_is_checked = IntVar()

        filter_checkBox = ttk.Checkbutton(ana_settings_group, text='Filter', onvalue=1, offvalue=0, variable=self.filter_is_checked)
        filter_checkBox.grid(row=4, padx=0, pady=0, sticky=W)

        # Use ROI setting
        self.ROI_is_checked = IntVar()
        self.ROI_checkBox = ttk.Checkbutton(ana_settings_group, text='ROI', onvalue=1, offvalue=0, variable=self.ROI_is_checked)
        self.ROI_checkBox.grid(row=4, column=1, padx=0, pady=0, sticky=W)
        self.ROI_checkBox.configure(state="disabled")

        # Calculate inner diameter setting
        self.ID_is_checked = IntVar()
        self.ID_is_checked.set(1)
        self.ID_checkBox = ttk.Checkbutton(ana_settings_group, text='ID', onvalue=1, offvalue=0, variable=self.ID_is_checked)
        self.ID_checkBox.grid(row=5, column=0, padx=0, pady=0, sticky=W)
        self.ID_checkBox.configure(state="enabled")

        # Org outer tracking algoritm
        self.org_is_checked = IntVar()
        self.org_is_checked.set(1)
        self.org_checkBox = ttk.Checkbutton(ana_settings_group, text='Org', onvalue=1, offvalue=0, variable=self.org_is_checked)
        self.org_checkBox.grid(row=5, column=1, padx=0, pady=0, sticky=W)
        self.org_checkBox.configure(state="enabled")

        # ROI Settings
        self.set_roi = False
        def ROIset_button_function(get_coords):
            self.set_roi = True
            print "Set ROI = ", self.set_roi
            self.ROI_checkBox.configure(state="enabled")
            stop_acq()
            return self.set_roi

        ROI_set_button = ttk.Button(ana_settings_group, text='Set ROI', command= lambda: ROIset_button_function(get_coords=True))
        ROI_set_button.grid(row=6,column=0, columnspan=1, pady=0)
        
        # ROI Settings
        def refdiam_set_button_function(get_coords):
            #### TODO SORT THIS
            self.ref_OD = self.parent.OD
            self.parent.tableframe.max_diameter_text.set(round(self.parent.toolbar.ref_OD,2))
            print "set ref button pressed = ", self.ref_OD
            return self.ref_OD
        refdiam_set_button = ttk.Button(ana_settings_group, text='Set ref', command= lambda: refdiam_set_button_function(get_coords=True))
        refdiam_set_button.grid(row=6,column=1, columnspan=1, padx = 0,pady=0)

    # Outer diameter group
    # Function for the labels
        def coord_label(window, text, row, column):
            label=ttk.Label(window, text=text)
            label.configure(anchor="center")
            label.grid(row=row, column=column, padx = 0, pady = 0,sticky=E)
    # Function for the labels 2
        def coord_entry(window, row, column, coord_label):
            entry = ttk.Entry(window, width=8, textvariable=coord_label)

            entry.config(state=NORMAL)
            entry.grid(row=row, column=column, padx=1, sticky=E)
            self.parent.master.focus_set()
            entry.focus_set()
            self.parent.master.focus_force()
            return entry

        def coord_limits(get_coords, default):
            if get_coords == True:
                if default:
                    self.xlims = (self.x_min_default, self.x_max_default)
                    self.ylims = (self.y_min_default, self.y_max_default)
                    self.ylims2 = (self.y_min_default2, self.y_max_default2)
                    outer_xmin_entry.delete(0, END), outer_xmax_entry.delete(0, END)
                    outer_xmin_entry.insert('0', self.x_min_default), outer_xmax_entry.insert('0', self.x_max_default)
                    outer_ymin_entry.delete(0, END), outer_ymax_entry.delete(0, END)
                    outer_ymin_entry.insert('0', self.y_min_default), outer_ymax_entry.insert('0', self.y_max_default)
                    inner_ymin_entry.delete(0, END), inner_ymax_entry.delete(0, END)
                    inner_ymin_entry.insert('0', self.y_min_default2), inner_ymax_entry.insert('0', self.y_max_default2)
                    self.parent.graphframe.update_scale()
                    print "it did it"
                else:
                    self.xlims = (self.x_min_label.get(),self.x_max_label.get())
                    self.ylims = (self.y_min_label.get(),self.y_max_label.get())
                    self.ylims2 = (self.y_min_label2.get(),self.y_max_label2.get())
                    self.parent.graphframe.update_scale()
                    print "it did it"
                return self.xlims, self.ylims, self.ylims2
                get_coords = False
            else:
                pass

    # Set the initial xlimit values
        self.x_min_label, self.x_max_label = IntVar(value=self.parent.x_min_default), IntVar(value=self.parent.x_max_default)
        self.x_min_default, self.x_max_default = self.x_min_label.get(),self.x_max_label.get()
    # Set the initial OD values
        self.y_min_label, self.y_max_label = IntVar(value=self.parent.y_min_default), IntVar(value=self.parent.y_max_default)
        self.y_min_default, self.y_max_default = self.y_min_label.get(),self.y_max_label.get()
    # Set the initial ID values
        self.y_min_label2, self.y_max_label2 = IntVar(value=self.parent.y_min_default2), IntVar(value=self.parent.y_max_default2)
        self.y_min_default2, self.y_max_default2 = self.y_min_label2.get(),self.y_max_label2.get()
    # Get the x and y limits
        self.xlims = (self.x_min_label.get(),self.x_max_label.get())
        self.ylims = (self.y_min_label.get(),self.y_max_label.get())
        self.ylims2 = (self.y_min_label2.get(),self.y_max_label2.get())


        coord_label(outer_diameter_group, 'Min:', 0, 1)
        coord_label(outer_diameter_group, 'Max:', 0, 2)
        coord_label(outer_diameter_group, 'Time:', 1, 0) # outer_xmin_label = 
        coord_label(outer_diameter_group, 'OD', 2, 0) # outer_xmax_label = 
        coord_label(outer_diameter_group, 'ID:', 3, 0) # inner_ymin_label = 

        outer_xmin_entry = coord_entry(outer_diameter_group, 1, 1, self.x_min_label)
        outer_xmax_entry = coord_entry(outer_diameter_group, 1, 2, self.x_max_label)
        outer_ymin_entry = coord_entry(outer_diameter_group, 2, 1, self.y_min_label)
        outer_ymax_entry = coord_entry(outer_diameter_group, 2, 2, self.y_max_label)
        inner_ymin_entry = coord_entry(outer_diameter_group, 3, 1, self.y_min_label2)
        inner_ymax_entry = coord_entry(outer_diameter_group, 3, 2, self.y_max_label2)

    # Button to set the axis limits
        set_button = ttk.Button(outer_diameter_group, text='Set', command= lambda: coord_limits(get_coords=True, default = False))
        set_button.grid(row=5, column=1, padx = 0, pady=0)
    # Button to set the axis limits to the default values 
        default_button = ttk.Button(outer_diameter_group, text='Default', command= lambda: coord_limits(get_coords=True, default = True))
        default_button.grid(row=6, column=1, padx =0, pady=0) 

    # acquisition_group

        time_label = ttk.Label(acquisition_group, text = 'hr:min:sec:msec:')
        time_label.grid(row=0, column=0, sticky=E)

        temp_label = ttk.Label(acquisition_group, text = 'Temp (' + u"\u00b0C):")
        temp_label.grid(row=1, column=0, sticky=E)

        pressureavg_label = ttk.Label(acquisition_group, text = 'Pressure (mmHg):')
        pressureavg_label.grid(row=2, column=0, sticky=E)

        outdiam_label = ttk.Label(acquisition_group, text = 'OD (' + u"\u03bcm):") 
        outdiam_label.grid(row=3, column=0, sticky=E)

        indiam_label = ttk.Label(acquisition_group, text = 'ID (' + u"\u03bcm):")
        indiam_label.grid(row=4, column=0, sticky=E)

        outdiam_pcnt_label = ttk.Label(acquisition_group, text = 'Diameter (%):')
        outdiam_pcnt_label.grid(row=5, column=0, sticky=E, pady=5)

        self.time_contents = IntVar()
        self.time_contents.set(str(datetime.timedelta(seconds=time.time()-time.time()))[:-4])
        self.time_entry = ttk.Entry(acquisition_group, textvariable = self.time_contents, width=10)
        self.time_entry.config(state=DISABLED)
        self.time_entry.grid(row=0, column=1, pady=0)

        self.temp_contents = IntVar()
        self.temp_contents.set("N/A")
        self.temp_entry = ttk.Entry(acquisition_group, textvariable = self.temp_contents,width=10)
        self.temp_entry.config(state=DISABLED)
        self.temp_entry.grid(row=1, column=1, pady=0)

        self.pressure_contents = IntVar()
        self.pressure_contents.set("N/A")
        self.pressure_entry = ttk.Entry(acquisition_group, textvariable = self.pressure_contents,width=10)
        self.pressure_entry.config(state=DISABLED)
        self.pressure_entry.grid(row=2, column=1, pady=0)

        self.outdiam_contents = IntVar()
        self.outdiam_contents.set("N/A")
        self.outdiam_entry = ttk.Entry(acquisition_group, textvariable = self.outdiam_contents,width=10)
        self.outdiam_entry.config(state=DISABLED)
        self.outdiam_entry.grid(row=3, column=1, pady=0)

        self.indiam_contents = IntVar()
        self.indiam_contents.set("N/A")
        self.indiam_entry = ttk.Entry(acquisition_group, textvariable = self.indiam_contents,width=10)
        self.indiam_entry.config(state=DISABLED)
        self.indiam_entry.grid(row=4, column=1, pady=0)

        self.outdiam_pcnt_contents = IntVar()
        self.outdiam_pcnt_contents.set("N/A")
        self.outdiam_pcnt_entry = ttk.Entry(acquisition_group, textvariable = self.outdiam_pcnt_contents,width=10, foreground='red')
        self.outdiam_pcnt_entry.config(state=DISABLED)
        self.outdiam_pcnt_entry.grid(row=5, column=1, pady=5)



    # Function that will stop the image acquisition
        def stop_acq():
            self.standard_settings.configure(state="enabled")
            if self.standard_settings_val.get() == 0:
                self.scale_entry.configure(state="enabled")
                self.exposure_entry.configure(state="enabled")
                self.pix_clock_entry.configure(state="enabled")
                self.rec_interval_entry.configure(state="enabled")
                self.mm_settings.configure(state="enabled")

            self.camera_entry.configure(state="enabled")
            self.num_lines_entry.configure(state="enabled")
            self.start_flag = False
            self.record_video_checkBox.configure(state="enabled")
            mmc.stopSequenceAcquisition()
            self.record_flag = False
            return self.start_flag,self.record_flag



    # Function that will start the data acquisition
        self.record_flag = False
        self.pressure_protocol_flag = False


        def snapshot():
            self.snapshot_flag = True
            return self.snapshot_flag

        start_button = ttk.Button(start_group, text='Start', command= lambda: self.start_acq())
        start_button.grid(row=0, column=0, pady=0, sticky=N+S+E+W) 

        record_button = ttk.Button(start_group, text='Track', command= lambda: self.record_data())
        record_button.grid(row=1, column=0, pady=0, sticky=N+S+E+W) 

        live_button = ttk.Button(start_group, text='Pause', command= lambda: stop_acq())
        live_button.grid(row=3, column=0, pady=0, sticky=N+S+E+W) 
        
        self.snapshot_flag = False
        snapshot_button = ttk.Button(start_group, text='Snapshot', command= lambda: snapshot())
        snapshot_button.grid(row=4, column=0, pady=0, sticky=N+S+E+W) 

        self.record_is_checked = IntVar()

        self.record_video_checkBox = ttk.Checkbutton(start_group,text='Record?', onvalue=1, offvalue=0, variable=self.record_is_checked)
        self.record_video_checkBox.grid(row=5, column=0, columnspan=1, padx=5, pady=3, sticky=W)


        # Line Settings
        self.set_caliper = False
        def caliper_button_function(get_coords):
            self.set_caliper = True
            print "Set Line = ", self.set_caliper
            #self.LINE_checkBox.configure(state="enabled")
            stop_acq()
            return self.set_caliper




        LINE_set_button = ttk.Button(caliper_group, text='Caliper start', command= lambda: caliper_button_function(get_coords=True))
        LINE_set_button.grid(row=0,column=0, columnspan=1, pady=5)

        label=ttk.Label(acquisition_group, text=u'Caliper length:')
        label.grid(row=6, column=0, padx = 1, sticky=E)

        self.caliper_contents = IntVar()
        self.caliper_contents.set("N/A")
        self.caliper_entry = ttk.Entry(acquisition_group, textvariable = self.caliper_contents,width=10)
        self.caliper_entry.config(state=DISABLED)
        self.caliper_entry.grid(row=6, column=1, pady=0)

        self.delete_caliper = False
        def close_caliper_button_function(get_coords):
            self.delete_caliper = True
            self.set_caliper = False
            print "Set Line = ", self.set_caliper
            #self.LINE_checkBox.configure(state="enabled")
            #stop_acq()
            return self.delete_caliper

        LINE_set_button = ttk.Button(caliper_group, text='Caliper stop', command= lambda: close_caliper_button_function(get_coords=True))
        LINE_set_button.grid(row=3,column=0, columnspan=1, pady=5)


    # Pressure servo control group (servo_group)
        def set_dev(self):
            print self.dev_variable.get() 
            print self.ao_variable.get()
            try:
                self.task.CreateAOVoltageChan("/"+self.dev_variable.get()+"/"+self.ao_variable.get(),"",-10.0,10.0,PyDAQmx.DAQmx_Val_Volts,None)
                self.task.StartTask()
                self.set_pressure_entry.configure(state="enabled")
                
            
            except:
                print "it did not connect"
                tmb.showinfo("Warning", "Cannot connect to NI device. Have you plugged it in?")
            self.update_set_pressure(1, table=False)


        ni_dev_label = ttk.Label(servo_group, text = 'Device:')
        ni_dev_label.grid(row=0, column=0, sticky=E)

        self.dev_options = ["...","Dev0","Dev1", "Dev2"]

        self.dev_variable = StringVar()
        self.dev_variable.set(self.dev_options[0])
        self.dev_entry = ttk.OptionMenu(servo_group, self.dev_variable,self.dev_options[0], *self.dev_options)#, command= lambda _: set_dev(self))
        self.dev_entry.grid(row=0, column=1, pady=0)

        ni_ao_label = ttk.Label(servo_group, text = 'ao channel:')
        ni_ao_label.grid(row=1, column=0, sticky=E)

        self.ao_options = ["...","ao0","ao1", "ao2"]

        self.ao_variable = StringVar()
        self.ao_variable.set(self.ao_options[0])
        self.ao_entry = ttk.OptionMenu(servo_group, self.ao_variable,self.ao_options[0], *self.ao_options, command= lambda _: set_dev(self))
        self.ao_entry.grid(row=1, column=1, pady=0)

        # Pressure settings
        set_pressure_label = ttk.Label(servo_group, text = 'Set pressure:')
        set_pressure_label.grid(row=2, column=0, sticky=E)

        set_pressure = self.parent.set_pressure
        set_pressure = int(set_pressure)
        self.set_pressure_contents = IntVar()
        self.set_pressure_contents.set(set_pressure)
        global set_pressure_prevcontents
        set_pressure_prevcontents = self.set_pressure_contents.get()
        self.set_pressure_entry = ttk.Entry(servo_group, textvariable = self.set_pressure_contents,width=10)
        self.set_pressure_entry.grid(row=2, column=1, pady=0)
        self.set_pressure_entry.bind('<Return>', self.update_set_pressure)
        self.set_pressure_entry.configure(state="disabled")
        
        start_protocol_button = ttk.Button(servo_group, text='Start Protocol', command= lambda: self.start_pressure_protocol())
        start_protocol_button.grid(row=3, column=0, pady=0, sticky=N+S+E+W) 
        start_protocol_button.state(["disabled"])

        stop_protocol_button = ttk.Button(servo_group, text='Stop Protocol', command= lambda: self.stop_pressure_protocol())
        stop_protocol_button.grid(row=3, column=1, pady=0, sticky=N+S+E+W) 
        start_protocol_button.state(["!disabled"])






##################################################
## Graph window
##################################################
class GraphFrame(tk.Frame):

    # Initialisation function
    def __init__(self,parent):

        tk.Frame.__init__(self, parent)#, bg = "yellow")#, highlightthickness=2, highlightbackground="#111")
        self.parent = parent
        self.top = Frame()
        self.top.update_idletasks()
        
        self.xlim1 = self.parent.toolbar.x_min_default # Outer
        self.xlim2 = self.parent.toolbar.x_max_default # Outer
        self.ylim1 = self.parent.toolbar.y_min_default # Outer
        self.ylim2 = self.parent.toolbar.y_max_default # Outer
        self.ylim3 = self.parent.toolbar.y_min_default2 # Inner
        self.ylim4 = self.parent.toolbar.y_max_default2 # Inner
        
    # Function for updating the scale    
    def update_scale(self, blit=True): #### NEE

        self.graphview.ax1.set_xlim(self.parent.toolbar.xlims[0],self.parent.toolbar.xlims[1]) # Outer diameter
        self.graphview.ax1.set_ylim(self.parent.toolbar.ylims[0],self.parent.toolbar.ylims[1]) # Outer diameter
        self.graphview.ax2.set_xlim(self.parent.toolbar.xlims[0],self.parent.toolbar.xlims[1]) # Inner diameter
        self.graphview.ax2.set_ylim(self.parent.toolbar.ylims2[0],self.parent.toolbar.ylims2[1]) # Inner diameter
        self.graphview.figure.canvas.draw()

    # Set things up in here
    def mainWidgets(self,blit=True):  

        # We want to explicitly set the size of the graph so that we can blit
        self.graphview = tk.Label(self)
        other_figsize = [self.parent.graphframe.winfo_width()/100,self.parent.graphframe.winfo_height()/100]
        self.graphview.figure,(self.graphview.ax1,self.graphview.ax2) = plt.subplots(2,1, figsize=other_figsize)

        # initialize lines to be drawn
        self.graphview.line, = self.graphview.ax1.plot([],[])
        self.graphview.line2, = self.graphview.ax2.plot([],[])

        # Set axis limits
        self.graphview.ax1.set_xlim(self.xlim1,self.xlim2) # Outer
        self.graphview.ax2.set_xlim(self.xlim1,self.xlim2) # Inner
        self.graphview.ax1.set_ylim(self.ylim1,self.ylim2) # Outer
        self.graphview.ax2.set_ylim(self.ylim3,self.ylim4) # Inner

        # Set axis labels
        self.graphview.ax1.set_ylabel('Outer diameter (um)', fontsize=14) # Outer diameter labels
        self.graphview.ax2.set_xlabel('Time (s)', fontsize=14) # Inner diameter labels
        self.graphview.ax2.set_ylabel('Lumen diameter (um)', fontsize=14) # Inner diameter labels

        # Draw the canvas
        self.graphview.figure.canvas = FigureCanvasTkAgg(self.graphview.figure, self)
        self.graphview.figure.canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=None, expand=False) ##### THIS IS THE PROBLEM WITH BLITTING HERE. WE NEED TO EXPLICITLY STATE THE FIGURE SIZE ABOVE!!
        self.graphview.figure.canvas.draw()

        # Get the background (because we are blitting)
        self.ax1background = self.graphview.figure.canvas.copy_from_bbox(self.graphview.ax1.bbox)
        self.ax2background = self.graphview.figure.canvas.copy_from_bbox(self.graphview.ax2.bbox)

        #bbarrray = self.graphview.ax1.bbox.get_points()
        #my_blit_box = Bbox(bbarrray)
        #my_blit_box = Bbox.from_bounds(bbarrray[0][0], bbarrray[0][1], (bbarrray[1][0]-bbarrray[0][0])*1.5, bbarrray[1][1]-bbarrray[0][1])

        #self.ax1background = self.graphview.figure.canvas.copy_from_bbox(my_blit_box)
        
    # Plotting function
    def plot(self, xdata, ydata1,ydata2,xlims,ylims, ylims2):

        # Restore the background
        self.graphview.figure.canvas.restore_region(self.ax1background)
        self.graphview.figure.canvas.restore_region(self.ax2background)

        # Remove the previous lines
        try:
            self.graphview.ax1.lines.remove(self.graphview.line)
            self.graphview.ax2.lines.remove(self.graphview.line2)
        except:
            pass

        # Set the new data
        self.graphview.line.set_xdata(xdata)
        self.graphview.line.set_ydata(ydata1)
        self.graphview.line.set_color('blue')

        self.graphview.line2.set_xdata(xdata) #self.graphview.line2.set_xdata(xdata4[::-1][0::int(self.parent.delta_i)][::-1])
        self.graphview.line2.set_ydata(ydata2)
        self.graphview.line2.set_color('red')

        # redraw just the points
        self.graphview.ax1.draw_artist(self.graphview.line)
        self.graphview.ax2.draw_artist(self.graphview.line2)

        # fill in the axes rectangle
        self.graphview.figure.canvas.blit(self.graphview.ax1.bbox)
        self.graphview.figure.canvas.blit(self.graphview.ax2.bbox)


##################################################
## Timing functions
##################################################
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

##################################################
## Table
##################################################
class TableFrame(tk.Frame):
    def __init__(self,parent):
        tk.Frame.__init__(self, parent)#,highlightthickness=2,highlightbackground="#111")#, width=250, height = 300)#, highlightthickness=2, highlightbackground="#111")
        self.parent = parent
        self.mainWidgets()

    def add_row(self):
        try:
            OutDiam = float(self.parent.OD)
            InDiam = float(self.parent.ID)
            caliper = float(self.parent.cameraframe.calibrated_caliper_distance)
            #InDiam = float(ID)
            Label = self.table_text_entry.get()
            Time = (time.time() - self.parent.start_time)
            Time = float(Time)
            Time = round(Time, 1)
            #mxDiastring = StringVar()
            try:
                self.max_diameter_text.set(round(self.parent.toolbar.ref_OD,2))
                max_diameter = self.parent.toolbar.ref_OD
            except:
                self.max_diameter_text.set(np.nan)
                max_diameter = np.nan
            #max_diameter = max_diameter_text.set()
            #max_diameter = int(max_diameter)
            if max_diameter > 0:
                max_diameter = float(max_diameter)
                max_percent = ((float(OutDiam/max_diameter))*100)
                max_percent = round(max_percent, 1)
                self.table_1.insert('', 'end', values=(Time, Label, OutDiam,  max_percent, InDiam, caliper, self.parent.P1,self.parent.P2)) #P1, P2
                hello = ((Time, Label, OutDiam, max_percent, InDiam, caliper, self.parent.P1, self.parent.P2))
            
            else:
                max_percent = '-'
                self.table_1.insert('', 'end', values=(Time, Label, OutDiam, max_percent, InDiam, caliper, self.parent.P1,self.parent.P2)) #P1, P2
                hello = ((Time, Label, OutDiam, max_percent, InDiam, caliper, self.parent.P1, self.parent.P2))
            
            self.table_1.yview_moveto(1)

        except ValueError:
            max_percent = '-'
            self.table_1.insert('', 'end', values=(Time, Label, OutDiam, max_percent, InDiam, caliper, self.parent.P1,self.parent.P2))
            hello = ((Time, Label, OutDiam, max_percent, InDiam, caliper, self.parent.P1, self.parent.P2))
        self.save_table(hello)

    def save_table(self, hello):
        with open((self.parent.txt_file), 'ab') as g:
            w=csv.writer(g, quoting=csv.QUOTE_ALL)
            w.writerow(hello)

    def mainWidgets(self):

        self.tableview = ttk.Frame(self)
        self.tableview.grid(row=1, column=3, sticky=N+S+E+W)

        self.table_text_entry = StringVar()
        self.max_diameter_text = IntVar()

        self.table_text_entry = StringVar()
        self.max_diameter_text = IntVar()

        self.table_2 = tk.Frame(self.tableview)
        self.table_2.grid(row=0, column=0, columnspan=5, sticky=N+S+E+W)

        table_label = ttk.Label(self.table_2, text = 'Label:')
        table_label.grid(row=0, column=0)
        table_entry = ttk.Entry(self.table_2, width=30, textvariable=self.table_text_entry )
        table_entry.grid(row=0, column=1)        
        add_button = ttk.Button(self.table_2, text='Add', command=self.add_row)
        add_button.grid(row=0, column=2)
        max_diameter_label = ttk.Label(self.table_2, text='Reference Diameter:')
        max_diameter_label.grid(row=0, column=3)
        max_diameter_entry = ttk.Entry(self.table_2, width=10, textvariable=self.max_diameter_text )
        max_diameter_entry.grid(row=0, column=4)
        max_diameter_entry.config(state=DISABLED)

       
        
        self.table_1 = ttk.Treeview(self.tableview, show= 'headings')
        self.table_1["columns"] = ('Time', 'Label', 'OD', '%OD ref', 'ID', 'Caliper', 'P1', 'P2')

        self.table_1.column('#0', width=50)
        self.table_1.column('Time', width=50, stretch=False)
        self.table_1.column('Label', width=150)
        self.table_1.column('OD', width=50)
        self.table_1.column('%OD ref', width=75)
        self.table_1.column('ID', width=50)
        self.table_1.column('Caliper', width=50)
        self.table_1.column('P1', width=50)
        self.table_1.column('P2', width=50)

        self.table_1.heading('#1', text = 'Time')
        self.table_1.heading('#2', text = 'Label')
        self.table_1.heading('#3', text = 'OD')
        self.table_1.heading('#4', text = '%OD ref')
        self.table_1.heading('#5', text = 'ID')
        self.table_1.heading('#6', text = 'Caliper')
        self.table_1.heading('#7', text = 'P1')
        self.table_1.heading('#8', text = 'P2')


        scrollbar = Scrollbar(self.tableview)
        scrollbar.grid(row=1,column=2, sticky=NS)
        scrollbar.config( command = self.table_1.yview )
        self.table_1.grid(row=1, column=1, sticky=N+S+E+W)


##################################################
## Camera window
##################################################
class CameraFrame(tk.Frame):
    def __init__(self,parent):
        tk.Frame.__init__(self, parent)#, width=1000, height = 600)#, highlightthickness=2, highlightbackground="#111")
        self.parent = parent

        self.calibrated_caliper_distance = np.nan

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
        # Caliper initialisation
        self.rect2 = None
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
            self.rect = self.cameraview.create_rectangle(self.start_x, self.start_y, self.start_x, self.start_y)#, width = 5, fill='purple')
        elif self.parent.toolbar.set_caliper == True:
            # Delete any old ROIs
            found = event.widget.find_all()
            for iid in found:
                if event.widget.type(iid) == 'rectangle' or event.widget.type(iid) == 'line':
                    event.widget.delete(iid)
            # Create the Line
            self.start_x_caliper = event.x
            self.start_y_caliper = event.y
            self.rect2 = self.cameraview.create_line(self.start_x_caliper, self.start_y_caliper, self.start_x_caliper, self.start_y_caliper, width = 5, fill='purple')
        elif self.parent.toolbar.delete_caliper == True:
            # Delete any old ROIs
            found = event.widget.find_all()
            for iid in found:
                if event.widget.type(iid) == 'rectangle' or event.widget.type(iid) == 'line':
                    event.widget.delete(iid)    
            self.parent.toolbar.delete_caliper = False


    def on_move_press(self, event):
        #Update the ROI when the mouse is dragged
        if self.parent.toolbar.set_roi == True:
            curX, curY = (event.x, event.y)
            self.cameraview.coords(self.rect, self.start_x, self.start_y, curX, curY)
        elif self.parent.toolbar.set_caliper == True:
            curX, curY = (event.x, event.y)
            self.cameraview.coords(self.rect2, self.start_x_caliper, self.start_y_caliper, curX, curY)


    def on_button_release(self, event):
        if self.parent.toolbar.set_roi == True: # Only enable if we have just pressed the button
            self.end_x =  event.x
            self.end_y =  event.y
            self.parent.toolbar.set_roi = False
            self.parent.toolbar.ROI_checkBox.state(['selected'])
            self.parent.toolbar.ROI_is_checked.set(1)

            self.parent.toolbar.start_acq()
            self.parent.toolbar.record_data()
            pass  
        elif self.parent.toolbar.set_caliper == True:
            self.end_x_caliper =  event.x
            self.end_y_caliper =  event.y
            #self.parent.toolbar.set_caliper = False
            self.caliper_line = ((self.start_x_caliper,self.start_y_caliper), (self.end_x_caliper, self.end_y_caliper))
            print "caliper coordinates: ", self.start_x_caliper,self.start_y_caliper,self.end_x_caliper, self.end_y_caliper

            start_x_caliper, start_y_caliper = self.caliper_line[0]
            end_x_caliper, end_y_caliper = self.caliper_line[1]

            # Correct for the scaling

            self.start_x_caliper = int((start_x_caliper - self.delta_width)/self.scale_factor)
            self.start_y_caliper = int((start_y_caliper - self.delta_height)/self.scale_factor)

            self.end_x_caliper = int((end_x_caliper - self.delta_width)/self.scale_factor)
            self.end_y_caliper = int((end_y_caliper - self.delta_height)/self.scale_factor)
            print "caliper coordinates: ", self.start_x_caliper,self.start_y_caliper,self.end_x_caliper, self.end_y_caliper

            self.caliper_distance = hypot(self.end_x_caliper - self.start_x_caliper, self.end_y_caliper - self.start_y_caliper)
            try:
                self.calibrated_caliper_distance = self.caliper_distance*self.parent.multiplication_factor
            except:
                self.calibrated_caliper_distance = self.caliper_distance

            print "Caliper distance = ", self.caliper_distance*self.parent.multiplication_factor
            self.parent.toolbar.update_calipervalue(self.calibrated_caliper_distance)
            
            # Restart imaging
            self.parent.toolbar.set_caliper = False
            self.parent.toolbar.start_acq()
            self.parent.toolbar.record_data()
        

            #print self.line
            #self.update_image(self.slider.get())
            #self.parent.toolbar.update_coords2()

    def rescale_frame(self,frame):
        # Scaling a rectangle to fit inside another rectangle.
        # works out destinationwidth/sourcewidth and destinationheight/sourceheight
        # and scaled by the smaller of the two ratios
        width = frame.shape[1]
        height = frame.shape[0]

        widthfactor = self.maxwidth / width
        heightfactor = self.maxheight / height

        if widthfactor < heightfactor:
            self.scale_factor = widthfactor
        else:
            self.scale_factor = heightfactor

        global scale_factor
        scale_factor = self.scale_factor

        width = int(frame.shape[1] * self.scale_factor)
        height = int(frame.shape[0] * self.scale_factor)

        self.delta_width = int((self.maxwidth - width)/2)
        self.delta_height = int((self.maxheight - height)/2)

        return cv2.resize(frame, (width, height), interpolation = cv2.INTER_AREA)
     
    def process_queue(self,params,img,count):

        try:
            img = img
            imgc = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
            
            OD1,OD2,ID1,ID2,start,diff,ODS_flag,IDS_flag, ROI = params

            if self.parent.toolbar.record_flag:
                
                # Draw the diameters:
                for m in range(len(OD1)):
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
                    if self.parent.toolbar.ID_is_checked.get() == 1:
                        imgc = cv2.line(imgc,(ID2[m],pos),(ID1[m],pos),C2,2) #in opencv rgb is bgr
                    #Vertical lines
                    imgc = cv2.line(imgc,(OD2[m],pos-5),(OD2[m],pos+5),C1,4) #in opencv rgb is bgr
                    imgc = cv2.line(imgc,(OD1[m],pos-5),(OD1[m],pos+5),C1,4) #in opencv rgb is bgr
                    if self.parent.toolbar.ID_is_checked.get() == 1:
                        imgc = cv2.line(imgc,(ID2[m],pos-5),(ID2[m],pos+5),C2,2) #in opencv rgb is bgr
                        imgc = cv2.line(imgc,(ID1[m],pos-5),(ID1[m],pos+5),C2,2) #in opencv rgb is bgr

                # Adding ROI to the image.
                # There is a problem here.
                # The RECTANGLE function uses coordinates from a box drawn on a scaled image
                # We then plot these directly onto the original image, and then scale it again
                # I need to transform the rectangle coordinates and subtract these off.
                #heightdiff = self.maxheight - imgc.shape[0]
                #widthdiff = self.maxwidth - imgc.shape[1]

                # This is drawing on the region of interest
                Cwhite = (0,0,0)
                # First one is horizontal line
                if self.rect and self.parent.toolbar.ROI_is_checked.get() == 1:
                    rx0 = int((ROI[0][0]  - self.delta_width)/self.scale_factor)#
                    rx1 = int((ROI[1][0]  - self.delta_width)/self.scale_factor)#
                    ry0 = int((ROI[0][1]  - self.delta_height)/self.scale_factor) #
                    ry1 = int((ROI[1][1]  - self.delta_height)/self.scale_factor)#

                else:
                    #print "Using this ROI"
                    rx0 = ROI[0][0]#int((ROI[0][0]  - self.delta_width)/self.scale_factor)
                    rx1 = ROI[1][0]#int((ROI[1][0]  - self.delta_width)/self.scale_factor)
                    ry0 = ROI[0][1]#int((ROI[0][1]  - self.delta_height)/self.scale_factor)
                    ry1 = ROI[1][1]#int((ROI[1][1]  - self.delta_height)/self.scale_factor)

                imgc = cv2.line(imgc,(rx0,ry0),(rx1,ry0),Cwhite,3) #in opencv rgb is bgr
                imgc = cv2.line(imgc,(rx0,ry1),(rx1,ry1),Cwhite,3) #in opencv rgb is bgr
                imgc = cv2.line(imgc,(rx0,ry0),(rx0,ry1),Cwhite,3) #in opencv rgb is bgr
                imgc = cv2.line(imgc,(rx1,ry0),(rx1,ry1),Cwhite,3) #in opencv rgb is bgr


                # First one is horizontal line
                if self.rect2 is not None:
                    print "Should be drawing caliper"
                    print "rectangle = ", self.rect2
                    rx0 = self.start_x_caliper
                    rx1 = self.end_x_caliper
                    ry0 = self.start_y_caliper #
                    ry1 = self.end_y_caliper#
                    imgc = cv2.line(imgc,(rx0,ry0),(rx1,ry1),Cwhite,3) #in opencv rgb is bgr
                
                #cv2.putText(imgc, 't=%.2f s' %timenow,(30,30), cv2.FONT_HERSHEY_SIMPLEX, 1,(255,255,255),2,cv2.LINE_AA)
                if self.parent.toolbar.record_is_checked.get() == 1 and self.parent.count%self.parent.rec_interval == 0:
                        directory = os.path.join(head, self.parent.filename.name[:-4]+'\\Tiff\\')
                        if not os.path.exists(directory):
                            os.makedirs(directory)
                        gfxPath = os.path.join(directory, '%s_f=%s_Result.tiff' % (os.path.splitext(tail)[0],str(int(self.parent.count/self.parent.rec_interval)).zfill(6))) 
                        cv2.imwrite(gfxPath,imgc)
                        #out.write(imgc) # For writing to AVI file.
                else:
                    pass

                if self.parent.toolbar.snapshot_flag == True:
                    print "Snapshot pressed"
                    gfxPath = os.path.join(head, '%s_t=%ss_Result SNAPSHOT.tiff' % (os.path.splitext(tail)[0],str(int(self.parent.count/self.parent.rec_interval)).zfill(6))) 
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
        self.gui = GuiPart(self.master, self.queue,self.endApplication)
        
        # Set up the thread to do asynchronous I/O
        # More threads can also be created and used, if necessary
        self.running = 1
        self.thread1 = threading.Thread(target=self.workerThread1)
        #self.thread1.deamon = True
        self.thread1.start(  )

        # Start the periodic call in the GUI to check if the queue contains anything
        self.periodicCall(  )

    # Check every 50 ms if there is something new in the queue.
    def periodicCall(self):

        if self.running:
            #####print "size = ", self.queue.qsize(  )
            if self.queue.qsize(  ) > 0:
                self.gui.processIncoming()
            else:
                pass
        self.master.after(50, self.periodicCall)

    # Thread for getting camera images. Adds each image to a queue
    def workerThread1(self):
        
        while self.running:
            if(self.queue.empty()):
                try: # Catch exception on closing the window!
                # Check if there is an image in the buffer, or an image acuisition in progress
                    #print "image remaining count = ", mmc.getRemainingImageCount()
                    if (mmc.getRemainingImageCount() > 0 or mmc.isSequenceRunning()):

                        if mmc.getRemainingImageCount() > 0:
                            
                            img = mmc.getLastImage()
                            '''
                        #Get image      
                            if self.gui.toolbar.mm_settings_val.get() == 1:
                                img = mmc.getLastImage()# mmc.popNextImage()# ## Get the next image. mmc.popNextImage() #
                            elif self.gui.toolbar.mm_settings_val.get() == 0:
                                img = mmc.popNextImage()
                            else:
                                pass
                            '''
                            if self.gui.toolbar.set_roi == False and self.gui.toolbar.set_caliper == False: # So we pause the image updating and view the damn ROI being drawn
                                self.queue.put(img) # Put the image in the queue
                            
                        else:
                            pass
                        if self.gui.toolbar.mm_settings_val.get() == 1:
                            time.sleep(self.gui.Force_faster_interval)
                        else:
                            time.sleep(self.gui.Force_min_interval)
                    else:
                        pass
                except:
                    pass
            else:
                pass

    # Function that cleans up on exit. It should kill all processes properly.
    def endApplication(self):

        try:
            mmc.stopSequenceAcquisition() # stop uManager acquisition
            mmc.reset() # reset uManager
        except:
            pass

        self.running = 0
        #sys.exit()
        self.master.quit()
        self.master.destroy()

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

# Initiate uManager
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

# Go go go!
    client = ThreadedClient(root)
    root.mainloop(  )