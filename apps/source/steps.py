import numpy as np
from scipy.signal import argrelextrema



def find_heelstrikes_from_z(segments):
    neighbors = 15

    heelstrikes = []
    for seg in segments:
        heelstrikes.append(argrelextrema(seg["Z"].values, np.less, order=neighbors)[0])  # np.less for minima

    return heelstrikes

