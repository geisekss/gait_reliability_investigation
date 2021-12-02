
"""
Generate frames for the trajectories and accelerations of the Multi-sensor Gait Dataset.
It reads the capture sessions in the 'processed_folder' folder, and section them in frames using a sliding window of 256 samples and overlaping of 75%.
These frames can be filtered by a low-pass, high-pass or band-pass filters given cuttof frequencies.
"""

from glob import glob
import os, math, argparse
import numpy as np
from scipy.signal import lfilter, firwin, butter
import matplotlib.pyplot as plt

WINDOW = 256
STEP = 32

def zero_pole_filter(f, fs):
    w = (2*math.pi*f)/fs
    r = 0.9
    z0 = [math.cos(w), math.sin(w)]
    zp = [r*math.cos(w), r*math.sin(w)]
    b = [1, -2*z0[0], (z0[0]*z0[0])+(z0[1]*z0[1])]
    a = [1, -2*zp[0], (zp[0]*zp[0])+(zp[1]*zp[1])]
    return b, a

def remove_bias_filter(data, Fs):
    ndata = np.copy(data)
    b, a =  zero_pole_filter(0, Fs)
    for i in range(data.shape[1]):
        ndata[:, i] = lfilter(b, a, ndata[:, i])
    return ndata

def low_pass_filter(data, Fs, lowcut):
    ndata = np.copy(data)
    b, a = butter(6, lowcut, btype='low', fs=100)
    for i in range(data.shape[1]):
        ndata[:, i] = lfilter(b, a, ndata[:, i])
    return ndata

def band_pass_filter(data, Fs, blow, bhigh):
    ndata = np.copy(data)
    b, a = butter(6, [blow, bhigh], btype='bandpass', fs=100)
    for i in range(data.shape[1]):
        ndata[:, i] = lfilter(b, a, ndata[:, i])
    return ndata

def high_pass_filter(data, Fs, highcut):
    ndata = np.copy(data)
    b, a = butter(6, highcut, btype='high', fs=100)
    for i in range(data.shape[1]):
        ndata[:, i] = lfilter(b, a, ndata[:, i])
    return ndata


parser = argparse.ArgumentParser()
parser.add_argument("-p", "--path", default=None, required=True, type=str, help="Path to store the generated frames")
parser.add_argument("-d", "--dc", default=False, type=bool, help="Wether remove or not the DC component from signals")
parser.add_argument("-t", "--typefilter", default=None, type=str, help="Filter type: band-pass, low-pass, high-pass")
parser.add_argument("-f", "--frequency", default=None, nargs="+", type=int, help="Cuttof frequency, for the band-pass filter pass lf hf]")
args = parser.parse_args()


users = sorted(glob("csv_files/*/"))
if(not os.path.isdir(args.path)):
    os.mkdir(args.path)

u = users[0]
files_csv = sorted(glob(u+"*.csv"))
dic_data = {os.path.basename(f).split('_')[4]: np.empty((0, WINDOW+2)) for f in files_csv}

for u in users:
    user = int(u.split('/')[-2].split('user')[-1])
    files_csv = sorted(glob(u+"*_fle_*_qtm_walk.csv")+glob(u+"*_fax_*_qtm_walk.csv")+glob(u+"*imu_walk.csv")+glob(u+"*nexus_walk.csv"))
    files_csv = sorted(list(set(glob(u+"*.csv"))))
    for f in files_csv:
        parts_f = os.path.basename(f).split('_')
        key = parts_f[4]
        if(len(parts_f) > 6 and parts_f[6] == 'acc'):
            key += '_acc'
        day = int(parts_f[2][-1])
        if(key=='imu'):
            data = np.loadtxt(f, delimiter=',', skiprows=1, usecols=(1,2,3)) 
            if(args.dc):
                data = data - np.mean(data, axis=0)
                data = data[100:]
        elif(key=='nexus'):
            data = np.loadtxt(f, delimiter=',', skiprows=1)
            if(args.dc):
                data = data - np.mean(data, axis=0)
                data = data[100:]
        else:
            data = np.loadtxt(f, delimiter=',')
            if(args.dc):
                data = remove_bias_filter(data, 100)[100:]

        if(args.typefilter != None):
            freq = args.frequency
            if(args.typefilter == 'low-pass'):
                dataf = low_pass_filter(data, 100, freq)
            elif(args.typefilter == 'high-pass'):
                dataf = high_pass_filter(data, 100, freq)
            elif(args.typefilter == 'band-pass' and isinstance(freq, list)):
                dataf = band_pass_filter(data, 100, freq[0], freq[1])
            else:
                print("Filter type or cuttof frequency not valid")
                exit(0)
            data = np.copy(dataf)

        frames = np.array([data[i:i+WINDOW, -1]*np.hamming(WINDOW) for i in range(0, len(data)-WINDOW, STEP)])
        labels = np.hstack(( np.full((len(frames), 1), user), np.full((len(frames), 1), day) ))
        dic_data[key] = np.vstack((dic_data[key], np.hstack((labels, frames))))

_ = [np.savetxt(args.path+"/frames_"+key+".csv", dic_data[key], delimiter=',', fmt="%.6f") for key in dic_data]

