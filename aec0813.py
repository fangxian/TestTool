from matplotlib import pyplot as plt
import numpy as np
import wave
import os

path = os.getcwd() + "\\wave\\linear.wav"

plt.rcParams['font.sans-serif'] = ['Microsoft YaHei']

file_h = wave.open(path)

params = file_h.getparams()

fs = params.framerate

frames_n = params.nframes

nchannels = params.nchannels

far = np.fromstring(file_h.readframes(frames_n), dtype = np.short)

file_h = wave.open(path)


far = far.T / 10000

M = len(far)

N = 240  #每次取的点数

print("Far audio length is %d, near audio length is %d"%(M,N))


voice = np.zeros(M)
voice[0:M-2000] = far[2000:M]

plt.figure()
plt.plot(far)
plt.show()