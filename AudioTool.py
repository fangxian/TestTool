from AudioUI import Ui_MainWindow
import serial
import serial.tools.list_ports
import os
import time

logpath = os.getcwd()+'\\logs'
class AudioToolUI(Ui_MainWindow):
    def __init__(self, MainWindow):
        super().setupUi(MainWindow)
        self.ser = None
        self.fp = None
        self.parameter = None
        self.isRenamed = False
        if os.path.exists(logpath):
            pass
        else:
            os.mkdir(logpath)

    def __del__(self):
        if self.fp is not None:
            self.fp.close()
            if self.isRenamed is False:
                if self.parameter is not None:
                    dst = self.logfile + '-' + self.parameter + '.log'
                else:
                    dst = self.logfile + '.log'
        if self.ser is not None:
            self.ser.close()
    # set slot
    def setSignalSlot(self):
        self.SerialRefreshBtn.clicked.connect(self.on_SerialRefreshBtn_clicked)
        self.SerialOpenBtn.clicked[bool].connect(self.on_SerialOpenBtn_clicked)
        self.SerialSendMsgBtn.clicked.connect(self.on_SerialSendMsgBtn_clicked)
        self.StartTestCaseBtn.clicked[bool].connect(self.on_StartTestCaseBtn_clicked)
        self.ClearLogBtn.clicked.connect(self.on_ClearLogBtn_clicked)


    def on_StartTestCaseBtn_clicked(self):
        '''
        read test case parameter config file
        and send parameter to board
        :return: none
        '''
        if self.StartTestCaseBtn.text() == 'Start':
            # read testcase
            self.testCaseName = ''
            self.log("start test case: " + self.testCaseName)
            #TODO parse parameter config, store test case name
            self.StartTestCaseBtn.setText("Stop")
        else:
            self.log("stop test case: " + self.testCaseName)
            self.fp.close()
            self.fp = None
            if self.parameter is not None:
                dst = self.logfile + '-' + self.parameter + '.log'
            else:
                dst = self.logfile + '.log'
            os.rename(self.logfile, dst)
            self.isRenamed = True
            #TODO send stop command

            self.StartTestCaseBtn.setText("Start")

    # SerialSendMsgBtn click event
    def on_SerialSendMsgBtn_clicked(self):
        commandMsg = self.CommandLineEdit.text()
        #TODO parse command to store test case name
        print("command msg: ", commandMsg)
        if self.ser is not None:
            self.ser.write(commandMsg.encode("utf-8"))
        else:
            self.log("serial has not open")

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

    def ExceptionProcess(self, e):
        self.log("Exception: " + e.__str__)
