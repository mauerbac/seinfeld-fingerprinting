'''
Matt Auerbach
CS591
Final Project
Spring 2014

Sources: Matplotlib, Pylab, Numpy, Dejavu (https://github.com/worldveil/dejavu)

Run with Python 2.7

Main.py

'''

#Math Libraries 
from cmath import exp
from math import cos, sin, pi
import array
import contextlib
import wave
import cmath
import copy
import numpy as np
import hashlib
import matplotlib


#Additional libraries
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from pylab import show, cm, plot,subplot,specgram, savefig
from matplotlib import pyplot as plt
from scipy.signal import lfilter, firwin

from scipy.ndimage.filters import maximum_filter
from scipy.ndimage.morphology import (generate_binary_structure,
                                      iterate_structure, binary_erosion)

import db
import hashlib


#function to read waves
def readwav(fname):
    with contextlib.closing(wave.open(fname)) as f:
        params = f.getparams()
        frames = f.readframes(params[3])
        numFrames=len(frames)
    return array.array("h", frames), params
    #return frames

#function to write waves
def writewav(fname, data, params):
    with contextlib.closing(wave.open(fname, "w")) as f:
        f.setparams(params)
        f.writeframes(data.tostring())
    print(fname + " written.")
    
#take fft of values
def fft(x):
    N = len(x)
    if N <= 1: return x
    even = fft(x[0::2])
    odd =  fft(x[1::2])
    return [even[k] + exp(-2j*pi*k/N)*odd[k] for k in range(int(N/2))] + \
           [even[k] - exp(-2j*pi*k/N)*odd[k] for k in range(int(N/2))]

'''
def getspectrogram(x):
    ansList=[]
    samples=len(x)
    W=4096 
    N=2048
    #print(math.floor(samples/N))
    for i in range(0,int(math.floor(samples/N))):
        inp= x[i*N:(i*N)+W]

        if len(inp) < W:
            break

        ans= fft(inp)

        ansList.append(ans)
    return ansList
'''


#uses pylab to get spectrogram
def getspectrogram(data,windowSize,sampleRate,overlap):
    return specgram(data,NFFT=windowSize,Fs=sampleRate,noverlap=overlap)

#low pass filter
def lowPassFilter(data,sampleRate):
    #cut off 5000hz 
    freqCutOff=5000
    nyquist=sampleRate/2

    print nyquist

    #lowPassFIR = firwin(92,cutoff=freqCutOff, nyq=nyquist)
    lowPassFIR = firwin(92,cutoff=freqCutOff)

    filteredData = lfilter(lowPassFIR, 1.0, data)

    return filteredData


#function to write waves
def writeWave(data):
    data1 = array.array("h")
    for i in data:
        i= math.floor(i)
        if i < -30000:
            i=-3000
        elif i> 32000:
            i=32000
        data1.append(long(i))
    params = [1, 2, 44100 , len(data1), "NONE", None]
    writewav("test.wav", data1, params)


def get_2D_peaks(arr2D, plot=False, amp_min=10):
    # http://docs.scipy.org/doc/scipy/reference/generated/scipy.ndimage.morphology.iterate_structure.html#scipy.ndimage.morphology.iterate_structure
    struct = generate_binary_structure(2, 1)
    neighborhood = iterate_structure(struct, 20)

    # find local maxima using our fliter shape
    local_max = maximum_filter(arr2D, footprint=neighborhood) == arr2D
    background = (arr2D == 0)
    eroded_background = binary_erosion(background, structure=neighborhood,
                                       border_value=1)

    # Boolean mask of arr2D with True at peaks
    detected_peaks = local_max - eroded_background

    # extract peaks
    amps = arr2D[detected_peaks]
    j, i = np.where(detected_peaks)

    # filter peaks
    amps = amps.flatten()
    peaks = zip(i, j, amps)
    peaks_filtered = [x for x in peaks if x[2] > amp_min]  # freq, time, amp

    # get indices for frequency and time
    frequency_idx = [x[1] for x in peaks_filtered]
    time_idx = [x[0] for x in peaks_filtered]

    '''
    if plot:
        # scatter of the peaks
        fig, ax = plt.subplots()
        ax.imshow(arr2D)
        ax.scatter(time_idx, frequency_idx)
        ax.set_xlabel('Time')
        ax.set_ylabel('Frequency')
        ax.set_title("Spectrogram")
        plt.gca().invert_yaxis()
        plt.show()
    '''

    return zip(frequency_idx, time_idx)

#Take from Dejavu
def compute_hashes(peaks, fan_value=15):

    IDX_FREQ_I = 0
    IDX_TIME_J = 1

    MIN_HASH_TIME_DELTA = 0
    MAX_HASH_TIME_DELTA = 200

    fingerprinted = set()  # to avoid rehashing same pairs

    for i in range(len(peaks)):
        for j in range(1, fan_value):
            if (i + j) < len(peaks) and not (i, i + j) in fingerprinted:
                freq1 = peaks[i][IDX_FREQ_I]
                freq2 = peaks[i + j][IDX_FREQ_I]

                t1 = peaks[i][IDX_TIME_J]
                t2 = peaks[i + j][IDX_TIME_J]

                t_delta = t2 - t1

                if t_delta >= MIN_HASH_TIME_DELTA and t_delta <= MAX_HASH_TIME_DELTA:
                    h = hashlib.sha1(
                        "%s|%s|%s" % (str(freq1), str(freq2), str(t_delta)))
                    yield (h.hexdigest()[0:20], t1)


                # ensure we don't repeat hashing
                fingerprinted.add((i, i + j))
    #print fingerprinted



def main():
    #Constants
    windowSize=4096
    sampleRate=44100
    overlap=2048
    fan_value=15

    epNum=0

    choice=input("Press 1 to fingerprint and 2 to recognize ")

    if choice == 1:
        epNum=input("Enter episode num")

    #ask user for input
    infileName = raw_input("Enter the name of the input .wav file: ")

    #Get data from input
    data, params = readwav(infileName)


    print "Applying Low Pass Filter"

    #1 Apply Low Pass Filter(<5000 Hz)
    filteredData= lowPassFilter(data,sampleRate)

    print "Finished Low Pass Filter"

    print "Processing Spectrogram"

    #G get spectrogram 
    spectrogram=getspectrogram(filteredData,windowSize,sampleRate,overlap)
    freqs=spectrogram[1]
    times=spectrogram[2]
    img=spectrogram[3]

    print "Finshed Spectrogram"


    arr2D = 10 * np.log10(spectrogram[0])
    arr2D[arr2D == -np.inf] = 0  

    print "Finding local Maxima/Peak Picking"
    local_maxima = get_2D_peaks(arr2D, plot=False, amp_min=10)
    print "Fininshed Peak picking"

    print "Compute hashes"
    hashes= compute_hashes(local_maxima, fan_value=fan_value)

    print "Done hashes"


    if choice == 1:


        result = set(hashes)

        print "Insert hases into DB"

        db.insert(epNum,result)

        print "Finshed"


    else:
        #recognize
        print "Finding Matches with hashes"

        match={}
        matches= db.lookup(hashes)
        for i in matches:
            sid, difference= i
            if sid not in match:
                match[sid]=1
            else:
                match[sid]+=1


        print "Matches Dict",
        print match
        print "Most common Episode Id",
        #get higest episode
        if len(match) > 0:  
            newSid=max(match, key=match.get)
            print newSid
        else:
            print "No Matches"
            return 0


        # extract idenfication
        episode = db.songTOID(newSid)[0]

        print "------- The Episode: ",
        print episode


        return episode



if __name__ == "__main__":
    main()





