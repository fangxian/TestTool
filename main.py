from PyQt5 import QtWidgets
import sys
import serial
import serial.tools.list_ports
from AudioTool import AudioToolUI
def qt_test():
    app = QtWidgets.QApplication(sys.argv)
    first_window = QtWidgets.QMainWindow()
    first_window.resize(400, 300)
    first_window.setWindowTitle("我的第一个pyqt程序")
    testToolUI = AudioToolUI(first_window)
    testToolUI.setupUi(first_window)
    testToolUI.setSignalSlot()
    testToolUI.loadSerialPort()
    testToolUI.addSerialBitRateItems()
    testToolUI.loadTestCase()
    first_window.show()
    sys.exit(app.exec())
# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.


def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    qt_test()
# See PyCharm help at https://www.jetbrains.com/help/pycharm/
