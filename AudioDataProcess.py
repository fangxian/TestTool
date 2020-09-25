import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import cv2 as cv
import os, time
import copy
from concurrent.futures import ThreadPoolExecutor
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

def threadRun(constInt1, ZoomFactor, raw2, constInt2):
    adc_x = np.zeros(512)
    adc_y = np.zeros(512)
    for i in range(512):
        adc_x[i] = i
        adc_y[i] = constInt1 - int(ZoomFactor[0] * raw2[i, constInt2])
    return adc_x, adc_y

def drawImage(q, runThread, runValue):
    #plt.figure()
    #plt.ion()
    fig, axes = plt.subplots(2,4)
    threadPool = ThreadPoolExecutor(max_workers=4, thread_name_prefix="test_")
    while runThread.value == 1:
        if runValue.value == 1:
            plt.ion()
            PlotDataAdc = q.get()
            runValue.value = 0
            canvas = np.ones((800, 1536), dtype="uint8")
            canvas1 = np.ones((600, 600, 3))
            canvas1raw = np.ones((600, 600))
            raw0 = PlotDataAdc.reshape((4176, 2))
            raw1 = (raw0[:, 1] * 256 + raw0[:, 0])[0:4096]
            raw1[raw1 > 32767] -= 65536
            raw1 += 32768
            raw2 = raw1.reshape((512, 8))
            DrawMax[0] = np.max(raw2[:, 0])
            DrawMax[1] = np.max(raw2[:, 1])
            DrawMax[2] = np.max(raw2[:, 2])
            DrawMax[3] = np.max(raw2[:, 3])
            DrawMin[0] = np.min(raw2[:, 0])
            DrawMin[1] = np.min(raw2[:, 1])
            DrawMin[2] = np.min(raw2[:, 2])
            DrawMin[3] = np.min(raw2[:, 3])
            raw2[:, 0] = raw2[:, 0] - DrawMin[0]
            raw2[:, 1] = raw2[:, 1] - DrawMin[1]
            raw2[:, 2] = raw2[:, 2] - DrawMin[2]
            raw2[:, 3] = raw2[:, 3] - DrawMin[3]
            ZoomFactor[0] = 300 / (DrawMax[0] - DrawMin[0])
            ZoomFactor[1] = 300 / (DrawMax[1] - DrawMin[1])
            ZoomFactor[2] = 300 / (DrawMax[2] - DrawMin[2])
            ZoomFactor[3] = 300 / (DrawMax[3] - DrawMin[3])
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

            adc0_x = np.zeros(512)
            adc0_y = np.zeros(512)
            adc1_x = np.zeros(512)
            adc1_y = np.zeros(512)
            adc2_x = np.zeros(512)
            adc2_y = np.zeros(512)
            adc3_x = np.zeros(512)
            adc3_y = np.zeros(512)

            fft0_x = np.zeros(256)
            fft0_y = np.zeros(256)
            fft1_x = np.zeros(256)
            fft1_y = np.zeros(256)
            fft2_x = np.zeros(256)
            fft2_y = np.zeros(256)
            fft3_x = np.zeros(256)
            fft3_y = np.zeros(256)

            adc0_x, adc0_y = threadPool.submit(threadRun, 300, ZoomFactor, raw2, 0).result()
            adc1_x, adc1_y = threadPool.submit(threadRun, 300, ZoomFactor, raw2, 1).result()
            adc2_x, adc2_y = threadPool.submit(threadRun, 700, ZoomFactor, raw2, 2).result()
            adc3_x, adc3_y = threadPool.submit(threadRun, 700, ZoomFactor, raw2, 3).result()

            '''
            for i in range(512):
                adc0_x[i] = i
                adc0_y[i] = 300 - int(ZoomFactor[0] * raw2[i, 0])

                adc1_x[i] = i
                adc1_y[i] = 300 - int(ZoomFactor[1] * raw2[i, 1])

                adc2_x[i] = i
                adc2_y[i] = 700 - int(ZoomFactor[2] * raw2[i, 2])

                adc3_x[i] = i
                adc3_y[i] = 700 - int(ZoomFactor[3] * raw2[i, 3])
            '''

            for i in range(256):
                fft0_x[i] = i
                fft0_y[i] = 300 - int(fftZoomFactor * fft0[i])
                fft1_x[i] = i
                fft1_y[i] = 300 - int(fftZoomFactor * fft1[i])
                fft2_x[i] = i
                fft2_y[i] = 700 - int(fftZoomFactor * fft2[i])
                fft3_x[i] = i
                fft3_y[i] = 700 - int(fftZoomFactor * fft3[i])

            '''
            fft_raw = PlotDataAdc[0:8192]
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
            canvas1[:, :, 0] = canvas1raw * 0.114
            canvas1[:, :, 1] = canvas1raw * 0.587
            canvas1[:, :, 2] = canvas1raw * 0.299
            '''

            '''
            plt.subplot(241)
            if first_time:
                plt.title("adc0")
                plt.xlim((0, 512))
                plt.ylim((0, 800))
            plt.plot(adc0_x, adc0_y)
            plt.subplot(242)
            if first_time:
                plt.title("adc1")
                plt.xlim((0, 512))
                plt.ylim((0, 800))
            plt.plot(adc1_x, adc1_y)
            plt.subplot(243)
            if first_time:
                plt.title("adc2")
                plt.xlim((0, 512))
                plt.ylim((0, 800))
            plt.plot(adc2_x, adc2_y)
            plt.subplot(244)
            if first_time:
                plt.title("adc3")
                plt.xlim((0, 512))
                plt.ylim((0, 800))
            plt.plot(adc3_x, adc3_y)

            plt.subplot(245)
            if first_time:
                plt.title("fft0")
                plt.xlim((0, 256))
                plt.ylim((0, 800))
            plt.plot(fft0_x, fft0_y)

            plt.subplot(246)
            if first_time:
                plt.title("fft1")
                plt.xlim((0, 256))
                plt.ylim((0, 800))
            plt.plot(fft1_x, fft1_y)

            plt.subplot(247)
            if first_time:
                plt.title("fft2")
                plt.xlim((0, 256))
                plt.ylim((0, 800))
            plt.plot(fft2_x, fft2_y)

            plt.subplot(248)
            if first_time:
                plt.title("fft3")
                plt.xlim((0, 256))
                plt.ylim((0, 800))
            plt.plot(fft3_x, fft3_y)
            '''
            axes[0,0].plot(adc0_x, adc0_y)

            fig.show()
            plt.pause(0.001)
            axes[0,0].cla()

        time.sleep(0.001)
    plt.close()
    threadPool.shutdown(wait=True)


class DataShow:
    def __init__(self, AudioTool):
        self.fp = open(currentPath + "\\data2.bin", "rb")
        self.audioTool = AudioTool

        self.PlotDataAdc = np.zeros(8352)
        self.ReceivePingPong = np.zeros((2, 92160144), dtype=np.uint8)

    def __del__(self):
        self.fp.close()

    def testReadFile(self):
        # return self.fp.read()
        data = self.fp.read(1536)

        if len(data) < 1536:
            return
        self.PlotDataAdc[0:1392] = copy.deepcopy(np.frombuffer(data[8:1400], dtype=np.uint8))
        data = self.fp.read(1536)
        self.PlotDataAdc[1392:1392 * 2] = copy.deepcopy(np.frombuffer(data[8:1400], dtype=np.uint8))
        data = self.fp.read(1536)
        self.PlotDataAdc[1392 * 2:1392 * 3] = copy.deepcopy(np.frombuffer(data[8:1400], dtype=np.uint8))
        data = self.fp.read(1536)
        self.PlotDataAdc[1392 * 3:1392 * 4] = copy.deepcopy(np.frombuffer(data[8:1400], dtype=np.uint8))
        data = self.fp.read(1536)
        self.PlotDataAdc[1392 * 4:1392 * 5] = copy.deepcopy(np.frombuffer(data[8:1400], dtype=np.uint8))
        data = self.fp.read(1536)
        self.PlotDataAdc[1392 * 5:1392 * 6] = copy.deepcopy(np.frombuffer(data[8:1400], dtype=np.uint8))
        return self.PlotDataAdc

    def dataProcess(self, data):
        pass

    def showImage(self):
        data = self.fp.read(1536)

        if len(data) < 1536:
            return
        self.PlotDataAdc[0:1392] = copy.deepcopy(np.frombuffer(data[8:1400], dtype=np.uint8))
        data = self.fp.read(1536)
        self.PlotDataAdc[1392:1392 * 2] = copy.deepcopy(np.frombuffer(data[8:1400], dtype=np.uint8))
        data = self.fp.read(1536)
        self.PlotDataAdc[1392 * 2:1392 * 3] = copy.deepcopy(np.frombuffer(data[8:1400], dtype=np.uint8))
        data = self.fp.read(1536)
        self.PlotDataAdc[1392 * 3:1392 * 4] = copy.deepcopy(np.frombuffer(data[8:1400], dtype=np.uint8))
        data = self.fp.read(1536)
        self.PlotDataAdc[1392 * 4:1392 * 5] = copy.deepcopy(np.frombuffer(data[8:1400], dtype=np.uint8))
        data = self.fp.read(1536)
        self.PlotDataAdc[1392 * 5:1392 * 6] = copy.deepcopy(np.frombuffer(data[8:1400], dtype=np.uint8))

        canvas = np.ones((800, 1536), dtype="uint8")
        canvas1 = np.ones((600, 600, 3))
        canvas1raw = np.ones((600, 600))
        raw0 = self.PlotDataAdc.reshape((4176, 2))
        raw1 = (raw0[:, 1] * 256 + raw0[:, 0])[0:4096]
        raw1[raw1 > 32767] -= 65536
        raw1 += 32768
        raw2 = raw1.reshape((512, 8))
        DrawMax[0] = np.max(raw2[:, 0])
        DrawMax[1] = np.max(raw2[:, 1])
        DrawMax[2] = np.max(raw2[:, 2])
        DrawMax[3] = np.max(raw2[:, 3])
        DrawMin[0] = np.min(raw2[:, 0])
        DrawMin[1] = np.min(raw2[:, 1])
        DrawMin[2] = np.min(raw2[:, 2])
        DrawMin[3] = np.min(raw2[:, 3])
        raw2[:, 0] = raw2[:, 0] - DrawMin[0]
        raw2[:, 1] = raw2[:, 1] - DrawMin[1]
        raw2[:, 2] = raw2[:, 2] - DrawMin[2]
        raw2[:, 3] = raw2[:, 3] - DrawMin[3]
        ZoomFactor[0] = 300 / (DrawMax[0] - DrawMin[0])
        ZoomFactor[1] = 300 / (DrawMax[1] - DrawMin[1])
        ZoomFactor[2] = 300 / (DrawMax[2] - DrawMin[2])
        ZoomFactor[3] = 300 / (DrawMax[3] - DrawMin[3])
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

        adc0_x = np.zeros(512)
        adc0_y = np.zeros(512)
        adc1_x = np.zeros(512)
        adc1_y = np.zeros(512)
        adc2_x = np.zeros(512)
        adc2_y = np.zeros(512)
        adc3_x = np.zeros(512)
        adc3_y = np.zeros(512)

        for i in range(512):
            canvas[300 - int(ZoomFactor[0] * raw2[i, 0]), i] = 255
            canvas[300 - int(ZoomFactor[1] * raw2[i, 1]), i + 512] = 255
            canvas[700 - int(ZoomFactor[2] * raw2[i, 2]), i] = 255
            canvas[700 - int(ZoomFactor[3] * raw2[i, 3]), i + 512] = 255
            adc0_x[i] = i
            adc0_y[i] = 300 - int(ZoomFactor[0] * raw2[i, 0])

            adc1_x[i] = i
            adc1_y[i] = 300 - int(ZoomFactor[1] * raw2[i, 1])

            adc2_x[i] = i
            adc2_y[i] = 700 - int(ZoomFactor[2] * raw2[i, 2])

            adc3_x[i] = i
            adc3_y[i] = 700 - int(ZoomFactor[3] * raw2[i, 3])


        for i in range(256):
            canvas[300 - int(fftZoomFactor * fft0[i]), i + 1024] = 255
            canvas[300 - int(fftZoomFactor * fft1[i]), i + 1280] = 255
            canvas[700 - int(fftZoomFactor * fft2[i]), i + 1024] = 255
            canvas[700 - int(fftZoomFactor * fft3[i]), i + 1280] = 255

        '''
        self.axes0.plot(adc0_x, adc0_y)
        self.axes1.plot(adc1_x, adc1_y)
        self.axes2.plot(adc2_x, adc2_y)
        self.axes3.plot(adc3_x, adc3_y)
        graphicscene = QtWidgets.QGraphicsScene()
        graphicscene.addWidget(self)
        self.audioTool.graphicsView.setScene(graphicscene)
        self.graphicview.show()
        # print("Draw")
        '''


        plt.subplot(221)
        plt.title("adc0")
        plt.xlim((0, 512))
        plt.ylim((0, 800))
        plt.plot(adc0_x, adc0_y)
        plt.subplot(222)
        plt.title("adc1")
        plt.xlim((0, 512))
        plt.ylim((0, 800))
        plt.plot(adc1_x, adc1_y)
        plt.subplot(223)
        plt.title("adc2")
        plt.xlim((0, 512))
        plt.ylim((0, 800))
        plt.plot(adc2_x, adc2_y)
        plt.subplot(224)
        plt.title("adc3")
        plt.xlim((0, 512))
        plt.ylim((0, 800))
        plt.plot(adc3_x, adc3_y)
        plt.show()
        plt.clf()