import cx_Freeze
import sys
import matplotlib

base = None

if sys.platform == 'Win32':
    base = 'Win32'

executables = [cx_Freeze.Executable("VasoTracker.py", base=base, icon="ICON.ICO")]
additional_mods = ['cv2','atexit','numpy.core._methods', 'numpy.lib.format', "matplotlib.backends.backend_tkagg"]
excludes = ["winpty"]
#buildOptions = dict(include_files = ['SampleData/']) #folder,relative path. Use tuple like in the single file to set a absolute path.

cx_Freeze.setup(
        name = "VasoTracker",
        options = {"build_exe": {"excludes": excludes,'includes': additional_mods, 
                    "packages":['skimage',"tkFileDialog","scipy","cv2","Tkinter", "matplotlib", "Queue"], 
                    "include_files":["ICON.ICO", 'SampleData/', 'Results/']}},
        version = "1.0.1",
        description = "Vasotracker Diameter Tracking",
        executables = executables    )


