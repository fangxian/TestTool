from PyQt5 import QtWidgets
import sys
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
    testToolUI.loadWaveCase()
    first_window.show()
    app.exec()
    testToolUI.relase()



# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    qt_test()
# See PyCharm help at https://www.jetbrains.com/help/pycharm/
