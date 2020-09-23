from AudioUI import Ui_MainWindow
import serial
import serial.tools.list_ports
import os
import time
import json

logpath = os.getcwd()+'\\logs'
configpath = os.getcwd()+'\\config'

class AudioToolUI(Ui_MainWindow):
    def __init__(self, MainWindow):
        super().setupUi(MainWindow)
        self.ser = None
        self.fp = None
        self.parameter = None
        self.testCaseName = None
        self.isRenamed = False
        self.configMap = {}
        self.serialWriteSuccess = False
        if os.path.exists(logpath):
            pass
        else:
            os.mkdir(logpath)

    def __del__(self):
        if self.fp is not None:
            self.fp.close()
            if self.isRenamed is False:
                if self.testCaseName is not None:
                    dst = self.logfile + '-' + self.testCaseName + '.log'
                else:
                    dst = self.logfile + '.log'
        os.rename(self.logfile, dst)
        if self.ser is not None:
            self.ser.close()

    # set slot
    def setSignalSlot(self):
        self.SerialRefreshBtn.clicked.connect(self.on_SerialRefreshBtn_clicked)
        self.SerialOpenBtn.clicked[bool].connect(self.on_SerialOpenBtn_clicked)
        self.SerialSendMsgBtn.clicked.connect(self.on_SerialSendMsgBtn_clicked)
        self.StartTestCaseBtn.clicked[bool].connect(self.on_StartTestCaseBtn_clicked)
        self.ClearLogBtn.clicked.connect(self.on_ClearLogBtn_clicked)
        self.TestCaseRefreshBtn.clicked.connect(self.on_TestCaseRefreshBtn_clicked)

    # walk json config files
    def loadTestCase(self):
        configFiles = os.listdir(configpath)
        self.TestCaseListWidget.addItems(configFiles)
        for f in configFiles:
            configFile = configpath + '\\' + f
            with open(configFile, 'r') as load_f:
                try:
                    data = json.load(load_f)
                    self.configMap[f] = json.dumps(data)
                except Exception as e:
                    self.log(f.__str__() + " " + e.__str__())


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
            self.parameter = self.configMap[self.testCaseName]
            self.log("parameters: " +self.parameter)
            self.serialWriteMsg(self.parameter)
            if self.serialWriteSuccess is True:
                self.StartTestCaseBtn.setText("Stop")
        else:

            self.serialWriteMsg("StopTestCase")
            if self.serialWriteSuccess is False:
                return
            self.StartTestCaseBtn.setText("Start")
            self.log("stop test case: " + self.testCaseName)
            self.fp.close()
            self.fp = None
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
        #TODO parse command to store test case name
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
                self.ser = serial.Serial(self.portx, self.bits, timeout=None)
                self.log("Open Serial port: " + self.portx + " bitrates: " + str(self.bits))
                self.SerialOpenBtn.setText("Close")
            except Exception as e:
                self.log("Exception: " + e.__str__())
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
        bitrates = ['110', '300', '600', '1200', '2400', '4800', '9600', '14400', '19200', '38400', '56000', '57600', '115200', '128000', '230400', '256000', '460800', '921600']
        self.SerialBitRateQCB.addItems(bitrates)

    # print log on text view and dump to file
    def log(self, str):
        if self.fp is None:
            self.logfile = time.strftime('%Y-%m-%d-%H_%M_%S', time.localtime(time.time())) + '-' + 'Log'
            self.logfile = logpath + "\\" + self.logfile
            self.fp = open(self.logfile, 'w')
            self.isRenamed = False
        self.fp.writelines(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))+': ' + str + '\n')
        self.OpLogBrowser.append(str)

    def on_ClearLogBtn_clicked(self):
        self.OpLogBrowser.clear()

    def exceptionProcess(self, e):
        self.log("Exception: " + e.__str__)

    def serialWriteMsg(self, str):
        if self.ser is not None:
            self.ser.write(str.encode("utf-8"))
            self.log("serial write msg: " + str)
            self.serialWriteSuccess = True
        else:
            self.log("ser has not been open, cannot write msg: " + str)
            self.serialWriteSuccess = False


    def serialReadData(self):
        pass