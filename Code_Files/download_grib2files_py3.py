#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Sep 27 08:56:25 2018

@author: cpaessvisitor
"""

import numpy as np
import subprocess
import re 
from io import StringIO 
from datetime import date, timedelta, datetime 
import urllib.request
import sys
import os
import time


def reporthook(a, b, c):
    """
    Report download progress in megabytes
    """
    # ',' at the end of the line is important!
    print("% 3.1f%% of %.2f MB\r" % (min(100, float(a * b) / c * 100), c/1000000.)),
    
def download_HRRR(DATE,
                  model='hrrr',
                  field='sfc',
                  hour=range(0, 24),
                  fxx=range(0, 1),
                  OUTDIR='./'):
    """
    Downloads from the University of Utah MesoWest HRRR archive
    Input:
        DATE   - A date object for the model run you are downloading from.
        model  - The model type you want to download. Default is 'hrrr'
                 Model Options are ['hrrr', 'hrrrX','hrrrak']
        field  - Variable fields you wish to download. Default is sfc, surface.
                 Options are fields ['prs', 'sfc','subh', 'nat']
        hour   - Range of model run hours. Default grabs all hours of day.
        fxx    - Range of forecast hours. Default grabs analysis hour (f00).
        OUTDIR - Directory to save the files.

    Outcome:
        Downloads the desired HRRR file and renames with date info preceeding
        the original file name (i.e. 20170101_hrrr.t00z.wrfsfcf00.grib2)
    """
    
    # Check if the outdir exists. If not, create it.
    if not os.path.exists(SAVEDIR):
        os.makedirs(SAVEDIR)

    # Loop through each hour and each forecast and download.
    for h in hour:
        for f in fxx:
            # 1) Build the URL string we want to download.
            #    fname is the file name in the format
            #    [model].t[hh]z.wrf[field]f[xx].grib2
            #    i.e. hrrr.t00z.wrfsfcf00.grib2
            fname = "%s.t%02dz.wrf%sf%02d.grib2" % (model, h, field, f)
            URL = "https://pando-rgw01.chpc.utah.edu/%s/%s/%s/%s" \
                   % (model, field, DATE.strftime('%Y%m%d'), fname)

            # 2) Rename file with date preceeding original filename
            #    i.e. 20170105_hrrr.t00z.wrfsfcf00.grib2
            rename = "%s_%s" \
                     % (DATE.strftime('%Y%m%d'), fname)

            # 3) Download the file via https
            # Check the file size, make it's big enough to exist.
            check_this = urllib.request.urlopen(URL)
            file_size = int(check_this.info()['content-length'])
            if file_size > 10000:
                print("Downloading:", URL)
                urllib.request.urlretrieve(URL, OUTDIR+rename, reporthook)
                print("\n")
            else:
                # URL returns an "Key does not exist" message
                print("ERROR:", URL, "Does Not Exist")

            # 4) Sleep five seconds, as a courtesy for using the archive.
            commande_cp = 'aws s3 cp %s%s s3://jedi-pub/remi/' % (OUTDIR,rename)
            os.system(commande_cp)
            commande_rm = 'rm %s%s' % (OUTDIR,rename)
            os.system(commande_rm)
            time.sleep(25)
            
            
            
            
# Fast download of HRRR grib2 files (single variable) with multithreading
# import some additional modules
from queue import Queue
from threading import Thread

def worker():
    # This is where the main download function is run.
    # Change the hour and fxx parameters here if needed.
    while True:
        item = q.get()
        # Unpack the date and variable from the item sent to this worker
        iDATE = item
        download_HRRR(iDATE, model, field, hours, fxx, OUTDIR=SAVEDIR)
        q.task_done()



hours = np.arange(2,24)
fxx = [0]
field = sys.argv[1]
model = 'hrrr'
SAVEDIR = './grib2_files_directory/'



# ===== User Modify the Variables and date range ==========================
sDATE = date(2017, 1, 1)          # Start date
eDATE = date(2017, 12, 31)          # End date (exclusive)
# =========================================================================

# Create list of dates to request
days = (eDATE-sDATE).days
DATES = [sDATE + timedelta(days=d) for d in range(days)]

# Make a list of inputs to send to the worker
input_list = [d for d in DATES]
#input_list = [DATE]


num_of_threads = 8
q = Queue()
for i in range(num_of_threads):
    t = Thread(target=worker)
    t.daemon = True
    t.start()

# Run each item through the threads
for item in input_list:
    q.put(item)


q.join() # block until all tasks are done
            
            
            
            
       
            
    

    