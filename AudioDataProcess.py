import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import cv2 as cv
import os, time
import copy
from concurrent.futures import ThreadPoolExecutor
import wave
import matplotlib.animation as animation
import pyqtgraph as pg

matplotlib.use('TkAgg')
currentPath = os.getcwd()
DrawMax = np.zeros((4), dtype=np.uint16)
DrawMin = np.zeros((4), dtype=np.uint16)
ZoomFactor = np.zeros(4)
tempmax = np.zeros(4)
fftDrawMax = 0
fftZoomFactor = 0
font = cv.FONT_HERSHEY_SIMPLEX
fft_result = np.ones((4, 256, 256))
first_time = 1


def adcRun(constInt1, ZoomFactor, raw2, constInt2):
    adc_x = np.zeros(512)
    adc_y = np.zeros(512)
    for i in range(512):
        adc_x[i] = i
        adc_y[i] = constInt1 - int(ZoomFactor[0] * raw2[i, constInt2])
    return adc_x, adc_y


def fftRun(constInt1, fftZoomFactor, fft):
    fft_x = np.zeros(256)
    fft_y = np.zeros(256)
    for i in range(256):
        fft_x[i] = i
        fft_y[i] = constInt1 - int(fftZoomFactor * fft[i])
    return fft_x, fft_y


def drawImage(q, runThread, hasData):
    # plt.figure()
    # plt.ion()
    # specFig = plt.figure()
    fig, axes = plt.subplots(2, 4)
    adc_x = []
    adc_y = []
    fft_x = []
    fft_y = []
    lines = []
    for i in range(4):
        adc_x.append(np.zeros(512))
        adc_y.append(np.zeros(512))
        fft_x.append(np.zeros(256))
        fft_y.append(np.zeros(256))

    # draw the canvas and lines
    for i in range(2):
        for j in range(4):
            if i < 1:
                lines.append(axes[i, j].plot(adc_x[j], adc_y[j])[0])
                axes[i, j].set_title("adc" + str(j))
                axes[i, j].axis('off')
                axes[i, j].set_xlim((0, 512))
                axes[i, j].set_ylim((0, 800))
            else:
                lines.append(axes[i, j].plot(fft_x[j], fft_y[j])[0])
                axes[i, j].set_title("fft" + str(j))
                axes[i, j].axis('off')
                axes[i, j].set_xlim((0, 256))
                axes[i, j].set_ylim((0, 800))

    fig.show()
    fig.canvas.draw()
    backgrounds = []
    for i in range(2):
        for j in range(4):
            backgrounds.append(fig.canvas.copy_from_bbox(axes[i, j].bbox))
    threadPool = ThreadPoolExecutor(max_workers=4, thread_name_prefix="test_")
    count = 0
    start = time.time()
    while runThread.value == 1:
        if hasData.value == 1:
            PlotDataAdc = q.get()
            count = count + 1
            hasData.value = 0
            raw0 = PlotDataAdc.reshape((4176, 2))
            raw1 = (raw0[:, 1] * 256 + raw0[:, 0])[0:4096]
            raw1[raw1 > 32767] -= 65536
            raw1 += 32768
            raw2 = raw1.reshape((512, 8))
            for i in range(4):
                DrawMax[i] = np.max(raw2[:, i])
                DrawMin[i] = np.min(raw2[:, i])
                raw2[:, i] = raw2[:, i] - DrawMin[i]
                ZoomFactor[i] = 300 / (DrawMax[i] - DrawMin[i])

            fft0 = 20 * np.log(np.abs(np.fft.fft(raw2[:, 0])[0:256]) + 1)
            fft1 = 20 * np.log(np.abs(np.fft.fft(raw2[:, 1])[0:256]) + 1)
            fft2 = 20 * np.log(np.abs(np.fft.fft(raw2[:, 2])[0:256]) + 1)
            fft3 = 20 * np.log(np.abs(np.fft.fft(raw2[:, 3])[0:256]) + 1)
            tempmax[0] = np.max(fft0)
            tempmax[1] = np.max(fft1)
            tempmax[2] = np.max(fft2)
            tempmax[3] = np.max(fft3)
            fftDrawMax = np.max(tempmax)
            fftZoomFactor = 300 / fftDrawMax

            # get the point axis
            adc_x[0], adc_y[0] = threadPool.submit(adcRun, 300, ZoomFactor, raw2, 0).result()
            adc_x[1], adc_y[1] = threadPool.submit(adcRun, 300, ZoomFactor, raw2, 1).result()
            adc_x[2], adc_y[2] = threadPool.submit(adcRun, 700, ZoomFactor, raw2, 2).result()
            adc_x[3], adc_y[3] = threadPool.submit(adcRun, 700, ZoomFactor, raw2, 3).result()
            fft_x[0], fft_y[0] = threadPool.submit(fftRun, 300, fftZoomFactor, fft0).result()
            fft_x[1], fft_y[1] = threadPool.submit(fftRun, 300, fftZoomFactor, fft1).result()
            fft_x[2], fft_y[2] = threadPool.submit(fftRun, 700, fftZoomFactor, fft2).result()
            fft_x[3], fft_y[3] = threadPool.submit(fftRun, 700, fftZoomFactor, fft3).result()

            # set new adc data
            for i in range(4):
                fig.canvas.restore_region(backgrounds[i])
                lines[i].set_data(adc_x[i], adc_y[i])
                axes[0, i].draw_artist(lines[i])
                fig.canvas.blit(axes[0, i].bbox)
            # set new fft data
            for i in range(4):
                fig.canvas.restore_region(backgrounds[i + 4])
                lines[i + 4].set_data(fft_x[i], fft_y[i])
                axes[1, i].draw_artist(lines[i + 4])
                fig.canvas.blit(axes[1, i].bbox)

            plt.pause(0.0000001)
        time.sleep(0.01)
    end = time.time()
    print(end - start)
    print(count)
    plt.close(fig)
    threadPool.shutdown(wait=False)


def drwaSpectrum(q, runThread, resetFlag):
    canvas1raw = np.ones((600, 600))
    plt.ion()
    fig, (ax0, ax1, ax2, ax3) = plt.subplots(1, 4)
    fig.show()
    count = 0
    while runThread.value == 1:
        if resetFlag.value == 1:
            fft_result = np.ones((4, 256, 256))
            count = 0
            resetFlag.value = 0
        if not q.empty() == 1:
            # if hasData.value == 1:
            PlotDataAdc = q.get()
            count += 1
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
                plt.pause(0.01)
                count = 0
                ax0.cla()
                ax1.cla()
                ax2.cla()
                ax3.cla()
    plt.close(fig)


def drawImage_1(q, runThread, hasData):
    fig, axes = plt.subplots(2, 4)
    adc_x = []
    adc_y = []
    fft_x = []
    fft_y = []
    lines = []
    for i in range(4):
        adc_x.append(np.zeros(512))
        adc_y.append(np.zeros(512))
        fft_x.append(np.zeros(256))
        fft_y.append(np.zeros(256))

    # draw the canvas and lines
    for i in range(2):
        for j in range(4):
            if i < 1:
                lines.append(axes[i, j].plot(adc_x[j], adc_y[j])[0])
                axes[i, j].set_title("adc" + str(j))
                axes[i, j].axis('off')
                axes[i, j].set_xlim((0, 512))
                axes[i, j].set_ylim((0, 800))
            else:
                lines.append(axes[i, j].plot(fft_x[j], fft_y[j])[0])
                axes[i, j].set_title("fft" + str(j))
                axes[i, j].axis('off')
                axes[i, j].set_xlim((0, 256))
                axes[i, j].set_ylim((0, 800))

    threadPool = ThreadPoolExecutor(max_workers=4, thread_name_prefix="test_")
    count = 0
    while runThread.value == 1:
        if hasData.value == 1:
            # if not q.empty():
            PlotDataAdc = q.get()
            count = count + 1
            hasData.value = 0
            raw0 = PlotDataAdc.reshape((4176, 2))
            raw1 = (raw0[:, 1] * 256 + raw0[:, 0])[0:4096]
            raw1[raw1 > 32767] -= 65536
            raw1 += 32768
            raw2 = raw1.reshape((512, 8))
            for i in range(4):
                DrawMax[i] = np.max(raw2[:, i])
                DrawMin[i] = np.min(raw2[:, i])
                raw2[:, i] = raw2[:, i] - DrawMin[i]
                ZoomFactor[i] = 300 / (DrawMax[i] - DrawMin[i])

            fft0 = 20 * np.log(np.abs(np.fft.fft(raw2[:, 0])[0:256]) + 1)
            fft1 = 20 * np.log(np.abs(np.fft.fft(raw2[:, 1])[0:256]) + 1)
            fft2 = 20 * np.log(np.abs(np.fft.fft(raw2[:, 2])[0:256]) + 1)
            fft3 = 20 * np.log(np.abs(np.fft.fft(raw2[:, 3])[0:256]) + 1)
            tempmax[0] = np.max(fft0)
            tempmax[1] = np.max(fft1)
            tempmax[2] = np.max(fft2)
            tempmax[3] = np.max(fft3)
            fftDrawMax = np.max(tempmax)
            fftZoomFactor = 300 / fftDrawMax

            # get the point axis
            adc_x[0], adc_y[0] = threadPool.submit(adcRun, 300, ZoomFactor, raw2, 0).result()
            adc_x[1], adc_y[1] = threadPool.submit(adcRun, 300, ZoomFactor, raw2, 1).result()
            adc_x[2], adc_y[2] = threadPool.submit(adcRun, 700, ZoomFactor, raw2, 2).result()
            adc_x[3], adc_y[3] = threadPool.submit(adcRun, 700, ZoomFactor, raw2, 3).result()
            fft_x[0], fft_y[0] = threadPool.submit(fftRun, 300, fftZoomFactor, fft0).result()
            fft_x[1], fft_y[1] = threadPool.submit(fftRun, 300, fftZoomFactor, fft1).result()
            fft_x[2], fft_y[2] = threadPool.submit(fftRun, 700, fftZoomFactor, fft2).result()
            fft_x[3], fft_y[3] = threadPool.submit(fftRun, 700, fftZoomFactor, fft3).result()

            # set new adc data
            for i in range(4):
                lines[i].set_data(adc_x[i], adc_y[i])

            # set new fft data
            for i in range(4):
                lines[i + 4].set_data(fft_x[i], fft_y[i])
            plt.pause(0.0000001)
            # plt.show()
        time.sleep(0.01)
    plt.close(fig)


def compareWaveFileSpec(files):
    for i in range(len(files)):
        fp = wave.open(files[i], "rb")
        params1 = fp.getparams()
        nchannels, sampwidth, framerate, nframes = params1[:4]
        str_data = fp.readframes(nframes)
        fp.close()
        wave_data = np.fromstring(str_data, dtype=np.short)
        wave_data = wave_data.T / 1000
        plt.subplot(len(files), 1, 1 + i)
        plt.title(files[i].split("/")[-1])
        plt.plot(wave_data)

    plt.show()


def saveData(dataQueue, threadRun):
    pass


class DataShow:
    def __init__(self, AudioTool):
        self.fp = open(currentPath + "\\data3.bin", "rb")
        self.audioTool = AudioTool
        self.PlotDataAdc = np.zeros(8352)
        self.ReceivePingPong = np.zeros((2, 92160144), dtype=np.uint8)
        self.count = 0
        self.indexMMic = 0
        self.dataIndex = 0

        self.indexBMic = 0

    def __del__(self):
        self.fp.close()

    def serialRead(self):
        pass

    # TODO to change len if board data length is different with mmic
    def storeAecBMicData(self, data, len):
        self.audioTool.receiveBMicPingPong[self.audioTool.recviveBMicFlag][
        self.indexBMic * len:len * (self.indexBMic + 1)] = copy.deepcopy(np.frombuffer(data, dtype=np.uint8))
        if self.audioTool.isAECCase is True and self.audioTool.isAECRT is True:
            self.audioTool.aecBMicQ.put(self.audioTool.receiveBMicPingPong[self.audioTool.recviveBMicFlag][
                                        self.indexBMic * len:len * (self.indexBMic + 1)])
        self.indexBMic += 1
        if self.indexBMic == 66207:
            if self.audioTool.recviveBMicFlag == 0:
                self.audioTool.recviveBMicFlag = 1
                self.audioTool.storeBMicFlag = 0
            elif self.audioTool.recviveBMicFlag == 1:
                self.audioTool.recviveBMicFlag = 0
                self.audioTool.storeBMicFlag = 1
            self.indexBMic = 0

    def storeCollectData(self, data, len):
        self.PlotDataAdc[self.dataIndex * len:(self.dataIndex + 1) * len] = copy.deepcopy(
            np.frombuffer(data, dtype=np.uint8))
        self.audioTool.receiveMMicPingPong[self.audioTool.recviveMMicFlag][
        self.indexMMic * len:len * (self.indexMMic + 1)] = copy.deepcopy(np.frombuffer(data, dtype=np.uint8))
        if self.audioTool.isAECCase is True and self.audioTool.isAECRT is True:
            self.audioTool.aecMMicQ.put(self.PlotDataAdc[self.dataIndex * len:(self.dataIndex + 1) * len])

        self.dataIndex += 1
        self.indexMMic += 1
        if self.indexMMic == 66207:
            if self.audioTool.recviveMMicFlag == 0:
                self.audioTool.recviveMMicFlag = 1
                self.audioTool.storeMMicFlag == 0
            elif self.audioTool.recviveMMicFlag == 1:
                self.audioTool.recviveMMicFlag = 0
                self.audioTool.storeMMicFlag == 1
            self.indexMMic = 0

        if self.dataIndex == 6:
            self.dataIndex = 0
            if self.count != 5:
                self.count = self.count + 1
                return None
            self.count = 0
            return self.PlotDataAdc

        return None

    def testReadFile(self):
        # return self.fp.read()
        data = self.fp.read(1536)
        self.PlotDataAdc[0:1392] = copy.deepcopy(np.frombuffer(data[8:1400], dtype=np.uint8))
        self.audioTool.receiveMMicPingPong[self.audioTool.recviveMMicFlag][
        self.indexMMic * 1392:1392 * (self.indexMMic + 1)] = copy.deepcopy(np.frombuffer(data[8:1400], dtype=np.uint8))
        self.indexMMic += 1

        data = self.fp.read(1536)
        self.PlotDataAdc[1392:1392 * 2] = copy.deepcopy(np.frombuffer(data[8:1400], dtype=np.uint8))
        self.audioTool.receiveMMicPingPong[self.audioTool.recviveMMicFlag][
        self.indexMMic * 1392:1392 * (self.indexMMic + 1)] = copy.deepcopy(np.frombuffer(data[8:1400], dtype=np.uint8))
        self.indexMMic += 1

        data = self.fp.read(1536)
        self.PlotDataAdc[1392 * 2:1392 * 3] = copy.deepcopy(np.frombuffer(data[8:1400], dtype=np.uint8))
        self.audioTool.receiveMMicPingPong[self.audioTool.recviveMMicFlag][
        self.indexMMic * 1392:1392 * (self.indexMMic + 1)] = copy.deepcopy(np.frombuffer(data[8:1400], dtype=np.uint8))
        self.indexMMic += 1

        data = self.fp.read(1536)
        self.PlotDataAdc[1392 * 3:1392 * 4] = copy.deepcopy(np.frombuffer(data[8:1400], dtype=np.uint8))
        self.audioTool.receiveMMicPingPong[self.audioTool.recviveMMicFlag][
        self.indexMMic * 1392:1392 * (self.indexMMic + 1)] = copy.deepcopy(np.frombuffer(data[8:1400], dtype=np.uint8))
        self.indexMMic += 1

        data = self.fp.read(1536)
        self.PlotDataAdc[1392 * 4:1392 * 5] = copy.deepcopy(np.frombuffer(data[8:1400], dtype=np.uint8))
        self.audioTool.receiveMMicPingPong[self.audioTool.recviveMMicFlag][
        self.indexMMic * 1392:1392 * (self.indexMMic + 1)] = copy.deepcopy(np.frombuffer(data[8:1400], dtype=np.uint8))
        self.indexMMic += 1

        data = self.fp.read(1536)
        self.PlotDataAdc[1392 * 5:1392 * 6] = copy.deepcopy(np.frombuffer(data[8:1400], dtype=np.uint8))
        self.audioTool.receiveMMicPingPong[self.audioTool.recviveMMicFlag][
        self.indexMMic * 1392:1392 * (self.indexMMic + 1)] = copy.deepcopy(np.frombuffer(data[8:1400], dtype=np.uint8))
        self.indexMMic += 1

        if self.indexMMic == 10000:
            if self.audioTool.recviveMMicFlag == 0:
                self.audioTool.recviveMMicFlag = 1
                self.audioTool.storeMMicFlag == 0
            elif self.audioTool.recviveMMicFlag == 1:
                self.audioTool.recviveMMicFlag = 0
                self.audioTool.storeMMicFlag == 1

        if self.count != 3:
            self.count = self.count + 1
            return None

        self.count = 0
        return self.PlotDataAdc

    def reset(self):
        self.count = 0
        self.indexMMic = 0
        self.indexBMic = 0
        self.dataIndex = 0

    def dataProcess(self, data):
        pass
