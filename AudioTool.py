from AudioUI import Ui_MainWindow
import serial
import serial.tools.list_ports
import os
import time
import json
import threading
import multiprocessing
from PyQt5.QtWidgets import QFileDialog
from AudioDataProcess import DataShow, drawImage, drawImage_1, drwaSpectrum, compareWaveFileSpec
from queue import Queue
import numpy as np
import wave
logpath = os.getcwd() + '\\logs'
configpath = os.getcwd() + '\\config'
wavepath = os.getcwd() + '\\wave'
binFilePath = os.getcwd() + '\\data'

class AudioToolUI(Ui_MainWindow):
    def __init__(self, MainWindow):
        super().setupUi(MainWindow)
        self.ser = None
        self.logFp = None
        self.dataFp = None
        self.parameterStr = None
        self.testCaseName = None
        self.isRenamed = False
        self.isStarted = False
        self.configMap = {}
        self.serialWriteSuccess = False
        self.parameterMap = {}
        self.dataShow = DataShow(self)
        self.receivePingPong = np.zeros((2, 92160144), dtype=np.uint8)
        self.recviveFlag = 0
        self.storeFlag = 0
        #self.dataReadThread = threading.Thread(target=self.serialReadData)
        self.dataStoreThread = threading.Thread(target=self.dataSave)
        self.serialReadThread = threading.Thread(target=self.serialRead)

        self.queue = multiprocessing.Queue()
        self.specQueue = multiprocessing.Queue()
        self.hasData = multiprocessing.Value('i', 0)
        self.threadRun = multiprocessing.Value('i', 1)
        self.resetFlag = multiprocessing.Value('i', 0)
        self.dataShowProcess = multiprocessing.Process(target=drawImage_1,
                                                       args=(self.queue, self.threadRun, self.hasData))

        self.spectrumShowProcess = multiprocessing.Process(target=drwaSpectrum, args=(self.specQueue, self.threadRun, self.resetFlag))

        self.pool = multiprocessing.Pool(processes=3)

        #self.dataReadThread.start()
        self.dataShowProcess.start()
        self.dataStoreThread.start()
        self.spectrumShowProcess.start()
        self.serialReadThread.start()
        if os.path.exists(logpath):
            pass
        else:
            os.mkdir(logpath)

        if os.path.exists(binFilePath):
            pass
        else:
            os.mkdir(binFilePath)


    def __del__(self):
        print("done")
        # self.relase()

    # set slot
    def setSignalSlot(self):
        self.SerialRefreshBtn.clicked.connect(self.on_SerialRefreshBtn_clicked)
        self.SerialOpenBtn.clicked[bool].connect(self.on_SerialOpenBtn_clicked)
        self.SerialSendMsgBtn.clicked.connect(self.on_SerialSendMsgBtn_clicked)
        self.StartTestCaseBtn.clicked[bool].connect(self.on_StartTestCaseBtn_clicked)
        self.ClearLogBtn.clicked.connect(self.on_ClearLogBtn_clicked)
        self.TestCaseRefreshBtn.clicked.connect(self.on_TestCaseRefreshBtn_clicked)
        self.DownloadBtn.clicked.connect(self.on_DownloadBtn_clicked)
        self.OpenFileBtn1.clicked.connect(self.on_OpenFileBtn1_clicked)
        self.OpenFileBtn2.clicked.connect(self.on_OpenFileBtn2_clicked)
        self.OpenFileBtn3.clicked.connect(self.on_OpenFileBtn3_clicked)
        self.CompareBtn.clicked.connect(self.on_CompareBtn_clicked)

    def on_OpenFileBtn1_clicked(self):
        openfile_name = QFileDialog.getOpenFileName(self.WavCompareWidget, '选择文件', '', 'Wav(*.wav)')
        fileName = openfile_name[0]
        self.FileLineEdit1.setText(fileName)

    def on_OpenFileBtn2_clicked(self):
        openfile_name = QFileDialog.getOpenFileName(self.WavCompareWidget, '选择文件', '', 'Wav(*.wav)')
        fileName = openfile_name[0]
        self.FileLineEdit2.setText(fileName)
    def on_OpenFileBtn3_clicked(self):
        openfile_name = QFileDialog.getOpenFileName(self.WavCompareWidget, '选择文件', '', 'Wav(*.wav)')
        fileName = openfile_name[0]
        self.FileLineEdit3.setText(fileName)

    def on_CompareBtn_clicked(self):
        files = []
        filename1 = self.FileLineEdit1.text()
        filename2 = self.FileLineEdit2.text()
        filename3 = self.FileLineEdit3.text()
        if filename1 != '':
            files.append(filename1)
        if filename2 != '':
            files.append(filename2)
        if filename3 != '':
            files.append(filename3)
        self.pool.apply(compareWaveFileSpec, (files,))
        print(filename1)

    # walk json config files
    def loadTestCase(self):
        configFiles = os.listdir(configpath)
        self.TestCaseListWidget.addItems(configFiles)
        for f in configFiles:
            configFile = configpath + '\\' + f
            with open(configFile, 'r') as load_f:
                try:
                    data = json.load(load_f)
                    self.parameterMap = data
                    self.configMap[f] = json.dumps(data)
                except Exception as e:
                    self.log(f.__str__() + " " + e.__str__())

    def loadWaveCase(self):
        waveFiles = os.listdir(wavepath)
        self.WaveListWidget.addItems(waveFiles)

    def on_DownloadBtn_clicked(self):
        wavefile = self.WaveListWidget.currentItem().text()
        wavefile = wavepath + '\\' + wavefile
        f = wave.open(wavefile, "rb")
        params = f.getparams()
        nchannels, sampwidth, framerate, nframes = params[:4]

        str_data = f.readframes(nframes=nframes)
        self.log(str(str_data))
        #TODO use a new thread to send wave data
        #self.serialWriteMsg(str_data, isByte=True)
        self.log("download wave data finished!")
        f.close()

    def on_TestCaseRefreshBtn_clicked(self):
        self.configMap.clear()
        self.TestCaseListWidget.clear()
        self.loadTestCase()

    def on_StartTestCaseBtn_clicked(self):
        '''
        read test case parameter config file
        and send parameter to board
        :return: none
        '''
        if self.StartTestCaseBtn.text() == 'Start':
            self.testCaseName = self.TestCaseListWidget.currentItem().text()
            self.log("start test case: " + self.testCaseName)
            self.parameterStr = self.configMap[self.testCaseName]
            self.log("parameters: " + self.parameterStr)
            self.serialWriteMsg(self.parameterStr)
            # cv.namedWindow("ADC data", cv.WINDOW_NORMAL)
            if self.serialWriteSuccess is True:
                binfile = '\\data-' + time.strftime('%Y-%m-%d-%H_%M_%S', time.localtime(time.time())) + '.bin'
                #self.dataFp = open(binFilePath + binfile, 'w+')
                self.isStarted = True
                self.resetFlag.value = 1
                self.StartTestCaseBtn.setText("Stop")
        else:
            stopJson = {"cmd":"StopCase"}
            stopStr = json.dumps(stopJson)
            self.serialWriteMsg(stopStr)
            if self.serialWriteSuccess is False:
                return
            time.sleep(0.1)
            self.isStarted = False

            if self.recviveFlag == 0:
                self.receivePingPong[0][0:].tofile(binFilePath+'\\data-' + time.strftime('%Y-%m-%d-%H_%M_%S', time.localtime(time.time()))+'.bin')
            else:
                self.receivePingPong[1][0:].tofile(binFilePath+'\\data-' + time.strftime('%Y-%m-%d-%H_%M_%S', time.localtime(time.time()))+'.bin')

            self.dataShow.reset()

            # self.queue.close()
            # self.queue = multiprocessing.Queue()

            while not self.specQueue.empty() or not self.queue.empty():
                if not self.specQueue.empty():
                    self.specQueue.get()
                if not self.queue.empty():
                    self.queue.get()

            self.StartTestCaseBtn.setText("Start")
            self.log("stop test case: " + self.testCaseName)
            self.logFp.close()
            self.logFp = None
            if self.testCaseName is not None:
                dst = self.logfile + '-' + self.testCaseName + '.log'
            else:
                dst = self.logfile + '.log'
            os.rename(self.logfile, dst)
            self.isRenamed = True
            self.testCaseName = None

    # SerialSendMsgBtn click event
    def on_SerialSendMsgBtn_clicked(self):
        commandMsg = self.CommandLineEdit.text()
        # TODO parse command to store test case name
        self.serialWriteSuccess(commandMsg)

    # SerialRefreshBtn click event
    def on_SerialRefreshBtn_clicked(self):
        self.SerialPortQCB.clear()
        self.loadSerialPort()
        self.log("refresh serial port\n")

    # SerialOpenBtn click event
    def on_SerialOpenBtn_clicked(self):
        if self.SerialOpenBtn.text() == "Open":
            try:
                self.portx = self.SerialPortQCB.currentText()
                self.bits = int(self.SerialBitRateQCB.currentText())
                self.ser = serial.Serial(self.portx, self.bits, timeout=0.01)
                self.log("Open Serial port: " + self.portx + " bitrates: " + str(self.bits))
                self.SerialOpenBtn.setText("Close")
            except Exception as e:
                self.log("Exception: " + e.__str__())
                #self.ser.close()
        else:
            try:
                self.ser.close()
                self.ser = None
                self.log("close serial port: " + self.portx)
                self.SerialOpenBtn.setText("Open")
            except Exception as e:
                self.log("Exception: " + e.__str__())

    # load system serial port
    def loadSerialPort(self):
        port_list = list(serial.tools.list_ports.comports())
        if len(port_list) == 0:
            self.log("no serial port avail")
        else:
            for i in range(len(port_list)):
                self.SerialPortQCB.addItem(port_list[i].device)

    # add serial baundrate
    def addSerialBitRateItems(self):
        bitrates = ['110', '300', '600', '1200', '2400', '4800', '9600', '14400', '19200', '38400', '56000', '57600',
                    '115200', '128000', '230400', '256000', '460800', '921600']
        self.SerialBitRateQCB.addItems(bitrates)

    # print log on text view and dump to file
    def log(self, str):
        if self.logFp is None:
            self.logfile = time.strftime('%Y-%m-%d-%H_%M_%S', time.localtime(time.time())) + '-' + 'Log'
            self.logfile = logpath + "\\" + self.logfile
            self.logFp = open(self.logfile, 'w')
            self.isRenamed = False
        self.logFp.writelines(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())) + ': ' + str + '\n')
        self.OpLogBrowser.append(str)

    def on_ClearLogBtn_clicked(self):
        self.OpLogBrowser.clear()

    def exceptionProcess(self, e):
        self.log("Exception: " + e.__str__)

    def serialWriteMsg(self, str, isByte=False):
        if self.ser is not None:
            if isByte:
                self.ser.write(str)
            self.ser.write(str.encode("utf-8"))
            self.log("serial write msg: " + str)
            self.serialWriteSuccess = True
        else:
            self.log("ser has not been open, cannot write msg: " + str)
            self.serialWriteSuccess = False

    def serialRead(self):
        while self.threadRun.value == 1:
            if self.isStarted:
                str1 = self.ser.read(1600)
                bytesHead = str1[:8]
                if str(bytesHead, encoding="utf-8") == '':
                    pass
                else:
                    strstr = str(bytesHead, encoding="utf-8")
                    if strstr[0:4] == "data":
                        len = int(strstr[4:8])
                        data = self.dataShow.storeCollectData(str1[8:8+len], len)
                        if data is not None:
                            self.queue.put(data)
                            self.specQueue.put(data)
                            self.hasData.value = 1
                    #self.log(str(str1, encoding="utf-8"))
                #time.sleep(0.001)

    # a new thread to recv data and show
    def serialReadData(self):
        while self.threadRun.value == 1:
            if self.isStarted:
                # self.dataShow.showImage()
                if self.hasData.value == 0:
                    data = self.dataShow.testReadFile()
                    if data is not None:
                        #self.dataFp.write(str(data))
                        self.queue.put(data)
                        self.specQueue.put(data)
                        self.hasData.value = 1
                    time.sleep(0.01)

    def serialReadData_1(self):
        while self.threadRun.value == 1:
            if self.isStarted:
                data = self.dataShow.testReadFile()
                if data is not None:
                    self.queue.put(self.dataShow.testReadFile())
                time.sleep(0.01)

    def dataProcess(self):
        pass

    def dataSave(self):
        while self.threadRun.value == 1:
            if self.storeFlag == 1:
                if self.recviveFlag == 0:
                    self.receivePingPong[1][0:].tofile(binFilePath+'\\data-' + time.strftime('%Y-%m-%d-%H_%M_%S', time.localtime(time.time()))+'.bin')
                    self.storeFlag = 0
                    self.receivePingPong[1].fill(0)
                else:
                    self.receivePingPong[0][0:].tofile(binFilePath+'\\data-' + time.strftime('%Y-%m-%d-%H_%M_%S', time.localtime(time.time()))+'.bin')
                    self.storeFlag = 0
                    self.receivePingPong[0].fill(0)

            time.sleep(0.01)


    def relase(self):
        self.threadRun.value = 0
        #self.dataReadThread.join()
        self.serialReadThread.join()
        self.dataStoreThread.join()
        self.dataShowProcess.join()
        self.spectrumShowProcess.join()
        self.pool.close()
        self.pool.join()
        if self.dataFp is not None:
            self.dataFp.close()
        if self.ser is not None:
            if self.isStarted:
                stopJson = {"cmd": "Stop"}
                stopStr = json.dumps(stopJson)
                self.serialWriteMsg(stopStr)
            self.ser.close()
            self.ser = None
        if self.logFp is not None:
            self.logFp.close()
            if self.isRenamed is False:
                if self.testCaseName is not None:
                    dst = self.logfile + '-' + self.testCaseName + '.log'
                else:
                    dst = self.logfile + '.log'
                os.rename(self.logfile, dst)

