#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Sep 14 10:48:41 2018

@author: cpaessvisitor
"""

from netCDF4 import Dataset
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from netCDF4 import Dataset
import matplotlib
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap # Import the Basemap toolkit
from pyproj import Proj
from matplotlib.colors import LinearSegmentedColormap
import numpy as np
import os
import glob
import sys


#RGB values must be between 0 and 1

# Rebin function from https://stackoverflow.com/questions/8090229/resize-with-averaging-or-rebin-a-numpy-2d-array
def rebin(a, shape):
    sh = shape[0],a.shape[0]//shape[0],shape[1],a.shape[1]//shape[1]
    return a.reshape(sh).mean(-1).mean(1)


formatstr = '*L1b-RadC-M3C'
datestr = '*s2017*' 


#Put into fns all the files from a directory corresponding to year 2017, a certain day and a certain hour
fns = []
nch = 1
for nch in range(1,17):
    chstr = str(nch).zfill(2)
    fns.append(sorted(glob.glob(formatstr+chstr+datestr+'*.nc')))


#Get the number of photographies per band
num_photos = np.shape(fns)[1]

#Choose the number of the photography (i.e 0)
photo = 10

#Get the full name of the path to the nc file
fn1 = fns[0][photo]
path = fn1


# Search for the Scan start in the file name
Start = (path[path.find("s")+1:path.find("_e")])
Start_Formatted = Start[0:4] + " Day " + Start[4:7] + " - " + Start [7:9] + ":" + Start [9:11] + ":" + Start [11:13] + "." + Start [13:14] + " UTC"
# Search for the Scan end in the file name
End = (path[path.find("e")+1:path.find("_c")])
End_Formatted = End[0:4] + " Day " + End[4:7] + " - " + End [7:9] + ":" + End [9:11] + ":" + End [11:13] + "." + End [13:14] + " UTC"

#Find files corresponding to red and veggie and IR
ifn2 = [i for i, s in enumerate(fns[1][:]) if Start in s]
ifn3 = [i for i, s in enumerate(fns[2][:]) if Start in s]
ifn13 = [i for i, s in enumerate(fns[12][:]) if Start in s]

#Get the path of these three files
fn2 = fns[1][ifn2[0]]
Start2 = (fn2[fn2.find("s")+1:fn2.find("_e")])
fn3 = fns[2][ifn3[0]]
Start3 = (fn3[fn3.find("s")+1:fn3.find("_e")])
fn13 = fns[12][ifn13[0]]
Start13 = (fn13[fn13.find("s")+1:fn13.find("_e")])
    


# Define some constants needed for the conversion of radiance per unit wavenumber to radiance only
Esun_Ch_01 = 726.721072
Esun_Ch_02 = 663.274497
Esun_Ch_03 = 441.868715
d2 = 0.3


#Load Channel 1 - Blue Visible
g16nc = Dataset(fn1)
radiance_1 = g16nc.variables['Rad'][:]
g16nc.close()
g16nc = None
ref_1 = (radiance_1 * np.pi * d2) / Esun_Ch_01
# Make sure all data is in the valid RGB data range
ref_1 = np.maximum(ref_1, 0.0)
ref_1 = np.minimum(ref_1, 1.0)
ref_gamma_1 = np.sqrt(ref_1)

#Load Channel 2 - Red Visible
g16nc = Dataset(fn2)
radiance_2 = g16nc.variables['Rad'][:]
g16nc.close()
g16nc = None
ref_2 = (radiance_2 * np.pi * d2) / Esun_Ch_02
# Make sure all data is in the valid RGB data range
ref_2 = np.maximum(ref_2, 0.0)
ref_2 = np.minimum(ref_2, 1.0)
ref_gamma_2 = np.sqrt(ref_2)
ref_gamma_2 = rebin(ref_gamma_2, ref_gamma_1.shape)

# Load Channel 3 - Veggie Near IR
g16nc = Dataset(fn3)
radiance_3 = g16nc.variables['Rad'][:]
g16nc.close()
g16nc = None
ref_3 = (radiance_3 * np.pi * d2) / Esun_Ch_03
# Make sure all data is in the valid RGB data range
ref_3 = np.maximum(ref_3, 0.0)
ref_3 = np.minimum(ref_3, 1.0)
ref_gamma_3 = np.sqrt(ref_3)

#Turn veggie into approximate green
ref_gamma_3_true = 0.48358168 * ref_gamma_2 + 0.45706946 * ref_gamma_1 + 0.06038137 * ref_gamma_3


#Do something to have the space white
masque = np.where(ref_gamma_3.mask == True)
alpha = np.ones(ref_gamma_3.shape)
alpha[masque] = 0.0


#Plot geostationnary picture
truecolor = np.stack([ref_gamma_2, ref_gamma_3_true, ref_gamma_1, alpha], axis=2)
im = plt.imshow(truecolor)
plt.title("True Color"  + "\n Scan from " + Start_Formatted + " to " + End_Formatted, color='black')
plt.show()






#More sophisticated plot
g16nc = Dataset(fn1)
# Satellite height
sat_h = g16nc.variables['goes_imager_projection'].perspective_point_height

# Satellite longitude
sat_lon = g16nc.variables['goes_imager_projection'].longitude_of_projection_origin

# Satellite sweep
sat_sweep = g16nc.variables['goes_imager_projection'].sweep_angle_axis

# The projection x and y coordinates equals
# the scanning angle (in radians) multiplied by the satellite height (http://proj4.org/projections/geos.html)
X = g16nc.variables['x'][:] * sat_h
Y = g16nc.variables['y'][:] * sat_h


# The geostationary projection is perhaps the easiest way to plot the image on a map.
# Essentially, we are stretching the image across a map with the same projection and dimensions.
m = Basemap(projection='geos', lon_0=sat_lon,
            resolution='i', area_thresh=5000,
            llcrnrx=X.min(),llcrnry=Y.min(),
            urcrnrx=X.max(),urcrnry=Y.max())


plt.figure(figsize=[15, 12])
m.imshow(np.flipud(truecolor)) # Remember, "images" are upside down, so flip up/down
m.drawcoastlines()
m.drawcountries()
m.drawstates()

plt.title("True Color"  + "\n Scan from " + Start_Formatted + " to " + End_Formatted, color='black')

g16nc.close()












    