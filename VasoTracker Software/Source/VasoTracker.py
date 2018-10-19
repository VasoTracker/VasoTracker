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
## Version: 1.0.0
## Maintainer: Calum Wilson
## Email: c.wilson.strath@gmail.com
## Status: Production
## 
##################################################

## We found the following to be useful:
## https://www.safaribooksonline.com/library/view/python-cookbook/0596001673/ch09s07.html
## http://code.activestate.com/recipes/82965-threads-tkinter-and-asynchronous-io/
## https://www.physics.utoronto.ca/~phy326/python/Live_Plot.py


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
# Import matplotlib
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
        self.rowconfigure(1, weight=1)
        self.columnconfigure(0, weight=1)
        self.filename = self.get_file_name()
        self.multiplication_factor = self.get_scale()
        self.initUI(endCommand)

    # Open the csv file and then clear it
        f = open(self.filename.name, "w+")
        f.close()

    # Add the headers
        with open((self.filename.name), 'ab') as f:
            w=csv.writer(f, quoting=csv.QUOTE_ALL)
            w.writerow(("Time","Outer Diameter", "Inner Diameter"))

    # Add file for table
        #head,tail = os.path.split(self.filename.name)
        self.txt_file = os.path.splitext(self.filename.name)[0]
        print "tail = ", self.txt_file
        self.txt_file = self.txt_file + ' - Table' + '.csv'
        g = open(self.txt_file, "w+")
        g.close()
        with open((self.txt_file), 'ab') as g:
                v=csv.writer(g, quoting=csv.QUOTE_ALL)
                column_headings = 'Time (s)', 'Label', 'Diameter', 'Pressure 1 (mmHg)', 'Pressure 2 (mmHg)'
                v.writerow(column_headings)


    # Function for getting the save file.
    def get_file_name(self):
        tmb.showinfo("", "Create a file to save output...")
        now = datetime.datetime.now()
        savename = now.strftime("%Y%m%d")
        f = tkFileDialog.asksaveasfile(mode='w', defaultextension=".csv", initialdir="Results\\", initialfile=savename)
        if f:
            return(f)            
        else: # asksaveasfile return `None` if dialog closed with "cancel".
            if tmb.askquestion("No save file selected", "Do you want to quit VasoTracker?", icon='warning'):
                self.endApplication()
            else:
                f = self.get_file_name()

    # Function for getting the save file.
    def get_scale(self):
        scale = tkSimpleDialog.askfloat("Input", "How many um per pixel?")
        if scale is None:
            scale = 1
        return(scale)
        

    # Function for writing to the save file
    def writeToFile(self,data):
        with open((self.filename.name), 'ab') as f:
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
        self.toolbar.grid(row=0, column=0,rowspan=1,columnspan=3, padx=ypadding, pady=ypadding, sticky=E+S+W+N)

    # Make the status bar along the bottom
        self.status_bar = ttk.Label(text = 'Thank you for using VasoTracker.', relief=SUNKEN, anchor='w')
        self.status_bar.pack(side=BOTTOM, fill=X)

    # Make the graph frame
        self.graphframe = GraphFrame(self)
        self.graphframe.grid(row=1, column=0, rowspan=3, padx=ypadding, pady=ypadding, sticky=E+S+W+N)
 
    # Make the table frame
        self.tableframe = TableFrame(self)
        self.tableframe.grid(row=1, column=2, padx=ypadding, pady=ypadding, sticky=E+S+W+N)
 
    # Make the Camera Frame bottom right
        self.cameraframe = CameraFrame(self)
        self.cameraframe.grid(row=2, column=2, padx=ypadding, pady=ypadding, sticky=E+S+W+N)
        if self.toolbar.start_flag:
            mmc.startContinuousSequenceAcquisition(500)

    # Count function for reading in with FakeCamera
        self.count = 0   


    # This function will process all of the incoming images
    def processIncoming(self, outers, inners, timelist):
        """Handle all messages currently in the queue, if any."""
        while self.queue.qsize(  ):
            print "Queue size = ", self.queue.qsize(  )
            try:
                if self.toolbar.record_flag:
                    if self.count == 0:
                        global start_time
                        start_time=time.time()
                    # This is for loading in a video as an example!
                    try:
                        mmc.setProperty('Focus', "Position", self.count)
                    except:
                        pass

                #Get the image
                    msg = self.queue.get(0)

                # Check contents of message and do whatever is needed. As a simple test, print it (in real life, you would suitably update the GUI's display in a richer fashion).
                    #Get the time
                    timenow = time.time() - start_time
                    print "Checkbox Status = ", self.toolbar.record_is_checked.get()
                    if self.toolbar.record_is_checked.get() == 1 and self.count%60 == 0:
                        print head
                        print tail
                        timenow2 = int(timenow)
                        gfxPath = os.path.join(head, '%s_t=%ss.tiff' % (os.path.splitext(tail)[0],timenow2)) 
                        skimage.io.imsave(gfxPath, msg)
                    #print msg
                    self.calculate_diameter = Calculate_Diameter(self,self.multiplication_factor)
                    global OD
                    global ID
                    outer_diameters1,outer_diameters2,inner_diameters1,inner_diameters2,OD,ID,start = self.calculate_diameter.calc(msg, self.multiplication_factor)
                    if self.count == 0:
                        global initOD, initID
                        initOD = OD
                        initID = ID
                    params = timenow,outer_diameters1,outer_diameters2,inner_diameters1,inner_diameters2,OD,start
                    savedata = timenow,OD,ID
                    self.writeToFile(savedata)
                    self.cameraframe.process_queue(params,msg)
                    timelist.append(timenow)
                    #print timelist
                    outers.append(OD)
                    inners.append(ID)
                    self.graphframe.plot(timelist,outers,inners,self.toolbar.xlims, self.toolbar.ylims, self.toolbar.xlims2, self.toolbar.ylims2)    
                    self.count += 1
                else:
                    msg = self.queue.get(0)
                    params = 0,0,0,0,0,0,0
                    self.cameraframe.process_queue(params,msg)  
                

                print self.count
                return
            except Queue.Empty:
                # just on general principles, although we don't expect this branch to be taken in this case
                pass
            return

class setCamera(object):
    def __init__(self,camera_label):
        camera_label = camera_label
        #print "working out the diameter"

    def set(self, camera_label):
        mmc.reset()
        if camera_label == "Thorlabs":
            print "Camera Selected: ", camera_label
            DEVICE = ["ThorCam","ThorlabsUSBCamera","ThorCam"] #camera properties - micromanager creates these in a file
        elif camera_label == "FakeCamera":
            print "Camera Selected: ", camera_label
            DEVICE = ['Camera', 'FakeCamera', 'FakeCamera'] #camera properties - micromanager creates these in a file
        elif camera_label == "":
            tmb.showinfo("Warning", "You need to select a camera source!")
            return
        # Set up the camera
        mmc.enableStderrLog(False)
        mmc.enableDebugLog(False)
        mmc.setCircularBufferMemoryFootprint(100)# (in case of memory problems)
        mmc.loadDevice(*DEVICE)
        mmc.initializeDevice(DEVICE[0])
        mmc.setCameraDevice(DEVICE[0])
        mmc.setExposure(500)
        mmc.setProperty(DEVICE[0], 'PixelType', '8bit')
        mmc.setProperty(DEVICE[0], 'Path mask', 'SampleData\\TEST?{4.0}?.tif') #C:\\00-Code\\00 - VasoTracker\\
        # To load in a sequence 
        DEVICE2 = ['Focus', 'DemoCamera', 'DStage']
        mmc.loadDevice(*DEVICE2)
        mmc.initializeDevice(DEVICE2[0])
        mmc.setFocusDevice(DEVICE2[0])
        #mmc.snapImage()
        #img = mmc.getImage() 
        #mmc.setProperty("DStage", "Position", 100);
        mmc.setProperty(self.DEVICE2[0], "Position", 0)




# Class for the main toolbar
class ToolBar(tk.Frame):
    def __init__(self,parent):
        tk.Frame.__init__(self, parent, height = 150)#,  width=250, highlightthickness=2, highlightbackground="#111")
        self.parent = parent
        self.mainWidgets()
        self.set_camera = setCamera(self)

    def mainWidgets(self):
        self.toolbarview = ttk.Frame(root, relief=RIDGE)
        #self.toolbarview.pack(side=LEFT,  fill=BOTH, expand=1)
        self.toolbarview.grid(row=2,column=2,rowspan=2,sticky=N+S+E+W, pady=ypadding)

   # Tool bar groups
        source_group = ttk.LabelFrame(self, text='Source', height=150, width=200)
        source_group.pack(side=LEFT, anchor=N, padx=3, fill=Y)

        outer_diameter_group = ttk.LabelFrame(self, text='Outer Diameter', height=150, width=200)
        outer_diameter_group.pack(side=LEFT, anchor=N, padx=3, fill=Y)

        inner_diameter_group = ttk.LabelFrame(self, text='Inner Diameter', height=150, width=200)
        inner_diameter_group.pack(side=LEFT, anchor=N, padx=3, fill=Y)

        acquisition_group = ttk.LabelFrame(self, text='Data acquisition', height=150, width=200)
        acquisition_group.pack(side=LEFT, anchor=N, padx=3, fill=Y)

        start_group = ttk.LabelFrame(self, text='Start/Stop', height=150, width=200)
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

        self.camoptions = ["...","Thorlabs","FakeCamera"]
        variable = StringVar()
        variable.set(self.camoptions[0])
        self.camera_entry = ttk.OptionMenu(source_group, variable,self.camoptions[0], *self.camoptions, command= lambda _: set_cam(self))

        #camera_entry = ttk.Entry(source_group, width=20)
        #camera_entry.insert('0', DEVICE[1])
        #camera_entry.config(state=DISABLED)
        self.camera_entry.grid(row=0, column=1, pady=5)

        global head
        global tail
        head,tail = os.path.split(self.parent.filename.name)

        path_entry = ttk.Entry(source_group, width=20)
        path_entry.insert(0, head)
        path_entry.config(state=DISABLED)
        path_entry.grid(row=1, column=1, pady=5)

        save_entry = ttk.Entry(source_group, width=20)
        save_entry.insert(0, tail)
        save_entry.config(state=DISABLED)
        save_entry.grid(row=2, column=1, pady=5)

        scale_label = ttk.Label(source_group, text = 'um/pixel:')
        scale_label.grid(row=3, column=0, sticky=E)
        scale_entry = ttk.Entry(source_group, width=20)
        scale = self.parent.multiplication_factor
        scalefloat = "%4.2f" % scale
        scale_entry.insert('0', scalefloat)
        scale_entry.config(state=DISABLED)
        scale_entry.grid(row=3, column=1, pady=5)


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
                else:
                    self.xlims = (self.x_min_label.get(),self.x_max_label.get())
                    self.ylims = (self.y_min_label.get(),self.y_max_label.get())
                print "XLIMS_TRUE_SET = ", self.xlims
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
                print "Inner XLIMS_TRUE_SET = ", self.xlims2
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

        pressure_label = ttk.Label(acquisition_group, text = 'Pressure (mmHg):')
        pressure_label.grid(row=1, column=0, sticky=E)

        temp_entry = ttk.Entry(acquisition_group, width=20)
        temp_entry.insert(0, "37")
        temp_entry.config(state=DISABLED)
        temp_entry.grid(row=0, column=1, pady=5)

        pressure_entry = ttk.Entry(acquisition_group, width=20)
        pressure_entry.insert(0, "60")
        pressure_entry.config(state=DISABLED)
        pressure_entry.grid(row=1, column=1, pady=5)
    
    

    # Function that will start the image acquisition
        def start_acq():
            if variable.get() == "...":
                tmb.showwarning(title="Warning", message = "You need to select a camera source!")
                self.start_flag = False
            else:
                self.camera_entry.configure(state="disabled")
                print self.start_flag
                self.start_flag = True
                print self.start_flag
                mmc.startContinuousSequenceAcquisition(1000)
            return self.start_flag
    # Function that will stop the image acquisition
        def stop_acq():
            self.camera_entry.configure(state="enabled")
            print self.start_flag
            self.start_flag = False
            print self.start_flag
            mmc.stopSequenceAcquisition()
            return self.start_flag

    # Function that will start the data acquisition
        self.record_flag = False
        def record_data():
            self.record_flag = True
            print "Just set the record flag to: ", self.record_flag
            return self.record_flag



        start_button = ttk.Button(start_group, text='Start', command= lambda: start_acq())
        start_button.grid(row=0, column=0, pady=5, sticky=N+S+E+W) 
        #console = tk.Button(master, text='Exit', command=self.close_app)
        #console.pack(  )
        live_button = ttk.Button(start_group, text='Stop', command= lambda: stop_acq())
        live_button.grid(row=1, column=0, pady=5, sticky=N+S+E+W) 

        record_button = ttk.Button(start_group, text='Record', command= lambda: record_data())
        record_button.grid(row=3, column=0, pady=5, sticky=N+S+E+W) 

        self.record_is_checked = IntVar()

        record_video_checkBox = ttk.Checkbutton(start_group, text='Record Video', onvalue=1, offvalue=0, variable=self.record_is_checked)
        record_video_checkBox.grid(row=4, columnspan=2, padx=5, pady=3, sticky=W)



class GraphFrame(tk.Frame):

    min_x = 0
    max_x = 10
    def __init__(self,parent):
        tk.Frame.__init__(self, parent, highlightthickness=2, highlightbackground="#111")
        self.parent = parent
        self.top = Frame()
        self.top.update_idletasks()
        self.n_points = 100000
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
        self.timeit = TimeIt()
        self.mainWidgets()
        
    
 


    def mainWidgets(self,blit=False):   
        self.graphview = tk.Label(self)
        self.graphview.figure,(self.graphview.ax1,self.graphview.ax2) = plt.subplots(2,1)
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


        self.graphview.figure.canvas.draw()
        self.graphview.figure.canvas = FigureCanvasTkAgg(self.graphview.figure, self)
        self.graphview.figure.canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
        

        if blit:
        # Get the background
            self.ax1background = self.graphview.figure.canvas.copy_from_bbox(self.graphview.ax1.bbox)
            self.ax2background = self.graphview.figure.canvas.copy_from_bbox(self.graphview.ax2.bbox)


    def on_running(self, xdata, ydata1,ydata2,xlims,ylims, xlims2,ylims2,blit=False):
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
    
    # Get the corresponding ydata points
        ydata1A = ydata1[::-1]
        ydata1B = ydata1A[0:len(xdata3)]
        ydata1C = ydata1B[::-1]

        ydata2A = ydata2[::-1]
        ydata2B = ydata2A[0:len(xdata3)]
        ydata2C = ydata2B[::-1]

        #ydata1 = [el2 for (el1,el2) in zip(xdata,ydata1) if el1 > self.xlim1-5] # For some reason this did not work
        #ydata2 = [el2 for (el1,el2) in zip(xdata,ydata2) if el1 > self.xlim1-5] # For some reason this did not work


        # If there are many data points, it is a waste of time to plot all
        #   of them once the screen resolution is reached,
        #   so when the maximum number of points is reached,
        #   halve the number of points plotted. This is repeated
        #   every time the number of data points has doubled.
        
        self.i = int(len(xdata3))
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
                                            xdata3[::-1][0::int(self.delta_i)][::-1],
                                                ydata2C[::-1][0::int(self.delta_i)][::-1],
                                                color="red", linewidth = 3)


            with self.timeit:
                self.graphview.figure.canvas.draw()
                self.graphview.figure.canvas.get_tk_widget().update_idletasks()
                #self.after(2,self.plotter)
                #self.graphview.figure.canvas.flush_events()
        if blit == True:
            with self.timeit:
                self.graphview.figure.canvas.restore_region(self.ax1background)
                self.graphview.figure.canvas.restore_region(self.ax2background)

                try:
                    self.graphview.ax1.lines.remove(self.graphview.line)
                    self.graphview.ax2.lines.remove(self.graphview.line2)
                except:
                    pass



                self.graphview.line.set_xdata(xdata3[::-1][0::int(self.delta_i)][::-1])
                self.graphview.line.set_ydata(ydata1C[::-1][0::int(self.delta_i)][::-1])


                self.graphview.line2.set_xdata(xdata3[::-1][0::int(self.delta_i)][::-1])
                self.graphview.line2.set_ydata(ydata2C[::-1][0::int(self.delta_i)][::-1])

                # redraw just the points
                self.graphview.ax1.draw_artist(self.graphview.line)
                self.graphview.ax2.draw_artist(self.graphview.line2)

                # fill in the axes rectangle
                self.graphview.figure.canvas.blit(self.graphview.ax1.bbox)
                self.graphview.figure.canvas.blit(self.graphview.ax2.bbox)

                self.graphview.figure.canvas.draw_idle()
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
class TimeIt():
    from datetime import datetime
    def __enter__(self):
        self.tic = self.datetime.now()
    def __exit__(self, *args, **kwargs):
        print('runtime: {}'.format(self.datetime.now() - self.tic))


class TableFrame(tk.Frame):
    def __init__(self,parent):
        tk.Frame.__init__(self, parent, width=250, height = 300)#, highlightthickness=2, highlightbackground="#111")
        self.parent = parent
        self.mainWidgets()
              
    def mainWidgets(self):
        self.tableview = ttk.Frame(self)
        self.tableview.grid(row=0, column=0, sticky=N+S+E+W)

        try:
            OutDiam = float(self.parent.processIncoming.OD)
            InDiam = float(self.parent.processIncoming.ID)
        except:
            pass
        
        P1 = '60'
        P2 = '60'

        def add_row():
                try:
                    OutDiam = float(OD)
                    InDiam = float(ID)
                    initOutDiam, initInDiam = float(initOD), float(initID)
                    Label = table_text_entry.get()
                    Time = (time.time() - start_time)
                    Time = float(Time)
                    Time = round(Time, 1)
                    mxDiastring = StringVar()
                    max_diameter_text.set(str(initOutDiam))
                    max_diameter = initOutDiam
                    #max_diameter = max_diameter_text.set()
                    #max_diameter = int(max_diameter)
                    if max_diameter > 0:
                        max_diameter = float(max_diameter)
                        max_percent = ((float(OutDiam/max_diameter))*100)
                        max_percent = round(max_percent, 1)
                        table_1.insert('', 'end', values=(Time, Label, OutDiam, P1, P2, max_percent))
                    else:
                        max_percent = '-'
                        table_1.insert('', 'end', values=(Time, Label, OutDiam, P1, P2, max_percent))
                        hello = Label
                        save_table(hello)
                    table_1.yview_moveto(1)

                except ValueError:
                    max_percent = '-'
                    table_1.insert('', 'end', values=(Time, Label, OutDiam, P1, P2, max_percent))
                    hello = ((Time, Label, OutDiam, P1, P2))
                    print hello
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
        max_diameter_label = ttk.Label(table_2, text='Initial Diameter:')
        max_diameter_label.grid(row=0, column=3)
        max_diameter_entry = ttk.Entry(table_2, width=5, textvariable=max_diameter_text )
        max_diameter_entry.grid(row=0, column=4)

       
        
        table_1 = ttk.Treeview(self.tableview, show= 'headings')
        table_1["columns"] = ('Time', 'Label', 'Diameter', 'Pressure 1', 'Pressure 2', '% Initial')

        table_1.column('#0', width=30)
        table_1.column('Time', width=100, stretch=True)
        table_1.column('Label', width=150)
        table_1.column('Diameter', width=100)
        table_1.column('Pressure 1', width=100)
        table_1.column('Pressure 2', width=100)
        table_1.column('% Initial', width=50)

        table_1.heading('#1', text = 'Time')
        table_1.heading('#2', text = 'Label')
        table_1.heading('#3', text = 'Diameter')
        table_1.heading('#4', text = 'Pressure 1')
        table_1.heading('#5', text = 'Pressure 2')
        table_1.heading('#6', text = '% Initial')


        scrollbar = Scrollbar(self.tableview)
        scrollbar.grid(row=1,column=2, sticky=NS)
        scrollbar.config( command = table_1.yview )
        table_1.grid(row=1, column=1, sticky=N+S+E+W)



class CameraFrame(tk.Frame):
    def __init__(self,parent):
        tk.Frame.__init__(self, parent, width=250, height = 300)#, highlightthickness=2, highlightbackground="#111")
        self.parent = parent
        self.mainWidgets()
              
    def mainWidgets(self):
        self.cameraview = tk.Label(self)
        self.cameraview.grid(row=2,column=2,sticky=N+S+E+W, pady=ypadding)
     
    def process_queue(self,params,img):
        try:
            
            img = img
            imgc = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
            timenow,OD1,OD2,ID1,ID2,OuterD,start = params
            if self.parent.toolbar.record_flag:
                # Draw the diameters:
                for m,OD in enumerate(OD1):
                    pos = m*start+start
                    #Horizontal lines
                    imgc = cv2.line(imgc,(OD1[m],pos),(OD2[m],pos),(255,0,0),4) #in opencv rgb is bgr
                    imgc = cv2.line(imgc,(ID2[m],pos),(ID1[m],pos),(0,0,255),2) #in opencv rgb is bgr
                    #Vertical lines
                    imgc = cv2.line(imgc,(OD2[m],pos-5),(OD2[m],pos+5),(255,0,0),4) #in opencv rgb is bgr
                    imgc = cv2.line(imgc,(OD1[m],pos-5),(OD1[m],pos+5),(255,0,0),4) #in opencv rgb is bgr
                    imgc = cv2.line(imgc,(ID2[m],pos-5),(ID2[m],pos+5),(0,0,255),2) #in opencv rgb is bgr
                    imgc = cv2.line(imgc,(ID1[m],pos-5),(ID1[m],pos+5),(0,0,255),2) #in opencv rgb is bgr

                cv2.putText(imgc, 't=%.2f seconds' %timenow,(20,30), cv2.FONT_HERSHEY_SIMPLEX, 0.5,(255,255,255),1,cv2.LINE_AA)
                if self.parent.toolbar.record_is_checked.get() == 1 and self.parent.count%60 == 0:
                        timenow2 = int(timenow)
                        gfxPath = os.path.join(head, '%s_t=%ss_Result.tiff' % (os.path.splitext(tail)[0],timenow2)) 
                        cv2.imwrite(gfxPath,imgc)

            imgc = cv2.cvtColor(imgc, cv2.COLOR_BGR2RGBA)
            prevImg = Image.fromarray(imgc)
            imgtk = ImageTk.PhotoImage(image=prevImg)
            #Show the image
            self.cameraview.configure(image=imgtk)
            self.cameraview.image = imgtk #If you don't have this - it will flicker the image since it gets deleted during one

        except:
            pass

class Calculate_Diameter(object):

    def __init__(self,image,multiplication_factor):
        image = image
        #print "working out the diameter"
        
    def calc(self,image,multiplication_factor):
    # Set up some parameters
        ny,nx = image.shape
        number,navg = 25,10
        start = int(np.floor(ny/(number+1)))
        end = number*start
        thresh = 0
        
    # The multiplication factor
        scale = multiplication_factor
    # Slice the image
        data = [np.average(image[y-int(navg/2):y+int(navg/2),:], axis=0) for y in  range(start,end+start,start)]
        data2 = np.array(data)
    #Smooth the datums
        window = np.ones(11,'d') 
        smoothed = [np.convolve(window / window.sum(), sig, mode = 'same') for sig in data2]
    #Differentiate the datums
        ddts = [VTutils.diff(sig, 1) for sig in smoothed]
    # Loop through each derivative
        outer_diameters1,outer_diameters2,inner_diameters1,inner_diameters2,OD,ID = VTutils.process_ddts(ddts,thresh,nx,scale)
    #Return the data
        return(outer_diameters1,outer_diameters2,inner_diameters1,inner_diameters2,OD,ID,start)



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

    def periodicCall(self):
        """
        Check every 10 ms if there is something new in the queue.
        """
        if self.running:
            self.gui.processIncoming( self.timelist, self.inners, self.outers )
        if not self.running:
            # This is the brutal stop of the system. You may want to do
            # some cleanup before actually shutting it down.
            import sys
            sys.exit(1)
        if self.running:
            self.master.after(10, self.periodicCall)

    def workerThread1(self):
        """
        This is where we handle the asynchronous I/O. For example, it may be
        a 'select(  )'. One important thing to remember is that the thread has
        to yield control pretty regularly, by select or otherwise.
        """
        while self.running:
            if(self.queue.empty()):
                try: # Catch exception on closing the window!
                # Check if there is an image in the buffer, or an image acuisition in progress
                    if (mmc.getRemainingImageCount() > 0 or mmc.isSequenceRunning()):
                    #Check if there is an image in the buffer
                        if mmc.getRemainingImageCount() > 0:
                            timenow = time.time() - start_time #Get the time
                            img = mmc.popNextImage() # Get the next image.
                            self.queue.put(img) # Put the image in the queue
                except:
                    pass


    def endApplication(self):
        try:
            mmc.stopSequenceAcquisition()
            mmc.reset()
        except:
            pass
        self.running = 0
        #sys.exit()
        root.quit()
        root.destroy()
        self.running = 0
        
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
    #Set the size and/or position

    #root.wm_state('zoomed')
    root.state("zoomed")
    #root.resizable(0,0) # Remove ability to resize
    #root.overrideredirect(True)
    #top = Toplevel(root)
    #root.overrideredirect(1) #hides max min buttons and the big x
# Go go go!
    client = ThreadedClient(root)
    root.mainloop(  )


