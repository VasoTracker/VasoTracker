from __future__ import division

import os
import numpy as np
from PIL import Image as something
import scipy
from scipy import ndimage

# THIS FILE COPYRIGHT (C) THE UNIVERSITY OF DURHAM 2014 with some input from Calum
# THIS FILE IS NOT FOR RE-DISTRUBUTION. ALL RIGHTS RESERVED

# EDIT AT YOUR OWN RISK

def diff(sig, n):
    dx = 1/n
    ddt = ndimage.gaussian_filter1d(sig, sigma=6, order=1, mode='nearest') / dx
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




def process_ddts(ddts,thresh,nx,scale):
    outer_diameters1 = [] # array for diameter data
    outer_diameters2 = []
    inner_diameters1 = [] # array for diameter data
    inner_diameters2 = []
    ODS = []
    IDS = []
    scale = scale
    for j,ddt in enumerate(ddts):
        #Get local extrema positions
        valley_indices = detect_peaks(ddt, mph=0.04, mpd=1, valley=True)
        peaks_indices = detect_peaks(ddt, mph=0.04, mpd=1, valley=False)
        #Get the local extrema values
        valleys = [ddt[indice] for indice in valley_indices]
        peaks = [ddt[indice] for indice in peaks_indices]
        try:
            # Get the value of the biggest nadir in the first half of the dataset
            args = [i for i,idx in enumerate(valley_indices) if idx > thresh  and idx < nx/2] # >170 to filter out tie
            length_to_add = len([i for i,idx in enumerate(valley_indices) if idx < thresh]) # Add this to correct for above filter
            nadirs_firsthalf = [valleys[i] for i in args]
            arg1 = np.argmax(np.absolute(nadirs_firsthalf))
            arg1 = arg1+length_to_add

        
            # Get the value of the biggest peak in the second half of the dataset

            args2 = [i for i,idx in enumerate(peaks_indices) if idx > nx/2]
            peaks_2ndhalf = [peaks[i] for i in args2]
            arg2 = np.argmax(np.absolute(peaks_2ndhalf))
            arg3 =  np.where(peaks == peaks_2ndhalf[arg2])[0][0]


            OD1_ = valley_indices[arg1]
            OD2_ = peaks_indices[arg3]

        except:
            OD1_ = 0
            OD2_ = nx
        
        try:
            # The first inner diameter point is the first big (or the biggest) positive peak after the initial negative peak
            test = [item for item in peaks_indices if item > OD1_ and item < nx/2]
            arg3 = 0 # This arg for the first!
            ID1_ = test[arg3]

            # Over writing this for the biggst peak
            #print test
            test3 = [ddt[item] for item in test]
            #print test3
            arg4 = np.argmax(np.absolute(test3)) # This arg for the biggest!
            #print arg4
            ID1_ = test[arg4]
            #print "Inner Diameter 1 = ", ID1_

            # The second inner diameter point is the last big negative peak before the big positive
            test2 = [item for item in valley_indices if item < OD2_ and item > nx/2]
            ID2_ = test2[-1]
            #print "Inner Diameter 2 = ", ID2_

            # Over writing this for the biggst peak
            test4 = [ddt[item] for item in test2]
            arg5 = np.argmax(np.absolute(test2))
            ID2_ = test2[arg5]


        except:
            ID1_ = 0
            ID2_ = 0


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

    print OD
    print STDEVOD

    ODlist2 = [el for el in ODlist if (OD - STDEVOD) < el < (OD + STDEVOD)]
    IDlist2 = [el for el in IDlist if (ID - STDEVID) < el < (ID + STDEVID)]

    OD = np.average(ODlist2)
    ID = np.average(IDlist2)

    return(outer_diameters1,outer_diameters2,inner_diameters1,inner_diameters2,OD,ID)
