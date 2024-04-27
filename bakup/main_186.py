from PyQt5 import QtWidgets, uic, QtCore, QtGui
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QDialog
import sys
import time
from bs4 import BeautifulSoup
import requests
from urllib.parse import urlparse
from urllib.request import urljoin
import re
from crossref.restful import Works

class Ui(QtWidgets.QMainWindow):
    def __init__(self):
        super(Ui, self).__init__()
        uic.loadUi('scix_1.ui', self)

        #########Download section################
        self.button = self.findChild(QtWidgets.QToolButton, 'downloadbutton')  # Find the button
        #self.qdialog=prog()
        self.input = self.findChild(QtWidgets.QLineEdit, 'inputurl')
        self.button.clicked.connect(self.scidexe)  # Remember to pass the definition/method, not the return value!
        #self.link=self.input.text()
        #self.qdialog.show()
        self.show()


    def scidexe(self):
        global link
        link = (self.input.text())
        Dialog=QDialog(None, QtCore.Qt.WindowSystemMenuHint | QtCore.Qt.WindowTitleHint)
        Dialog.setObjectName("Dialog")
        Dialog.setWindowModality(QtCore.Qt.NonModal)
        Dialog.resize(321, 150)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Dialog.sizePolicy().hasHeightForWidth())
        Dialog.setSizePolicy(sizePolicy)
        Dialog.setMaximumSize(QtCore.QSize(321, 150))
        Dialog.setContextMenuPolicy(QtCore.Qt.NoContextMenu)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("icons/1040213-ui/png/028-download.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        Dialog.setWindowIcon(icon)
        Dialog.setStatusTip("")
        Dialog.setWhatsThis("")
        Dialog.setStyleSheet("background-color: rgb(194, 195, 255);")
        Dialog.setSizeGripEnabled(False)
        Dialog.setModal(True)
        #Dialog.setWindowFlags(windowFlags() & ~Qt::WindowContextHelpButtonHint);
        Dialog.setWindowFlag(QtCore.Qt.WindowCloseButtonHint, False)
        self.progressBar = QtWidgets.QProgressBar(Dialog)
        self.progressBar.setGeometry(QtCore.QRect(30, 60, 271, 16))
        #self.progressBar.setProperty("value", 24)
        self.progressBar.setTextVisible(True)
        self.progressBar.setInvertedAppearance(False)
        self.progressBar.setTextDirection(QtWidgets.QProgressBar.TopToBottom)
        self.progressBar.setObjectName("progressBar")
        self.qbutton = QtWidgets.QPushButton(Dialog)
        self.qbutton.setGeometry(QtCore.QRect(120, 90, 75, 23))
        font = QtGui.QFont()
        font.setBold(False)
        font.setWeight(50)

        self.qbutton.setFont(font)
        self.qbutton.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.qbutton.setFlat(False)
        self.qbutton.setObjectName("qbutton")
        global qbutton
        qbutton=self.qbutton
        #self.qbutton.clicked.connect(Dialog.done)
        self.qbutton.clicked.connect(self.stop_thread)


        self.calc = External()
        self.calc.countChanged.connect(self.onCountChanged)
        #print('p='+self.calc.countChanged)
        self.calc.start()

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)
        # This is executed when the button is pressed
        #print(self.input.text())

        #from progress import Ui_Dialog
        import time
        #scraping.scrap(self.input.text())
        #Dialog = QtWidgets.QDialog()
        #ui = Ui_Dialog()
        #ui.setupUi(Dialog)
        Dialog.show()
        #Dialog.exec_()

        #self.calc = External()
        #self.calc.countChanged.connect(self.onCountChanged)
        #self.calc.start()
        #Dialog.show()
        #Dialog.exec_()

        #Dialog.close()
        #ui.setupUi(self.link)
        #scraping.scrap(self.input.text())
        #link=self.input.text()
        #Ui_Dialog(link)
    #def killthread(self):
     #   External.stop(self)

    def onCountChanged(self, value):
        #print(value)
        self.progressBar.setValue(value)
    def stop_thread(self):
        self.calc.stop()
        self.thread.quit()
        self.thread.wait()

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Download status"))
        self.qbutton.setText(_translate("Dialog", "Cancel"))


class External(QThread):
    """
    Runs a counter thread.
    """
    countChanged = pyqtSignal(int)




    def run(self):
        global link
        #link=Ui.link
        print(link)
        threadactive=True
        #link='https://www.pnas.org/content/105/38/14262.short'
        count = 0
        self.countChanged.emit(count)
        URL = 'https://sci-hub.tw/'
        sreq = requests.Session()
        count=20
        self.countChanged.emit(count)
        soup = BeautifulSoup(sreq.get(URL).content, features="html5lib")

        form = soup.find('form')
        print(form)
        fields = form.findAll('input')
        print(fields)
        if threadactive==True:
            count = 30
            self.countChanged.emit(count)
            formdata = dict((field.get('name'), field.get('value')) for field in fields)
            formdata['request'] = link
            posturl = urljoin(URL, form['action'])
            print(posturl)

        if threadactive==True:
            count = 40
            self.countChanged.emit(count)
            res = sreq.post(posturl, data=formdata)
            soups = BeautifulSoup(res.text, features="html5lib")
            src = soups.find('iframe')
            count = 50
            self.countChanged.emit(count)
            src = src['src']
            count = 60
            self.countChanged.emit(count)
            pattern = re.compile(r"var doi = '(.*?)';$", re.MULTILINE | re.DOTALL)
            script = soups.find("script", text=pattern)
            doi = pattern.search(script.text).group(1)
            count = 70
            self.countChanged.emit(count)
            print(doi)

        if threadactive==True:
            works = Works()
            meta = works.doi(doi)
            count = 80
            self.countChanged.emit(count)
            try:
                title = meta['title']
                title = title[0]
            except KeyError:
                title = None
            try:
                authors = meta['author']
                authordict = []
                for i in range(len(authors)):
                    authordict.append(authors[i])
                author = []
                for i in range(len(authordict)):
                    author.append(authordict[i]['given'] + authordict[i]['family'])
            except KeyError:
                author = None
            count = 90
            self.countChanged.emit(count)
            try:
                journal = meta['container-title']
                journal = journal[0]
            except KeyError:
                journal = None
            try:
                yr = meta['created']
                yrs = yr['date-time']
                year = yrs[:4]
            except KeyError:
                year = None
            count = 100
            self.countChanged.emit(count)
            print(journal)
            print(author)
            print(year)
            print(title)




    def stop(self):
        self.threadactive = False
        self.wait()
        print('stopped')

    def killthread(self):
        self.thread.stop()
        print('How do I do this')
app = QtWidgets.QApplication(sys.argv)
window = Ui()

app.exec_()