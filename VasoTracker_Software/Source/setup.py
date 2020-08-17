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
## Version: 1.3.0
## Maintainer: Calum Wilson
## Email: vasotracker@gmail.com
## Status: Production
## Last updated: 20200816
## 
##################################################



import cx_Freeze
import sys
import matplotlib
import os
import glob
import json

#base = None
base = None#'Win32GUI'

#if sys.platform == 'Win32':
#    base = 'Win32GUI'

PythonPath = os.path.split(sys.executable)[0] #get python path

os.environ['TCL_LIBRARY'] = os.path.join(PythonPath,"tcl","tcl8.5")
os.environ['TK_LIBRARY']  = os.path.join(PythonPath,"tcl","tk8.5")

mkl_files_json_file = glob.glob(os.path.join(PythonPath, "conda-meta", "mkl-[!service]*.json"))[0] #json files that has mkl files list (exclude the "service" file)

mkl_omp_files_relative_path = os.path.join("Library", "bin")
mkl_omp_files = glob.glob(os.path.join(PythonPath, mkl_omp_files_relative_path, "libiomp*.dll")) #Without these, this error would appear: Intel MKL FATAL ERROR: Cannot load mkl_intel_thread.dll.

qt_platform_files_relative_path = os.path.join("Library", "plugins", "platforms")
qt_platform_files = glob.glob(os.path.join(PythonPath, qt_platform_files_relative_path, "*.dll")) #Qt necessary files

with open(mkl_files_json_file) as file:
    mkl_files_json_data = json.load(file)

numpy_mkl_dlls = mkl_files_json_data["files"] #get the list of files from the json data file

np_dlls_fullpath = list(map(lambda currPath: os.path.join(PythonPath, currPath), numpy_mkl_dlls)) #get the full path of these files

qt_platform_files_include_pairs = list(map(lambda currPath: (currPath, os.path.join("platforms", os.path.basename(currPath))), qt_platform_files)) #get the full path of these files


executables = [cx_Freeze.Executable("VasoTracker.py", base=base, icon="ICON.ICO")]
additional_mods = ['cv2','atexit','numpy.core._methods', 'numpy.lib.format', "matplotlib.backends.backend_tkagg"]
excludes = ["winpty"]
#buildOptions = dict(include_files = ['SampleData/']) #folder,relative path. Use tuple like in the single file to set a absolute path.
includefiles = ["ICON.ICO", "Start_up.bat",'SampleData/', 'Pressure_Monitor_V3/', 'Temperature_Controller_V3/','Results/', 'Splash.gif', 'fonts/','images/','sounds/',
                'Instructions.pdf','default_settings.ini', 'OpenCV.cfg', 'MMConfig.cfg','opencv_ffmpeg310_64.dll', 'opencv_ffmpeg320_64.dll'] + np_dlls_fullpath + qt_platform_files_include_pairs + mkl_omp_files


cx_Freeze.setup(
        name = "VasoTracker",
        options = {"build_exe": {"excludes": excludes,'includes': additional_mods, 
                    "packages":['skimage',"tkFileDialog","scipy","cv2","Tkinter", "matplotlib", "Queue","cytoolz"], 
                    "include_files":includefiles}},
        version = "1.3.0",
        description = "Vasotracker Diameter Tracking",
        executables = executables    )
