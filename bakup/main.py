from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QApplication, QWidget, QListWidget, QVBoxLayout, QListWidgetItem
import sys

class Ui(QtWidgets.QMainWindow):
    def __init__(self):
        super(Ui, self).__init__()
        uic.loadUi('scix_1.ui', self)

        self.button = self.findChild(QtWidgets.QToolButton, 'downloadbutton') # Find the button
        self.button.clicked.connect(self.scidexe) # Remember to pass the definition/method, not the return value!

        self.input = self.findChild(QtWidgets.QLineEdit, 'inputurl')
        self.folderlist = self.findChild(QtWidgets.QListWidget, 'folderlist')
        QListWidgetItem("Geeks", self.folderlist)
        QListWidgetItem("Gee", self.folderlist)
        fname=self.folderlist.selectedItems()
        #
        for i in range(self.folderlist.count()):
            itemsTextList = [str(self.folderlist.item(i).text())]
        self.folderlist=QtWidgets.QListWidget()
        self.folderlist.insertItem(0,'a')
        print(itemsTextList)
        self.folderlist.currentItemChanged.connect(self.info)
        self.show()
    def info(self):
        print(self.folderlist.currentRow())
        print(self.folderlist.currentItem().text())
    def information():
        print(self.folderlist.currentItem().text())

    def scidexe(self):
        # This is executed when the button is pressed
        print('Input text:' + self.input.text())
        from scidownload import downloadfromlink
        downloadfromlink(self.input.text())

app = QtWidgets.QApplication(sys.argv)
window = Ui()
app.exec_()
