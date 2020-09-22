from AudioUI import Ui_MainWindow
from PyQt5 import QtCore, QtGui, QtWidgets
import serial
import serial.tools.list_ports


class AudioToolUI(Ui_MainWindow):
    def __init__(self, MainWindow):
        super().setupUi(MainWindow)
        self.ser = None

    def setSignalSlot(self):
        self.SerialRefreshBtn.clicked.connect(self.on_SerialRefreshBtn_clicked)
        self.SerialOpenBtn.clicked.connect(self.on_SerialOpenBtn_clicked)
        self.SerialCloseBtn.clicked.connect(self.on_SerialCloseBtn_clicked)
        self.SerialSendMsgBtn.clicked.connect(self.on_SerialSendMsgBtn_clicked)

    # SerialSendMsgBtn click event
    def on_SerialSendMsgBtn_clicked(self):
        commandMsg = self.CommandLineEdit.text()
        print("command msg: ", commandMsg)
        if self.ser is not None:
            self.ser.write(commandMsg.encode("utf-8"))
        else:
            print("serial has not open")

    # SerialRefreshBtn click event
    def on_SerialRefreshBtn_clicked(self):
        print('done')
        self.SerialPortQCB.clear()
        self.loadSerialPort()

    # SerialOpenBtn click event
    def on_SerialOpenBtn_clicked(self):
        try:
            portx = self.SerialPortQCB.currentText()
            bits = int(self.SerialBitRateQCB.currentText())
            self.ser = serial.Serial(portx, bits, timeout=None)
            print("Serial ars: ", self.ser)
        except Exception as e:
            print("Exception: ", e)

    # SerialCloseBtn click event
    def on_SerialCloseBtn_clicked(self):
        self.ser.close()
        print("close ser")

    # load system serial port
    def loadSerialPort(self):
        port_list = list(serial.tools.list_ports.comports())
        if len(port_list) == 0:
            print("no serial port avail")
        else:
            for i in range(len(port_list)):
                self.SerialPortQCB.addItem(port_list[i].device)

    # add serial baundrate
    def addSerialBitRateItems(self):
        bitrates = ['110', '300', '600', '1200', '2400', '4800', '9600', '14400', '19200', '38400', '56000', '57600', '115200', '128000', '230400', '256000', '460800', '921600']
        self.SerialBitRateQCB.addItems(bitrates)

