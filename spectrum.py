import numpy as np

import copy
import os
currentPath = os.getcwd() + '\\data'
PlotDataAdc = np.zeros(8352)
fp = open(currentPath + "\\data3.bin", "rb")

def testReadFile():
    # return self.fp.read()
    data = fp.read(1536)
    PlotDataAdc[0:1392] = copy.deepcopy(np.frombuffer(data[8:1400], dtype=np.uint8))


    data = fp.read(1536)
    PlotDataAdc[1392:1392 * 2] = copy.deepcopy(np.frombuffer(data[8:1400], dtype=np.uint8))


    data = fp.read(1536)
    PlotDataAdc[1392 * 2:1392 * 3] = copy.deepcopy(np.frombuffer(data[8:1400], dtype=np.uint8))


    data = fp.read(1536)
    PlotDataAdc[1392 * 3:1392 * 4] = copy.deepcopy(np.frombuffer(data[8:1400], dtype=np.uint8))


    data = fp.read(1536)
    PlotDataAdc[1392 * 4:1392 * 5] = copy.deepcopy(np.frombuffer(data[8:1400], dtype=np.uint8))

    data = fp.read(1536)
    PlotDataAdc[1392 * 5:1392 * 6] = copy.deepcopy(np.frombuffer(data[8:1400], dtype=np.uint8))

    return PlotDataAdc

for i in range(1000):
    PlotDataAdc= testReadFile()

    fft_result = np.ones((4, 256, 256))

    fft_result[:, 0:255, :] = fft_result[:, 1:256, :]
    fft_raw = PlotDataAdc[0:8192]
# print("---------%d %d %d"%(b,a,temp_a))
    fft_raw = fft_raw.reshape((4096, 2))
    fft_raw = fft_raw[:, 0] * 256 + fft_raw[:, 1]
    fft_raw = fft_raw.reshape(512, 8)
    fft_result[0, 255, :] = 20 * np.log(np.abs((np.fft.fft(fft_raw[:, 0])[0:256])))
    fft_result[1, 255, :] = 20 * np.log(np.abs((np.fft.fft(fft_raw[:, 1])[0:256])))
    fft_result[2, 255, :] = 20 * np.log(np.abs((np.fft.fft(fft_raw[:, 2])[0:256])))
    fft_result[3, 255, :] = 20 * np.log(np.abs((np.fft.fft(fft_raw[:, 3])[0:256])))

    canvas1raw[0:256, 0:256] = (self.fft_result[0, :, :] - np.min(self.fft_result[0, :, :])).T
    canvas1raw[300:556, 0:256] = (self.fft_result[1, :, :] - np.min(self.fft_result[1, :, :])).T
    canvas1raw[0:256, 300:556] = (self.fft_result[2, :, :] - np.min(self.fft_result[2, :, :])).T
    canvas1raw[300:556, 300:556] = (self.fft_result[3, :, :] - np.min(self.fft_result[3, :, :])).T
    canvas1[:, :, 0] = canvas1raw * 0.114
    canvas1[:, :, 1] = canvas1raw * 0.587
    canvas1[:, :, 2] = canvas1raw * 0.299
    imgzi1 = cv.putText(canvas1, 'CH0', (120, 20), font, 0.8, (255, 255, 255), 2)
    imgzi1 = cv.putText(canvas1, 'CH1', (376, 20), font, 0.8, (255, 255, 255), 2)
    imgzi1 = cv.putText(canvas1, 'CH2', (120, 320), font, 0.8, (255, 255, 255), 2)
    imgzi1 = cv.putText(canvas1, 'CH3', (376, 320), font, 0.8, (255, 255, 255), 2)
    cv.normalize(imgzi1, imgzi1, 0, 1, cv.NORM_MINMAX);
    cv.imshow("Spetrum data", imgzi1)
    cv.waitKey(1)
