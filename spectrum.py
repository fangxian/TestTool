import numpy as np
import time
import copy
import os
import cv2 as cv
import matplotlib.pyplot as plt
import threading
currentPath = os.getcwd()
PlotDataAdc = np.zeros(8352)
fp = open(currentPath + "\\data3.bin", "rb")
canvas = np.ones((800, 1536), dtype="uint8")
canvas1 = np.ones((600, 600, 3))
canvas1raw = np.ones((600, 600))
font = cv.FONT_HERSHEY_SIMPLEX

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
plt.ion()
fft_result = np.ones((4, 256, 256))
fig, (ax0,ax1,ax2,ax3) = plt.subplots(1, 4)

fig.show()

#plt.axes("off")
def showData():
    count = 0
    for i in range(100000):
        count += 1

        PlotDataAdc = testReadFile()
        fft_result[:, 0:255, :] = fft_result[:, 1:256, :]
        fft_raw = PlotDataAdc[100:8292]
        # print("---------%d %d %d"%(b,a,temp_a))
        fft_raw = fft_raw.reshape((4096, 2))
        fft_raw = fft_raw[:, 0] * 256 + fft_raw[:, 1]
        fft_raw = fft_raw.reshape(512, 8)
        fft_result[0, 255, :] = 20 * np.log(np.abs((np.fft.fft(fft_raw[:, 0])[0:256])))
        fft_result[1, 255, :] = 20 * np.log(np.abs((np.fft.fft(fft_raw[:, 1])[0:256])))
        fft_result[2, 255, :] = 20 * np.log(np.abs((np.fft.fft(fft_raw[:, 2])[0:256])))
        fft_result[3, 255, :] = 20 * np.log(np.abs((np.fft.fft(fft_raw[:, 3])[0:256])))

        canvas1raw[0:256, 0:256] = (fft_result[0, :, :] - np.min(fft_result[0, :, :])).T
        canvas1raw[300:556, 0:256] = (fft_result[1, :, :] - np.min(fft_result[1, :, :])).T
        canvas1raw[0:256, 300:556] = (fft_result[2, :, :] - np.min(fft_result[2, :, :])).T
        canvas1raw[300:556, 300:556] = (fft_result[3, :, :] - np.min(fft_result[3, :, :])).T
        if count == 255:
            start = time.time()
            ax0.axis("off")
            ax1.axis("off")
            ax2.axis("off")
            ax3.axis("off")
            ax0.set_title("CH1")
            ax1.set_title("CH2")
            ax2.set_title("CH3")
            ax3.set_title("CH4")
            ax0.pcolormesh(canvas1raw[0:256, 0:256], cmap=plt.cm.jet)
            ax1.pcolormesh(canvas1raw[300:556, 0:256], cmap=plt.cm.jet)
            ax2.pcolormesh(canvas1raw[0:256, 300:556], cmap=plt.cm.jet)
            ax3.pcolormesh(canvas1raw[300:556, 300:556], cmap=plt.cm.jet)
            #plt.pcolor(canvas1raw, cmap=plt.cm.jet)
            #plt.show()
            plt.pause(0.01)
            count = 0
            #fig.clf()
            ax0.cla()
            ax1.cla()
            ax2.cla()
            ax3.cla()


            end = time.time()
            print(end-start)
        # plt.pcolor(canvas1raw)

        '''
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
        '''
if __name__ == "__main__":
    showData()
    #cvThread = threading.Thread(target=showData)
    #cvThread.start()
    #cvThread.join()