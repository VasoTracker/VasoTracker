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


from __future__ import division

import os
import numpy as np
from PIL import Image as something
import scipy
from scipy import ndimage



# EDIT AT YOUR OWN RISK

def diff(sig, n):
    dx = 1/n
    ddt = ndimage.gaussian_filter1d(sig, sigma=6, order=1, mode='nearest') / dx
    ddt = np.array(ddt)
    return ddt

def diff2(sig, n):
    dx = 1/n
    ddt = np.convolve(sig, [1,-1]) / dx# ndimage.gaussian_filter1d(sig, sigma=6, order=1, mode='nearest') / dx
    ddt = np.array(ddt)
    return ddt

def diff3(sig, n):
    dx = 1/n
    ddt = np.diff(sig) / dx# ndimage.gaussian_filter1d(sig, sigma=6, order=1, mode='nearest') / dx
    ddt = np.array(ddt)
    return ddt


# Peak finding function

def detect_peaks(x, mph=None, mpd=1, threshold=0, edge='rising',
                 kpsh=False, valley=False, show=False, ax=None):
    
    "Marcos Duarte, https://github.com/demotu/BMC"


    """Detect peaks in data based on their amplitude and other features.

    Parameters
    ----------
    x : 1D array_like
        data.
    mph : {None, number}, optional (default = None)
        detect peaks that are greater than minimum peak height.
    mpd : positive integer, optional (default = 1)
        detect peaks that are at least separated by minimum peak distance (in
        number of data).
    threshold : positive number, optional (default = 0)
        detect peaks (valleys) that are greater (smaller) than `threshold`
        in relation to their immediate neighbors.
    edge : {None, 'rising', 'falling', 'both'}, optional (default = 'rising')
        for a flat peak, keep only the rising edge ('rising'), only the
        falling edge ('falling'), both edges ('both'), or don't detect a
        flat peak (None).
    kpsh : bool, optional (default = False)
        keep peaks with same height even if they are closer than `mpd`.
    valley : bool, optional (default = False)
        if True (1), detect valleys (local minima) instead of peaks.
    show : bool, optional (default = False)
        if True (1), plot data in matplotlib figure.
    ax : a matplotlib.axes.Axes instance, optional (default = None).

    Returns
    -------
    ind : 1D array_like
        indeces of the peaks in `x`.

    Notes
    -----
    The detection of valleys instead of peaks is performed internally by simply
    negating the data: `ind_valleys = detect_peaks(-x)`
    
    The function can handle NaN's 

    See this IPython Notebook [1]_.

    References
    ----------
    .. [1] http://nbviewer.ipython.org/github/demotu/BMC/blob/master/notebooks/DetectPeaks.ipynb

    Examples
    --------
    >>> from detect_peaks import detect_peaks
    >>> x = np.random.randn(100)
    >>> x[60:81] = np.nan
    >>> # detect all peaks and plot data
    >>> ind = detect_peaks(x, show=True)
    >>> print(ind)

    >>> x = np.sin(2*np.pi*5*np.linspace(0, 1, 200)) + np.random.randn(200)/5
    >>> # set minimum peak height = 0 and minimum peak distance = 20
    >>> detect_peaks(x, mph=0, mpd=20, show=True)

    >>> x = [0, 1, 0, 2, 0, 3, 0, 2, 0, 1, 0]
    >>> # set minimum peak distance = 2
    >>> detect_peaks(x, mpd=2, show=True)

    >>> x = np.sin(2*np.pi*5*np.linspace(0, 1, 200)) + np.random.randn(200)/5
    >>> # detection of valleys instead of peaks
    >>> detect_peaks(x, mph=0, mpd=20, valley=True, show=True)

    >>> x = [0, 1, 1, 0, 1, 1, 0]
    >>> # detect both edges
    >>> detect_peaks(x, edge='both', show=True)

    >>> x = [-2, 1, -2, 2, 1, 1, 3, 0]
    >>> # set threshold = 2
    >>> detect_peaks(x, threshold = 2, show=True)
    """

    x = np.atleast_1d(x).astype('float64')
    if x.size < 3:
        return np.array([], dtype=int)
    if valley:
        x = -x
    # find indices of all peaks
    dx = x[1:] - x[:-1]
    # handle NaN's
    indnan = np.where(np.isnan(x))[0]
    if indnan.size:
        x[indnan] = np.inf
        dx[np.where(np.isnan(dx))[0]] = np.inf
    ine, ire, ife = np.array([[], [], []], dtype=int)
    if not edge:
        ine = np.where((np.hstack((dx, 0)) < 0) & (np.hstack((0, dx)) > 0))[0]
    else:
        if edge.lower() in ['rising', 'both']:
            ire = np.where((np.hstack((dx, 0)) <= 0) & (np.hstack((0, dx)) > 0))[0]
        if edge.lower() in ['falling', 'both']:
            ife = np.where((np.hstack((dx, 0)) < 0) & (np.hstack((0, dx)) >= 0))[0]
    ind = np.unique(np.hstack((ine, ire, ife)))
    # handle NaN's
    if ind.size and indnan.size:
        # NaN's and values close to NaN's cannot be peaks
        ind = ind[np.in1d(ind, np.unique(np.hstack((indnan, indnan-1, indnan+1))), invert=True)]
    # first and last values of x cannot be peaks
    if ind.size and ind[0] == 0:
        ind = ind[1:]
    if ind.size and ind[-1] == x.size-1:
        ind = ind[:-1]
    # remove peaks < minimum peak height
    if ind.size and mph is not None:
        ind = ind[x[ind] >= mph]
    # remove peaks - neighbors < threshold
    if ind.size and threshold > 0:
        dx = np.min(np.vstack([x[ind]-x[ind-1], x[ind]-x[ind+1]]), axis=0)
        ind = np.delete(ind, np.where(dx < threshold)[0])
    # detect small peaks closer than minimum peak distance
    if ind.size and mpd > 1:
        ind = ind[np.argsort(x[ind])][::-1]  # sort ind by peak height
        idel = np.zeros(ind.size, dtype=bool)
        for i in range(ind.size):
            if not idel[i]:
                # keep peaks with the same height if kpsh is True
                idel = idel | (ind >= ind[i] - mpd) & (ind <= ind[i] + mpd) \
                    & (x[ind[i]] > x[ind] if kpsh else True)
                idel[i] = 0  # Keep current peak
        # remove the small peaks and sort back the indices by their occurrence
        ind = np.sort(ind[~idel])

    if show:
        if indnan.size:
            x[indnan] = np.nan
        if valley:
            x = -x
        _plot(x, mph, mpd, threshold, edge, valley, ax, ind)

    return ind
    
def _plot(x, mph, mpd, threshold, edge, valley, ax, ind):
    """Plot results of the detect_peaks function, see its help."""
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        print('matplotlib is not available.')
    else:
        if ax is None:
            _, ax = plt.subplots(1, 1, figsize=(8, 4))

        ax.plot(x, 'b', lw=1)
        if ind.size:
            label = 'valley' if valley else 'peak'
            label = label + 's' if ind.size > 1 else label
            ax.plot(ind, x[ind], '+', mfc=None, mec='r', mew=2, ms=8,
                    label='%d %s' % (ind.size, label))
            ax.legend(loc='best', framealpha=.5, numpoints=1)
        ax.set_xlim(-.02*x.size, x.size*1.02-1)
        ymin, ymax = x[np.isfinite(x)].min(), x[np.isfinite(x)].max()
        yrange = ymax - ymin if ymax > ymin else 1
        ax.set_ylim(ymin - 0.1*yrange, ymax + 0.1*yrange)
        ax.set_xlabel('Data #', fontsize=14)
        ax.set_ylabel('Amplitude', fontsize=14)
        mode = 'Valley detection' if valley else 'Peak detection'
        ax.set_title("%s (mph=%s, mpd=%d, threshold=%s, edge='%s')"
                     % (mode, str(mph), mpd, str(threshold), edge))
        # plt.grid()
        plt.show()

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


def process_ddts(ddts,thresh_factor,thresh,nx,scale,start_x, ID_mode, detection_mode):
    outer_diameters1 = [] # array for diameter data
    outer_diameters2 = []
    inner_diameters1 = [] # array for diameter data
    inner_diameters2 = []
    ODS = []
    IDS = []
    scale = scale
    start_x = int(start_x)
    timeit = TimeIt()
    end_x = start_x + len(ddts[0])


    print "start_x = ", start_x
    print "end_x = ", end_x
    print "length = ", len(ddts[0])
    print "thresh = ", thresh

    for j,ddt in enumerate(ddts):
        #Get local extrema positions
        valley_indices = detect_peaks(ddt, mph=0.04, mpd=1, valley=True)
        peaks_indices = detect_peaks(ddt, mph=0.04, mpd=1, valley=False)
        #Get the local extrema values
        valleys = [ddt[indice] for indice in valley_indices]
        peaks = [ddt[indice] for indice in peaks_indices]
        try:
            # Get the value of the biggest nadir in the first half of the dataset
            if detection_mode == 1:
                args = [i for i,idx in enumerate(valley_indices) if idx > thresh  and idx < len(ddts[0])/2] # >170 to filter out tie #args = [i for i,idx in enumerate(valley_indices) if idx > thresh  and idx < (end_x)/2] # >170 to filter out tie
            else:
                args = [i for i,idx in enumerate(valley_indices) if idx > thresh  and idx < 3*len(ddts[0])/4]

            length_to_add = len([i for i,idx in enumerate(valley_indices) if idx < thresh]) # Add this to correct for above filter
            nadirs_firsthalf = [valleys[i] for i in args]
            arg1 = np.argmax(np.absolute(nadirs_firsthalf))
            arg1 = arg1+length_to_add

            OD1 = valley_indices[arg1]
            OD1_ = valley_indices[arg1] + start_x

        
            # Get the value of the biggest peak in the second half of the dataset

            args2 = [i for i,idx in enumerate(peaks_indices) if idx > OD1+(len(ddts[0])-OD1)/10]# if idx > (end_x)/2] #args2 = [i for i,idx in enumerate(peaks_indices) if idx > (end_x)/2]
            peaks_2ndhalf = [peaks[i] for i in args2]
            arg2 = np.argmax(np.absolute(peaks_2ndhalf))
            arg3 =  np.where(peaks == peaks_2ndhalf[arg2])[0][0]

            
            OD2 = peaks_indices[arg3]
            OD2_ = peaks_indices[arg3] + start_x

        except:
            OD1_ = 0
            OD2_ = nx
        
        try:
            # The first inner diameter point is the first big (or the biggest) positive peak after the initial negative peak
            #test = [item for item in peaks_indices if item > OD1_ and item < nx/2]
            test = [item for item in peaks_indices if item > OD1 and item < (OD1+(OD2-OD1)/2)]#nx/2]

            arg3 = 0 # This arg for the first!
            ID1_ = test[arg3] + start_x
            '''

            # Over writing this for the biggst peak
            #print test
            test3 = [ddt[item] for item in test]
            #print test3
            arg4 = np.argmax(np.absolute(test3)) # This arg for the biggest!
            #print arg4
            ID1_ = test[arg4]
            #print "Inner Diameter 1 = ", ID1_
            '''
            # The second inner diameter point is the last big negative peak before the big positive
            #test2 = [item for item in valley_indices if item < OD2_ and item > nx/2]
            test2 = [item for item in valley_indices if item < OD2 and item > (OD1-(OD2-OD1)/2)]#nx/2]
            ID2_ = test2[-1] + start_x
            #print "Inner Diameter 2 = ", ID2_

            '''
            # Over writing this for the biggst peak
            test4 = [ddt[item] for item in test2]
            arg5 = np.argmax(np.absolute(test2))
            ID2_ = test2[arg5]
            '''


        except:
            ID1_ = 0
            ID2_ = 0


        OD = scale*(OD2_-OD1_)
        ID = scale*(ID2_ - ID1_)

        if ID_mode == 0:

            ID1_ = np.NaN
            ID2_ = np.NaN
            ID = np.NaN

        outer_diameters1.append(OD1_,)
        outer_diameters2.append(OD2_,)
        inner_diameters1.append(ID1_,)
        inner_diameters2.append(ID2_,)
        ODS.append(OD)
        IDS.append(ID)
    ODlist = [el for el in ODS if el != 0]
    IDlist = [el for el in IDS if el != 0]

    OD = np.average(ODlist)
    ID = np.average(IDlist)

    STDEVOD = np.std(ODlist)
    STDEVID = np.std(IDlist)


    ODlist2 = [el for el in ODlist if (OD - STDEVOD) < el < (OD + STDEVOD)]
    IDlist2 = [el for el in IDlist if (ID - STDEVID) < el < (ID + STDEVID)]

    OD = np.average(ODlist2)
    ID = np.average(IDlist2)

    ODS_flag = [1 if (OD - 3*STDEVOD) < el < (OD + 3*STDEVOD) else 0 for i,el in enumerate(ODS) ]
    IDS_flag = [1 if (ID - 3*STDEVID) < el < (ID + 3*STDEVID) else 0 for i,el in enumerate(IDS) ]

    ODS_zscore = is_outlier(np.asarray(ODS), thresh_factor).tolist()
    IDS_zscore = is_outlier(np.asarray(IDS), thresh_factor).tolist()

    ODS_flag = [0 if el else 1 for el in ODS_zscore]
    IDS_flag = [0 if el else 1 for el in IDS_zscore]


    ODlist2 = [el1 for el1,el2 in zip(ODlist, ODS_flag) if el2 == 1]
    IDlist2 = [el1 for el1,el2 in zip(IDlist, ODS_flag) if el2 == 1]

    OD = np.average(ODlist2)
    ID = np.average(IDlist2)

    return(outer_diameters1,outer_diameters2,inner_diameters1,inner_diameters2,OD,ID,ODS_flag,IDS_flag,ODlist, IDlist)





### Outlier function is from here:
### https://stackoverflow.com/questions/22354094/pythonic-way-of-detecting-outliers-in-one-dimensional-observation-data

def is_outlier(points, thresh):
    """
    Returns a boolean array with True if points are outliers and False 
    otherwise.

    Parameters:
    -----------
        points : An numobservations by numdimensions array of observations
        thresh : The modified z-score to use as a threshold. Observations with
            a modified z-score (based on the median absolute deviation) greater
            than this value will be classified as outliers.

    Returns:
    --------
        mask : A numobservations-length boolean array.

    References:
    ----------
        Boris Iglewicz and David Hoaglin (1993), "Volume 16: How to Detect and
        Handle Outliers", The ASQC Basic References in Quality Control:
        Statistical Techniques, Edward F. Mykytka, Ph.D., Editor. 
    """
    if len(points.shape) == 1:
        points = points[:,None]
    median = np.median(points, axis=0)
    diff = np.sum((points - median)**2, axis=-1)
    diff = np.sqrt(diff)
    med_abs_deviation = np.median(diff)

    modified_z_score = 0.6745 * diff / med_abs_deviation

    return modified_z_score > thresh





def process_ddts_US(ddts,thresh,nx,scale,start_x):
    outer_diameters1 = [] # array for diameter data
    outer_diameters2 = []
    inner_diameters1 = [] # array for diameter data
    inner_diameters2 = []
    ODS = []
    IDS = []
    scale = scale
    start_x = int(start_x)
    timeit = TimeIt()
    for j,ddt in enumerate(ddts):
        nx2 = len(ddt)
        #Get local extrema positions
        valley_indices = detect_peaks(ddt, mph=0.04, mpd=1, valley=True)
        peaks_indices = detect_peaks(ddt, mph=0.04, mpd=1, valley=False)
        #Get the local extrema values
        valleys = [ddt[indice] for indice in valley_indices]
        peaks = [ddt[indice] for indice in peaks_indices]
        try:
            # Get the value of the biggest nadir in the first half of the dataset
            args = [i for i,idx in enumerate(valley_indices)if idx >25 and idx < nx2/2] # >170 to filter out tie
            length_to_add = len([i for i,idx in enumerate(valley_indices) if idx < thresh]) # Add this to correct for above filter
            nadirs_firsthalf = [valleys[i] for i in args]
            arg1 = np.argmax(np.absolute(nadirs_firsthalf))
            arg1 = arg1+length_to_add
            OD1_ = valley_indices[arg1] + start_x
        except:
            OD1_ = 0
        
        try:
            # Get the value of the biggest peak in the second half of the dataset
            
            args2 = [i for i,idx in enumerate(peaks_indices) if OD1_<idx]
            peaks_2ndhalf = [peaks[i] for i in args2]
            arg2 = np.argmax(np.absolute(peaks_2ndhalf))
            arg3 =  np.where(peaks == peaks_2ndhalf[arg2])[0][0]


            
            OD2_ = peaks_indices[arg3] + start_x

        except:
            OD2_ = nx
        

        ID1_ = OD1_
        ID2_ = OD2_


        OD = scale*(OD2_-OD1_)
        ID = scale*(ID2_ - ID1_)
        outer_diameters1.append(OD1_,)
        outer_diameters2.append(OD2_,)
        inner_diameters1.append(ID1_,)
        inner_diameters2.append(ID2_,)
        ODS.append(OD)
        IDS.append(ID)
    ODlist = [el for el in ODS if el != 0]
    IDlist = [el for el in IDS if el != 0]

    OD = np.average(ODlist)
    ID = np.average(IDlist)

    STDEVOD = np.std(ODlist)
    STDEVID = np.std(IDlist)


    ODlist2 = [el for el in ODlist if (OD - STDEVOD) < el < (OD + STDEVOD)]
    IDlist2 = [el for el in IDlist if (ID - STDEVID) < el < (ID + STDEVID)]

    OD = np.average(ODlist2)
    ID = np.average(IDlist2)

    ODS_flag = [1 if (OD - 3*STDEVOD) < el < (OD + 3*STDEVOD) else 0 for i,el in enumerate(ODS) ]
    IDS_flag = [1 if (ID - 3*STDEVID) < el < (ID + 3*STDEVID) else 0 for i,el in enumerate(IDS) ]

    ODS_zscore = is_outlier(np.asarray(ODS)).tolist()
    IDS_zscore = is_outlier(np.asarray(IDS)).tolist()

    ODS_flag = [0 if el else 1 for el in ODS_zscore]
    IDS_flag = [0 if el else 1 for el in IDS_zscore]


    ODlist2 = [el1 for el1,el2 in zip(ODlist, ODS_flag) if el2 == 1]
    IDlist2 = [el1 for el1,el2 in zip(IDlist, ODS_flag) if el2 == 1]

    OD = np.average(ODlist2)
    ID = np.average(IDlist2)

    return(outer_diameters1,outer_diameters2,inner_diameters1,inner_diameters2,OD,ID,ODS_flag,IDS_flag,ODlist, IDlist)