from PyQt5 import QtWidgets, uic, QtCore, QtGui,QtWebEngineWidgets
from PyQt5.QtCore import QThread, pyqtSignal, QDir
from PyQt5.QtWidgets import *
from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtCore import *
import sys
import time
from bs4 import BeautifulSoup
import requests
import os
from urllib.parse import urlparse
from urllib.request import urljoin
import re
from crossref.restful import Works
import shutil
import pickle
from pdfrw import PdfReader, PdfWriter, PdfDict
from datetime import date
from win32com.shell import shell, shellcon
from turboactivate import (
    TurboActivate,
    IsGenuineResult,
    TurboActivateError,
    TurboActivateTrialExpiredError,
    TA_USER,
    TA_SYSTEM
)
global docpath
docpath=shell.SHGetFolderPath(0, shellcon.CSIDL_PERSONAL, None, 0)
docpath=docpath+'\SciX'
print(docpath)
try:
    os.mkdir(docpath)
except:
    pass

class Ui(QtWidgets.QMainWindow):
    def __init__(self):
        super(Ui, self).__init__()
        uic.loadUi('scix_1.ui', self)
        #############toolbar#############################
        self.addfromlocal.triggered.connect(self.funaddfromlocal)
        self.addfromlocalf.triggered.connect(self.funaddfromlocal)
        #########Download section################
        self.button = self.findChild(QtWidgets.QToolButton, 'downloadbutton')  # Find the button
        #self.qdialog=prog()
        self.input = self.findChild(QtWidgets.QLineEdit, 'inputurl')
        self.button.clicked.connect(self.scidexe)  # Remember to pass the definition/method, not the return value!
        ##########Explorer###################
        self.maintab.tabBar().setTabButton(0, QtWidgets.QTabBar.RightSide, None)
        self.maintab.tabBar().setTabButton(1, QtWidgets.QTabBar.RightSide, None)
        self.maintab.tabCloseRequested.connect(self.closetab)
        self.model = QFileSystemModel()
        self.model.setRootPath(QDir.rootPath())
        self.model.setReadOnly(False)
        self.model.setFilter(QtCore.QDir.AllDirs | QtCore.QDir.NoDotAndDotDot)
        self.tree.setModel(self.model)
        try:
            rootset=pickle.load(open(docpath+"\syslog1.pkl", "rb"))
            self.tree.setRootIndex(self.model.index(rootset))
        except:
            self.tree.setRootIndex(self.model.index("C:"))

        self.tree.clicked.connect(self.fileview)

        #self.tree.setSelectionMode(QtWidgets.QAbstractItemView.ContiguousSelection) unselect
        self.tree.setAnimated(False)
        self.tree.setIndentation(20)
        self.tree.setSortingEnabled(True)
        for i in range(1, self.tree.model().columnCount()):
            self.tree.header().hideSection(i)
        ##########FILELIST###########################
        self.modellist = QtGui.QStandardItemModel()
        self.modellist.setHorizontalHeaderLabels(['Author', 'Title', 'Journal', 'Year', 'Added on'])
        self.filelist.header().setDefaultSectionSize(180)
        self.filelist.setModel(self.modellist)

        ############COMBO############
        self.filtercombo=self.findChild(QtWidgets.QComboBox, 'filtercombo')
        self.filtercombo.currentIndexChanged.connect(self.combo)
        self.sortlist=self.findChild(QtWidgets.QListWidget,'sortlist')


        self.newfolder = self.findChild(QtWidgets.QToolButton, 'newfolder')
        self.newfolder.clicked.connect(self.makedir)
        self.deletefolder=self.findChild(QtWidgets.QToolButton,'deletefolder')
        self.deletefolder.clicked.connect(self.deletefold)
        self.renamefolder.clicked.connect(self.folderrename_ui)
        self.actionStorage_Location.triggered.connect(self.storagetrigger)
        group = QActionGroup(self.menuRename_preference)
        texts = ["Author-Title-Journal-Year", "Title-Author-Journal-Year", "Journal-Author-Title-Year", "Year-Author-Title-Journal","Year-Journal-Author-Title"]

        try:
            renamepref = pickle.load(open(docpath+"\syslog2.pkl", "rb"))
            for text in texts:
                action = QAction(text, self.menuRename_preference, checkable=True, checked=text == renamepref)
                self.menuRename_preference.addAction(action)
                group.addAction(action)
            group.setExclusive(True)
        except:
            for text in texts:
                action = QAction(text, self.menuRename_preference, checkable=True, checked=text == texts[0])
                self.menuRename_preference.addAction(action)
                group.addAction(action)
            group.setExclusive(True)
        group.triggered.connect(self.filenametrigger)
        self.show()

        #################SearchX###############################################
        self.searchx.setDocumentMode(True)
        self.searchx.tabBarDoubleClicked.connect(self.tab_open_doubleclick)
        self.searchx.currentChanged.connect(self.current_tab_changed)
        self.searchx.setTabsClosable(True)
        self.searchx.tabCloseRequested.connect(self.close_current_tab)
        self.addtab.clicked.connect(lambda _: self.add_new_tab())
        self.add_new_tab(QUrl('http://www.google.com'), 'Homepage')
        self.urlbox.returnPressed.connect(self.navigate_to_url)
        self.back.clicked.connect(lambda: self.searchx.currentWidget().back())
        self.forward.clicked.connect(lambda: self.searchx.currentWidget().forward())
        self.refresh.clicked.connect(lambda: self.searchx.currentWidget().reload())
        self.home.clicked.connect(self.navigate_home)
        self.stop.clicked.connect(lambda: self.searchx.currentWidget().stop())

    def funaddfromlocal(self):
        AddDialog = QtWidgets.QDialog()
        AddDialog.setObjectName("AddDialog")
        AddDialog.resize(351, 229)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("ico/028.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        AddDialog.setWindowIcon(icon)
        AddDialog.setStyleSheet("background-color: rgb(194, 195, 255);")
        self.verticalLayout = QtWidgets.QVBoxLayout(AddDialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label = QtWidgets.QLabel(AddDialog)
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)
        self.lineEdit = QtWidgets.QLineEdit(AddDialog)
        self.lineEdit.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.lineEdit.setObjectName("lineEdit")
        self.horizontalLayout.addWidget(self.lineEdit)
        self.openfiledialog = QtWidgets.QToolButton(AddDialog)
        self.openfiledialog.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.openfiledialog.setObjectName("openfiledialog")
        self.horizontalLayout.addWidget(self.openfiledialog)
        self.import_2 = QtWidgets.QPushButton(AddDialog)
        self.import_2.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.import_2.setObjectName("import_2")
        self.horizontalLayout.addWidget(self.import_2)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.line = QtWidgets.QFrame(AddDialog)
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.verticalLayout.addWidget(self.line)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.label_2 = QtWidgets.QLabel(AddDialog)
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.label_2.setFont(font)
        self.label_2.setObjectName("label_2")
        self.horizontalLayout_2.addWidget(self.label_2)
        self.enterdoi = QtWidgets.QLineEdit(AddDialog)
        self.enterdoi.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.enterdoi.setObjectName("enterdoi")
        self.horizontalLayout_2.addWidget(self.enterdoi)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.line_2 = QtWidgets.QFrame(AddDialog)
        self.line_2.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_2.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_2.setObjectName("line_2")
        self.verticalLayout.addWidget(self.line_2)
        self.label_3 = QtWidgets.QLabel(AddDialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_3.sizePolicy().hasHeightForWidth())
        self.label_3.setSizePolicy(sizePolicy)
        self.label_3.setObjectName("label_3")
        self.verticalLayout.addWidget(self.label_3)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.typemanually = QtWidgets.QPushButton(AddDialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.typemanually.sizePolicy().hasHeightForWidth())
        self.typemanually.setSizePolicy(sizePolicy)
        self.typemanually.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.typemanually.setObjectName("typemanually")
        self.horizontalLayout_3.addWidget(self.typemanually)
        self.verticalLayout.addLayout(self.horizontalLayout_3)
        self.flagman=True
        self.openfiledialog.clicked.connect(self.openfd)
        self.typemanually.clicked.connect(self.manent)
        self.import_2.clicked.connect(self.importfromlocal)
        self.retranslateUi_add(AddDialog)
        self.AddDialog=AddDialog
        QtCore.QMetaObject.connectSlotsByName(AddDialog)
        AddDialog.show()



    def importfromlocal(self):
        flag=False
        if self.lineEdit.text()!='':
            if self.enterdoi.text()!='':
                doi=self.enterdoi.text()
                works = Works()
                meta = works.doi(doi)
                print(meta)
                try:
                    title = meta['title']
                    title = title[0]
                    title = title.replace('/', '')
                    title = title.replace(':', '')
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
                        author[i] = author[i].replace('/', '')
                except KeyError:
                    author = None

                try:
                    journal = meta['container-title']
                    journal = journal[0]
                    journal = journal.replace('/', '')
                except KeyError:
                    journal = None
                try:
                    yr = meta['created']
                    yrs = yr['date-time']
                    year = yrs[:4]
                    year = year.replace('/', '')
                except KeyError:
                    year = None
                try:
                    page = meta['page']
                    page = page.replace('/', '')
                except KeyError:
                    page = None
                try:
                    issue = meta['issue']
                    issue = issue.replace('/', '')
                except KeyError:
                    issue = None
                try:
                    volume = meta['volume']
                    volume = volume.replace('/', '')
                except KeyError:
                    volume = None
                try:
                    issn = meta['ISSN']
                    issn = issn[0]
                    issn = issn.replace('/', '')
                except KeyError:
                    issn = None
                try:
                    url = meta['URL']

                except KeyError:
                    url = None
                print(journal)
                print(author)
                print(year)
                print(title)
                filerename = pickle.load(open(docpath+"\syslog2.pkl", "rb"))
                print(filerename)
                read = PdfReader(self.lineEdit.text())
                read.Info
                if author is None:
                    author = ['XXX', 'COULD NOT FETCH AUTHOR DETAILS', 'ADD MANUALLY']
                metadatain = PdfDict(Xauthor=author, Xdoi=doi, Xtitle=title, Xjournal=journal, Xyear=year, Xpage=page,
                                     Xissue=issue, Xvolume=volume, Xissn=issn, Xurl=url, Xdate=date.today())

                read.Info.update(metadatain)

                if title is None:
                    title = ''
                if journal is None:
                    journal = ''
                if year is None:
                    year = ''
                flag=True
                if filerename == 'Author-Title-Journal-Year':
                    print(savetofolderpath + '/' + author[0] + '--' + title + '--' + journal + '--' + year + '.pdf')
                    PdfWriter().write(
                        savetofolderpath + '/' + author[0] + '--' + title + '--' + journal + '--' + year + '.pdf', read)
                    # PdfWriter().write('C:/Users/LeBert/Desktop/testdd.pdf',read)

                if filerename == 'Title-Author-Journal-Year':
                    PdfWriter().write(
                        savetofolderpath + '/' + title + '--' + author[0] + '--' + journal + '--' + year + '.pdf', read)
                if filerename == 'Journal-Author-Title-Year':
                    PdfWriter().write(
                        savetofolderpath + '/' + journal + '--' + author[0] + '--' + title + '--' + year + '.pdf',
                        readd)
                if filerename == 'Year-Author-Title-Journal':
                    PdfWriter().write(
                        savetofolderpath + '/' + year + '--' + author[0] + '--' + title + '--' + journal + '.pdf', read)
                if filerename == 'Year-Journal-Author-Title':
                    PdfWriter().write(
                        savetofolderpath + '/' + year + '--' + journal + '--' + author[0] + '--' + title + '.pdf', read)
                self.AddDialog.close()
                msg = QMessageBox(QMessageBox.Warning, "Import Successful",
                                  "File has been Imported",
                                  QMessageBox.Ok)
                # msg.setWindowIcon(QIcon(":/icons/app.svg"))
                msg.exec_()
            elif self.mtitle != '' and self.mauthors != '':
                print('nodoi')
                title = self.mtitle.text()
                author = self.mauthors.text()
                author = author.split(',')
                journal = self.mjournal.text()
                year = self.myear.text()
                issn = self.missn.text()
                issue = self.missue.text()
                url = self.murl.text()
                doi = self.mdoi.text()
                volume = self.mvolume.text()
                page = self.mpage.text()
                filerename = pickle.load(open(docpath+"\syslog2.pkl", "rb"))
                print(filerename)
                print(self.lineEdit.text())
                read = PdfReader(self.lineEdit.text())
                read.Info
                metadatain = PdfDict(Xauthor=author, Xdoi=doi, Xtitle=title, Xjournal=journal, Xyear=year,
                                     Xpage=page,
                                     Xissue=issue, Xvolume=volume, Xissn=issn, Xurl=url, Xdate=date.today())

                read.Info.update(metadatain)
                print('read')
                if filerename == 'Author-Title-Journal-Year':
                    print(savetofolderpath + '/' + author[0] + '--' + title + '--' + journal + '--' + year + '.pdf')
                    PdfWriter().write(
                        savetofolderpath + '/' + author[0] + '--' + title + '--' + journal + '--' + year + '.pdf',
                        read)
                    # PdfWriter().write('C:/Users/LeBert/Desktop/testdd.pdf',read)

                if filerename == 'Title-Author-Journal-Year':
                    PdfWriter().write(
                        savetofolderpath + '/' + title + '--' + author[0] + '--' + journal + '--' + year + '.pdf',
                        read)
                if filerename == 'Journal-Author-Title-Year':
                    PdfWriter().write(
                        savetofolderpath + '/' + journal + '--' + author[0] + '--' + title + '--' + year + '.pdf',
                        readd)
                if filerename == 'Year-Author-Title-Journal':
                    PdfWriter().write(
                        savetofolderpath + '/' + year + '--' + author[0] + '--' + title + '--' + journal + '.pdf',
                        read)
                if filerename == 'Year-Journal-Author-Title':
                    PdfWriter().write(
                        savetofolderpath + '/' + year + '--' + journal + '--' + author[0] + '--' + title + '.pdf',
                        read)
                self.AddDialog.close()
                msg = QMessageBox(QMessageBox.Warning, "Import Successful",
                                  "File has been Imported",
                                  QMessageBox.Ok)
                # msg.setWindowIcon(QIcon(":/icons/app.svg"))
                msg.exec_()
            else:
                msg = QMessageBox(QMessageBox.Warning, "Fill the fields",
                                  "Type the required fields",
                                  QMessageBox.Ok)
                # msg.setWindowIcon(QIcon(":/icons/app.svg"))
                msg.exec_()
        else:
            msg = QMessageBox(QMessageBox.Warning, "Select file",
                              "Select a file to import",
                              QMessageBox.Ok)
            # msg.setWindowIcon(QIcon(":/icons/app.svg"))
            msg.exec_()

    def openfd(self):
        path, _ = QtWidgets.QFileDialog.getOpenFileName(None, "Select pdf", "*." + 'pdf')
        self.fpath=path
        self.lineEdit.setText(path)



    def add_new_tab(self, qurl=None, label="Blank"):

        if qurl is None:
            qurl = QUrl('')

        self.browser = QWebEngineView()
        self.browser.setUrl(qurl)
        self.browser.page().profile().downloadRequested.connect(self._downloadRequested)
        i = self.searchx.addTab(self.browser, label)

        self.searchx.setCurrentIndex(i)

        # More difficult! We only want to update the url when it's from the
        # correct tab
        self.browser.urlChanged.connect(lambda qurl, browser=self.browser:
                                   self.update_urlbar(qurl, self.browser))

        self.browser.loadFinished.connect(lambda _, i=i, browser=self.browser:
                                     self.searchx.setTabText(i, self.browser.page().title()))

    @QtCore.pyqtSlot(QtWebEngineWidgets.QWebEngineDownloadItem)
    def _downloadRequested(self, download):
        print('dnld')

        self.download=download
        old_path = self.download.path()
        print(old_path)
        suffix = QtCore.QFileInfo(old_path).suffix()
        print(suffix)
        # path='C:/Users/LeBert/Downloads/tst.pdf'
        if suffix=='pdf' or suffix=='PDF' :
            if 'savetofolderpath' in globals():
                self.path_ = savetofolderpath + '/' + 'test.pdf'
                print(self.path_)
                self.download.setPath(self.path_)
                self.download.accept()
                self.download.finished.connect(self.fooo)
            else:
                print('nosave')
                msg = QMessageBox(QMessageBox.Warning, "Select folder",
                                  "Select a folder from resource browser to download",
                                  QMessageBox.Ok)
                # msg.setWindowIcon(QIcon(":/icons/app.svg"))
                msg.exec_()

        else:
            path, _ = QtWidgets.QFileDialog.getSaveFileName(None, "Save File", self.old_path, "*." + self.suffix)
            print(path)
            download.setPath(path)
            download.accept()
            download.finished.connect(self.foo)

    def _download(self):
        doi = self.pastedoi.text()
        if doi!='':
            print(doi)

            self.Dialog_d.close()

            works = Works()
            meta = works.doi(doi)
            print(meta)
            try:
                title = meta['title']
                title = title[0]
                title = title.replace('/', '')
                title = title.replace(':', '')
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
                    author[i] = author[i].replace('/', '')
            except KeyError:
                author = None

            try:
                journal = meta['container-title']
                journal = journal[0]
                journal = journal.replace('/', '')
            except KeyError:
                journal = None
            try:
                yr = meta['created']
                yrs = yr['date-time']
                year = yrs[:4]
                year = year.replace('/', '')
            except KeyError:
                year = None
            try:
                page = meta['page']
                page = page.replace('/', '')
            except KeyError:
                page = None
            try:
                issue = meta['issue']
                issue = issue.replace('/', '')
            except KeyError:
                issue = None
            try:
                volume = meta['volume']
                volume = volume.replace('/', '')
            except KeyError:
                volume = None
            try:
                issn = meta['ISSN']
                issn = issn[0]
                issn = issn.replace('/', '')
            except KeyError:
                issn = None
            try:
                url = meta['URL']

            except KeyError:
                url = None
            print(journal)
            print(author)
            print(year)
            print(title)
            filerename = pickle.load(open(docpath+"\syslog2.pkl", "rb"))
            print(filerename)
            read = PdfReader(self.path_)
            read.Info
            if author is None:
                author = ['XXX', 'COULD NOT FETCH AUTHOR DETAILS', 'ADD MANUALLY']
            metadatain = PdfDict(Xauthor=author, Xdoi=doi, Xtitle=title, Xjournal=journal, Xyear=year, Xpage=page,
                                 Xissue=issue, Xvolume=volume, Xissn=issn, Xurl=url, Xdate=date.today())

            read.Info.update(metadatain)


            if title is None:
                title = ''
            if journal is None:
                journal = ''
            if year is None:
                year = ''
            if filerename == 'Author-Title-Journal-Year':
                print(savetofolderpath + '/' + author[0] + '--' + title + '--' + journal + '--' + year + '.pdf')
                PdfWriter().write(
                    savetofolderpath + '/' + author[0] + '--' + title + '--' + journal + '--' + year + '.pdf', read)
                # PdfWriter().write('C:/Users/LeBert/Desktop/testdd.pdf',read)

            if filerename == 'Title-Author-Journal-Year':
                PdfWriter().write(
                    savetofolderpath + '/' + title + '--' + author[0] + '--' + journal + '--' + year + '.pdf', read)
            if filerename == 'Journal-Author-Title-Year':
                PdfWriter().write(
                    savetofolderpath + '/' + journal + '--' + author[0] + '--' + title + '--' + year + '.pdf', readd)
            if filerename == 'Year-Author-Title-Journal':
                PdfWriter().write(
                    savetofolderpath + '/' + year + '--' + author[0] + '--' + title + '--' + journal + '.pdf', read)
            if filerename == 'Year-Journal-Author-Title':
                PdfWriter().write(
                    savetofolderpath + '/' + year + '--' + journal + '--' + author[0] + '--' + title + '.pdf', read)
            os.remove(self.path_)

        else:
            print('nodoi')
            msg = QMessageBox(QMessageBox.Warning, "Empty field",
                              "Enter the DOI",
                              QMessageBox.Ok)
            # msg.setWindowIcon(QIcon(":/icons/app.svg"))
            msg.exec_()

    def fooo(self):
        print("finished")
        Dialog_d=QDialog()
        Dialog_d.setObjectName("Dialog_d")
        Dialog_d.resize(321, 150)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Dialog_d.sizePolicy().hasHeightForWidth())
        Dialog_d.setSizePolicy(sizePolicy)
        Dialog_d.setMaximumSize(QtCore.QSize(321, 150))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("ico/016.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        Dialog_d.setWindowIcon(icon)
        Dialog_d.setStyleSheet("background-color: rgb(194, 195, 255);")
        self.buttonBox = QtWidgets.QDialogButtonBox(Dialog_d)
        self.buttonBox.setGeometry(QtCore.QRect(10, 440, 621, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel | QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.horizontalLayoutWidget = QtWidgets.QWidget(Dialog_d)
        self.horizontalLayoutWidget.setGeometry(QtCore.QRect(30, 30, 271, 60))
        self.horizontalLayoutWidget.setObjectName("horizontalLayoutWidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.horizontalLayoutWidget)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label = QtWidgets.QLabel(self.horizontalLayoutWidget)
        font = QtGui.QFont()
        font.setPointSize(9)
        font.setBold(False)
        font.setWeight(50)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)
        self.pastedoi = QtWidgets.QLineEdit(self.horizontalLayoutWidget)
        self.pastedoi.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.pastedoi.setObjectName("pastedoi")
        self.horizontalLayout.addWidget(self.pastedoi)
        self.getdoi = QtWidgets.QPushButton(Dialog_d)
        self.getdoi.setGeometry(QtCore.QRect(120, 90, 75, 23))
        self.getdoi.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.getdoi.setObjectName("getdoi")
        self.typemanual = QtWidgets.QPushButton(Dialog_d)
        self.typemanual.setGeometry(QtCore.QRect(210, 90, 75, 23))
        self.typemanual.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.typemanual.setObjectName("typemanual")
        self.flagman=False
        self.typemanual.clicked.connect(self.manent)
        self.retranslateUi_d(Dialog_d)
        self.buttonBox.accepted.connect(Dialog_d.accept)
        self.buttonBox.rejected.connect(Dialog_d.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog_d)
        Dialog_d.show()
        self.getdoi.clicked.connect(self._download)
        self.Dialog_d = Dialog_d
    def manent(self):
        manualentry = QtWidgets.QDialog()
        manualentry.setObjectName("manualentry")
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(manualentry.sizePolicy().hasHeightForWidth())
        manualentry.setSizePolicy(sizePolicy)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("ico/011.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        manualentry.setWindowIcon(icon)
        manualentry.setStyleSheet("background-color: rgb(194, 195, 255);")
        self.formLayout = QtWidgets.QFormLayout(manualentry)
        self.formLayout.setObjectName("formLayout")
        self.label = QtWidgets.QLabel(manualentry)
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.label)
        self.mtitle = QtWidgets.QLineEdit(manualentry)
        self.mtitle.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.mtitle.setObjectName("mtitle")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.mtitle)
        self.label_2 = QtWidgets.QLabel(manualentry)
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.label_2.setFont(font)
        self.label_2.setObjectName("label_2")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.label_2)
        self.mauthors = QtWidgets.QLineEdit(manualentry)
        self.mauthors.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.mauthors.setObjectName("mauthors")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.mauthors)
        self.label_3 = QtWidgets.QLabel(manualentry)
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.label_3.setFont(font)
        self.label_3.setObjectName("label_3")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.label_3)
        self.mjournal = QtWidgets.QLineEdit(manualentry)
        self.mjournal.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.mjournal.setObjectName("mjournal")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.mjournal)
        self.label_4 = QtWidgets.QLabel(manualentry)
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.label_4.setFont(font)
        self.label_4.setObjectName("label_4")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.LabelRole, self.label_4)
        self.myear = QtWidgets.QLineEdit(manualentry)
        self.myear.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.myear.setObjectName("myear")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.FieldRole, self.myear)
        self.label_5 = QtWidgets.QLabel(manualentry)
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.label_5.setFont(font)
        self.label_5.setObjectName("label_5")
        self.formLayout.setWidget(4, QtWidgets.QFormLayout.LabelRole, self.label_5)
        self.mpage = QtWidgets.QLineEdit(manualentry)
        self.mpage.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.mpage.setObjectName("mpage")
        self.formLayout.setWidget(4, QtWidgets.QFormLayout.FieldRole, self.mpage)
        self.label_6 = QtWidgets.QLabel(manualentry)
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.label_6.setFont(font)
        self.label_6.setObjectName("label_6")
        self.formLayout.setWidget(5, QtWidgets.QFormLayout.LabelRole, self.label_6)
        self.missue = QtWidgets.QLineEdit(manualentry)
        self.missue.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.missue.setObjectName("missue")
        self.formLayout.setWidget(5, QtWidgets.QFormLayout.FieldRole, self.missue)
        self.label_7 = QtWidgets.QLabel(manualentry)
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.label_7.setFont(font)
        self.label_7.setObjectName("label_7")
        self.formLayout.setWidget(6, QtWidgets.QFormLayout.LabelRole, self.label_7)
        self.mvolume = QtWidgets.QLineEdit(manualentry)
        self.mvolume.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.mvolume.setObjectName("mvolume")
        self.formLayout.setWidget(6, QtWidgets.QFormLayout.FieldRole, self.mvolume)
        self.label_8 = QtWidgets.QLabel(manualentry)
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.label_8.setFont(font)
        self.label_8.setObjectName("label_8")
        self.formLayout.setWidget(7, QtWidgets.QFormLayout.LabelRole, self.label_8)
        self.missn = QtWidgets.QLineEdit(manualentry)
        self.missn.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.missn.setObjectName("missn")
        self.formLayout.setWidget(7, QtWidgets.QFormLayout.FieldRole, self.missn)
        self.label_9 = QtWidgets.QLabel(manualentry)
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.label_9.setFont(font)
        self.label_9.setObjectName("label_9")
        self.formLayout.setWidget(8, QtWidgets.QFormLayout.LabelRole, self.label_9)
        self.mdoi = QtWidgets.QLineEdit(manualentry)
        self.mdoi.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.mdoi.setObjectName("mdoi")
        self.formLayout.setWidget(8, QtWidgets.QFormLayout.FieldRole, self.mdoi)
        self.label_10 = QtWidgets.QLabel(manualentry)
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.label_10.setFont(font)
        self.label_10.setObjectName("label_10")
        self.formLayout.setWidget(9, QtWidgets.QFormLayout.LabelRole, self.label_10)
        self.murl = QtWidgets.QLineEdit(manualentry)
        self.murl.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.murl.setObjectName("murl")
        self.formLayout.setWidget(9, QtWidgets.QFormLayout.FieldRole, self.murl)
        self.buttonBox = QtWidgets.QDialogButtonBox(manualentry)
        self.buttonBox.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel | QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.formLayout.setWidget(10, QtWidgets.QFormLayout.FieldRole, self.buttonBox)

        self.retranslateUi_man(manualentry)
        #self.buttonBox.accepted.connect(self.mandownload)
        if self.flagman==True:
            self.buttonBox.accepted.connect(manualentry.accept)
        else:
            self.buttonBox.accepted.connect(self.mandownload)
        self.buttonBox.rejected.connect(manualentry.reject)
        QtCore.QMetaObject.connectSlotsByName(manualentry)
        manualentry.show()
        #manualentry.exec_()
        self.manualentry_d=manualentry
    def mandownload(self):
        self.manualentry_d.close()
        filerename = pickle.load(open(docpath+"\syslog2.pkl", "rb"))
        print(filerename)
        read = PdfReader(self.path_)
        read.Info
        print('s')
        author=self.mauthors.text()
        author=author.split(',')
        print(author[0])
        doi=self.mdoi.text()
        title=self.mtitle.text()
        journal=self.mjournal.text()
        year=self.myear.text()
        page=self.mpage.text()
        issue=self.missue.text()
        volume=self.mvolume.text()
        issn=self.missn.text()
        url=self.murl.text()
        print(url)
        metadatain = PdfDict(Xauthor=author, Xdoi=doi, Xtitle=title, Xjournal=journal, Xyear=year, Xpage=page,
                             Xissue=issue, Xvolume=volume, Xissn=issn, Xurl=url, Xdate=date.today())
        read.Info.update(metadatain)

        if title is None:
            title = ''
        if journal is None:
            journal = ''
        if year is None:
            year = ''
        try:
            if filerename == 'Author-Title-Journal-Year':
                print(savetofolderpath + '/' + author[0] + '--' + title + '--' + journal + '--' + year + '.pdf')
                PdfWriter().write(
                    savetofolderpath + '/' + author[0] + '--' + title + '--' + journal + '--' + year + '.pdf', read)

                os.remove(self.path_)
            if filerename == 'Title-Author-Journal-Year':
                PdfWriter().write(
                    savetofolderpath + '/' + title + '--' + author[0] + '--' + journal + '--' + year + '.pdf', read)
                os.remove(self.path_)
            if filerename == 'Journal-Author-Title-Year':
                PdfWriter().write(
                    savetofolderpath + '/' + journal + '--' + author[0] + '--' + title + '--' + year + '.pdf', readd)
                os.remove(self.path_)
            if filerename == 'Year-Author-Title-Journal':
                PdfWriter().write(
                    savetofolderpath + '/' + year + '--' + author[0] + '--' + title + '--' + journal + '.pdf', read)
                os.remove(self.path_)
            if filerename == 'Year-Journal-Author-Title':
                PdfWriter().write(
                    savetofolderpath + '/' + year + '--' + journal + '--' + author[0] + '--' + title + '.pdf', read)
                os.remove(self.path_)


            self.Dialog_d.close()
        except:
            msg = QMessageBox(QMessageBox.Warning, "Empty field",
                              "Enter a proper link!",
                              QMessageBox.Ok)
            # msg.setWindowIcon(QIcon(":/icons/app.svg"))
            msg.exec_()


    def tab_open_doubleclick(self, i):
        if i == -1:  # No tab under the click
            self.add_new_tab()

    def current_tab_changed(self, i):
        qurl = self.searchx.currentWidget().url()
        self.update_urlbar(qurl, self.searchx.currentWidget())
        self.update_title(self.searchx.currentWidget())

    def close_current_tab(self, i):
        if self.searchx.count() < 2:
            return

        self.searchx.removeTab(i)

    def update_title(self, browser):
        if browser != self.searchx.currentWidget():
            # If this signal is not from the current tab, ignore
            return

        title = self.searchx.currentWidget().page().title()
       # self.setWindowTitle("%s - Mozarella Ashbadger" % title)

    def navigate_mozarella(self):
        self.searchx.currentWidget().setUrl(QUrl("https://www.udemy.com/522076"))

    def about(self):
        dlg = AboutDialog()
        dlg.exec_()

    def open_file(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Open file", "",
                                                  "Hypertext Markup Language (*.htm *.html);;"
                                                  "All files (*.*)")

        if filename:
            with open(filename, 'r') as f:
                html = f.read()

            self.searchx.currentWidget().setHtml(html)
            self.urlbox.setText(filename)

    def save_file(self):
        filename, _ = QFileDialog.getSaveFileName(self, "Save Page As", "",
                                                  "Hypertext Markup Language (*.htm *html);;"
                                                  "All files (*.*)")

        if filename:
            html = self.searchx.currentWidget().page().toHtml()
            with open(filename, 'w') as f:
                f.write(html.encode('utf8'))

    def print_page(self):
        dlg = QPrintPreviewDialog()
        dlg.paintRequested.connect(self.browser.print_)
        dlg.exec_()

    def navigate_home(self):
        self.searchx.currentWidget().setUrl(QUrl("http://www.google.com"))

    def navigate_to_url(self):  # Does not receive the Url
        q = QUrl(self.urlbox.text())
        if q.scheme() == "":
            q.setScheme("http")

        self.searchx.currentWidget().setUrl(q)

    def update_urlbar(self, q, browser=None):
        ic=QtGui.QIcon()
        if browser != self.searchx.currentWidget():
            # If this signal is not from the current tab, ignore
            return

        if q.scheme() == 'https':
            ic.addPixmap(QtGui.QPixmap(r'ico\009.png'))
            self.httpsicon.setIcon(ic)
        else:
            ic.addPixmap(QtGui.QPixmap(r'ico\006.png'))
            self.httpsicon.setIcon(ic) 


        self.urlbox.setText(q.toString())
        self.urlbox.setCursorPosition(0)



    def combo(self,findex):
        try:
            self.sortlist.clear()
            self.findex = findex
            print(savetofolderpath)
            pdffiles = []
            for dirpath, dirnames, filenames in os.walk(savetofolderpath):
                for filename in [f for f in filenames if f.endswith(".pdf" or ".PDF")]:
                    pdffiles.append(filename)
            print(pdffiles)
            if findex == 1:
                auth = []
                for i in range(len(pdffiles)):
                    readd = PdfReader(savetofolderpath + '/' + pdffiles[i])
                    try:
                        for j in range(len(readd.Info.Xauthor)):
                            auth.append(readd.Info.Xauthor[j].strip('()'))
                    except:
                        pass

                fauth = []
                fauth = list(dict.fromkeys(auth))
                self.sortlist.addItems(fauth)
                print(auth)

            if findex == 2:
                journ = []
                for i in range(len(pdffiles)):
                    readd = PdfReader(savetofolderpath + '/' + pdffiles[i])
                    try:
                        journ.append(readd.Info.Xjournal.strip('()'))
                    except:
                        pass
                fjourn = []
                fjourn = list(dict.fromkeys(journ))
                self.sortlist.addItems(fjourn)
                print(journ)
            if findex == 3:
                yer = []
                for i in range(len(pdffiles)):
                    readd = PdfReader(savetofolderpath + '/' + pdffiles[i])
                    try:
                        yer.append(readd.Info.Xyear.strip('()'))
                    except:
                        pass
                fyer = []
                fyer = list(dict.fromkeys(yer))
                self.sortlist.addItems(fyer)
                print(yer)
            # self.sortlist.itemSelectionChanged.connect(self.filterview)
            # self.sortlist.itemActivated.connect(self.filterview)
            self.sortlist.itemClicked.connect(self.filterview)
            self.sortitem_dup = None
        except:
            pass



    def scidexe(self):
        global link
        link = (self.input.text())
        #global savefolderpath
        #print(len(savefolderpath))
        if len(link)>0:
            Dialog = QDialog(None, QtCore.Qt.WindowSystemMenuHint | QtCore.Qt.WindowTitleHint)
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
            icon.addPixmap(QtGui.QPixmap("ico/008.png"), QtGui.QIcon.Normal,
                           QtGui.QIcon.Off)
            Dialog.setWindowIcon(icon)
            Dialog.setStatusTip("")
            Dialog.setWhatsThis("")
            Dialog.setStyleSheet("background-color: rgb(194, 195, 255);")
            Dialog.setSizeGripEnabled(False)
            Dialog.setModal(True)
            # Dialog.setWindowFlags(windowFlags() & ~Qt::WindowContextHelpButtonHint);
            Dialog.setWindowFlag(QtCore.Qt.WindowCloseButtonHint, False)
            self.progressBar = QtWidgets.QProgressBar(Dialog)
            self.progressBar.setGeometry(QtCore.QRect(30, 60, 271, 16))
            # self.progressBar.setProperty("value", 24)
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
            self.qbutton.clicked.connect(Dialog.done)
            # self.qbutton.clicked.connect(self.External.stop())

            self.calc = External()
            self.calc.countChanged.connect(self.onCountChanged)
            # print('p='+self.calc.countChanged)
            self.calc.start()

            self.retranslateUi(Dialog)
            QtCore.QMetaObject.connectSlotsByName(Dialog)
            Dialog.show()


        else:
            print('no link')
            msg = QMessageBox(QMessageBox.Warning, "Empty field",
                              "Enter a proper link!",
                              QMessageBox.Ok)
            #msg.setWindowIcon(QIcon(":/icons/app.svg"))
            msg.exec_()
    def onCountChanged(self, value):
        #print(value)
        self.progressBar.setValue(value)
    def filterview(self,itemm):
        sortitem = itemm.text()
        if sortitem != self.sortitem_dup:
            self.sortitem_dup = sortitem
            print(sortitem)
            print(self.findex)
            print(savetofolderpath)
            self.modellist.clear()
            self.modellist = QtGui.QStandardItemModel()
            self.modellist.setHorizontalHeaderLabels(['Author', 'Title', 'Journal', 'Year', 'Added on'])
            if self.findex==1:
                pdffiles = []
                for dirpath, dirnames, filenames in os.walk(savetofolderpath):
                    for filename in [f for f in filenames if f.endswith(".pdf" or ".PDF")]:
                        pdffiles.append(filename)
                print(pdffiles)
                self.dict = {}
                for row in range(len(pdffiles)):

                    read = PdfReader(savetofolderpath + "/" + pdffiles[row])
                    for j in range(len(read.Info.Xauthor)):
                        if read.Info.Xauthor[j].strip('()') == sortitem:
                            try:
                                for column in range(5):

                                    Xauthors = ' '
                                    for i in range(len(read.Info.Xauthor)):
                                        Xauthors = Xauthors + read.Info.Xauthor[i].strip('()') + ';'
                                    data = [Xauthors, read.Info.Xtitle.strip('()'), read.Info.Xjournal.strip('()'),
                                            read.Info.Xyear.strip('()'), read.Info.Xdate.strip('()')]
                                    item = QtGui.QStandardItem(data[column])
                                    self.modellist.setItem(row, column, item)
                                    self.dict[str(item)] = pdffiles[row]
                                    if column == 0:
                                        item.setIcon(
                                            QtGui.QIcon('ico/023.png'))
                                    else:
                                        pass
                                    # item.icon(QtGui.QIcon('icons/1040213-ui/png/pdf.png'))
                                    item.setEditable(False)
                            except:
                                pass
                        else:
                            pass
            if self.findex==2:
                pdffiles = []
                for dirpath, dirnames, filenames in os.walk(savetofolderpath):
                    for filename in [f for f in filenames if f.endswith(".pdf" or ".PDF")]:
                        pdffiles.append(filename)
                print(pdffiles)
                self.dict = {}
                for row in range(len(pdffiles)):
                    read = PdfReader(savetofolderpath + "/" + pdffiles[row])
                    if read.Info.Xjournal.strip('()')==sortitem:
                        try:
                            for column in range(5):

                                Xauthors = ' '
                                for i in range(len(read.Info.Xauthor)):
                                    Xauthors = Xauthors + read.Info.Xauthor[i].strip('()') + ';'
                                data = [Xauthors, read.Info.Xtitle.strip('()'), read.Info.Xjournal.strip('()'),
                                        read.Info.Xyear.strip('()'), read.Info.Xdate.strip('()')]
                                item = QtGui.QStandardItem(data[column])
                                self.modellist.setItem(row, column, item)
                                self.dict[str(item)] = pdffiles[row]
                                if column == 0:
                                    item.setIcon(
                                        QtGui.QIcon('ico/023.png'))
                                else:
                                    pass
                                # item.icon(QtGui.QIcon('icons/1040213-ui/png/pdf.png'))
                                item.setEditable(False)
                        except:
                            pass
            if self.findex==3:
                pdffiles = []
                for dirpath, dirnames, filenames in os.walk(savetofolderpath):
                    for filename in [f for f in filenames if f.endswith(".pdf" or ".PDF")]:
                        pdffiles.append(filename)
                print(pdffiles)
                self.dict = {}
                for row in range(len(pdffiles)):
                    read = PdfReader(savetofolderpath + "/" + pdffiles[row])
                    if read.Info.Xyear.strip('()') == sortitem:
                        try:
                            for column in range(5):

                                Xauthors = ' '
                                for i in range(len(read.Info.Xauthor)):
                                    Xauthors = Xauthors + read.Info.Xauthor[i].strip('()') + ';'
                                data = [Xauthors, read.Info.Xtitle.strip('()'), read.Info.Xjournal.strip('()'),
                                        read.Info.Xyear.strip('()'), read.Info.Xdate.strip('()')]
                                item = QtGui.QStandardItem(data[column])
                                self.modellist.setItem(row, column, item)
                                self.dict[str(item)] = pdffiles[row]
                                if column == 0:
                                    item.setIcon(
                                        QtGui.QIcon(
                                            'ico/023.png'))
                                else:
                                    pass
                                # item.icon(QtGui.QIcon('C:/Users/LeBert/PycharmProjects/alpha/icons/1040213-ui/png/pdf.png'))
                                item.setEditable(False)
                        except:
                            pass


        else:
            pass
        self.filelist.setModel(self.modellist)
        print(self.dict)
        self.filedup = None
        self.filelist.doubleClicked.connect(self.treeitemdoubleClicked)
    def fileview(self,indexx):
        self.modellist.clear()
        self.modellist = QtGui.QStandardItemModel()
        self.modellist.setHorizontalHeaderLabels(['Author', 'Title', 'Journal', 'Year', 'Added on'])
        self.filelist.setModel(self.modellist)
        global savetofolderpath
        savetofolderpath = self.model.filePath(indexx)
        self.savetofolderpath=savetofolderpath
        print(savetofolderpath)

        pdffiles = []
        for dirpath, dirnames, filenames in os.walk(savetofolderpath):
                for filename in [f for f in filenames if f.endswith(".pdf" or ".PDF")]:
                        pdffiles.append(filename)
        print(pdffiles)
        self.dict={}
        for row in range(len(pdffiles)):
                #self.dictl=[]
                try:
                    for column in range(5):
                        read = PdfReader(savetofolderpath + "/" + pdffiles[row])
                        Xauthors = ' '
                        for i in range(len(read.Info.Xauthor)):
                            Xauthors = Xauthors + read.Info.Xauthor[i].strip('()') + ';'
                        data = [Xauthors, read.Info.Xtitle.strip('()'), read.Info.Xjournal.strip('()'),
                                read.Info.Xyear.strip('()'), read.Info.Xdate.strip('()')]
                        item = QtGui.QStandardItem(data[column])
                        self.modellist.setItem(row, column, item)
                        if column==0:
                            item.setIcon(QtGui.QIcon('ico/023.png'))
                        else:
                            pass
                        #item.icon(QtGui.QIcon('C:/Users/LeBert/PycharmProjects/alpha/icons/1040213-ui/png/pdf.png'))
                        item.setEditable(False)
                        self.dict[str(item)] = pdffiles[row]
                except:
                    pass

        print(self.dict)
        print(len(self.dict))
        self.filtercombo.setCurrentIndex(0)
        self.filedup=None
        self.filelist.doubleClicked.connect(self.treeitemdoubleClicked)


    def treeitemsingleclicked(self,index):
        item = self.modellist.itemFromIndex(index)
        file = self.dict[str(item)]
        print(file)
        if self.filedup!=file:
            self.filedup=file
            read = PdfReader(self.savetofolderpath + "/" + file)
            print(read.Info)
    def treeitemdoubleClicked(self, index):
        print(index)
        item = self.modellist.itemFromIndex(index)
        file = self.dict[str(item)]
        if self.filedup!=file:
            self.filedup=file
            print(file)
            print(item)
            # loc=dict[item]
            # print(loc)
            row = item.row()
            print(row)
            print(self.savetofolderpath)
            read = PdfReader(self.savetofolderpath + "/" + file)
            print(read.Info)
            self.titleinfo.setText(str(read.Info.Xtitle).strip('()'))
            self.journalinfo.setText(str(read.Info.Xjournal).strip('()'))
            self.issninfo.setText(str(read.Info.Xissn).strip('()'))
            self.urlinfo.setText(str(read.Info.Xurl).strip('()'))
            self.doiinfo.setText(str(read.Info.Xdoi).strip('()'))
            self.authorinfo.clear()
            for i in range(len(read.Info.Xauthor)):
                self.authorinfo.append(str(read.Info.Xauthor[i]).strip('()'))
           # self.fileinfo.setText(str(read.Info.Xauthor).strip('[]'))
            PDFJS = 'file:///web/viewer.html'
            # PDFJS = 'file:///usr/share/pdf.js/web/viewer.html'
            PDF = 'file:///' + self.savetofolderpath + '/' + file

            self.tab_3 = QWebEngineView()
            # self.tab_2 = QtWidgets.QWidget()
            self.tab_3.setObjectName("tab_2")
            tab3 = self.maintab.addTab(self.tab_3, file)
            self.maintab.setTabIcon(tab3,
                                    QtGui.QIcon('ico/024.png'))
            self.tab_3.load(QtCore.QUrl.fromUserInput('%s?file=%s' % (PDFJS, PDF)))



        else:
            pass



    def closetab(self,index):
        #index=self.maintab.currentIndex()
        #print(index)
        self.maintab.removeTab(index)

    def savetofolder(self, index):
        global savetofolderpath
        savetofolderpath = self.model.filePath(index)

        print(savetofolderpath)


    def makedir(self):
        Dialog = QDialog()
        Dialog.setObjectName("Dialog")
        Dialog.resize(321, 150)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Dialog.sizePolicy().hasHeightForWidth())
        Dialog.setSizePolicy(sizePolicy)
        Dialog.setMaximumSize(QtCore.QSize(321, 150))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("ico/026.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        Dialog.setWindowIcon(icon)
        Dialog.setStyleSheet("background-color: rgb(194, 195, 255);")

        self.horizontalLayoutWidget = QtWidgets.QWidget(Dialog)
        self.horizontalLayoutWidget.setGeometry(QtCore.QRect(30, 30, 271, 60))
        self.horizontalLayoutWidget.setObjectName("horizontalLayoutWidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.horizontalLayoutWidget)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label = QtWidgets.QLabel(self.horizontalLayoutWidget)
        font = QtGui.QFont()
        font.setPointSize(9)
        font.setBold(False)
        font.setWeight(50)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)
        self.newfoldername = QtWidgets.QLineEdit(self.horizontalLayoutWidget)
        self.newfoldername.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.newfoldername.setObjectName("newfoldername")
        self.horizontalLayout.addWidget(self.newfoldername)
        self.newfoldercreate = QtWidgets.QPushButton(Dialog)
        self.newfoldercreate.setGeometry(QtCore.QRect(120, 90, 75, 23))
        self.newfoldercreate.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.newfoldercreate.setObjectName("newfoldercreate")
        self.newfoldercreate.clicked.connect(self.createfolder)
        self.newfoldercreate.clicked.connect(Dialog.done)
        self.radiobutton_c = QtWidgets.QRadioButton(Dialog)
        self.radiobutton_c.setGeometry(QtCore.QRect(210, 93, 91, 17))
        self.radiobutton_c.setObjectName("radiobutton_c")
        self.retranslateUi_c(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)
        Dialog.show()
        Dialog.exec_()

    def createfolder(self):
        print('created')
        print('create')
        if self.radiobutton_c.isChecked()==False:
            if 'savetofolderpath' in globals():
                directory = self.newfoldername.text()
                path = os.path.join(savetofolderpath, directory)
                os.mkdir(path)
            else:
                msg = QMessageBox(QMessageBox.Warning, "Empty field",
                                  "Select a folder to create or check 'create in main' to create new folder in main directroy",
                                  QMessageBox.Ok)
                # msg.setWindowIcon(QIcon(":/icons/app.svg"))
                msg.exec_()
        else:
            directory = self.newfoldername.text()
            store=pickle.load(open(docpath+"\syslog1.pkl", "rb"))
            path = os.path.join(store, directory)
            os.mkdir(path)

    def folderrename_ui(self):
        Dialog = QDialog()
        Dialog.setObjectName("Dialog")
        Dialog.resize(321, 150)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Dialog.sizePolicy().hasHeightForWidth())
        Dialog.setSizePolicy(sizePolicy)
        Dialog.setMaximumSize(QtCore.QSize(321, 150))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("ico/026png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        Dialog.setWindowIcon(icon)
        Dialog.setStyleSheet("background-color: rgb(194, 195, 255);")

        self.horizontalLayoutWidget = QtWidgets.QWidget(Dialog)
        self.horizontalLayoutWidget.setGeometry(QtCore.QRect(30, 30, 271, 60))
        self.horizontalLayoutWidget.setObjectName("horizontalLayoutWidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.horizontalLayoutWidget)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label = QtWidgets.QLabel(self.horizontalLayoutWidget)
        font = QtGui.QFont()
        font.setPointSize(9)
        font.setBold(False)
        font.setWeight(50)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)
        self.renamefolder = QtWidgets.QLineEdit(self.horizontalLayoutWidget)
        self.renamefolder.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.renamefolder.setObjectName("renamefolder")
        self.horizontalLayout.addWidget(self.renamefolder)
        self.renamebutton = QtWidgets.QPushButton(Dialog)
        self.renamebutton.setGeometry(QtCore.QRect(120, 90, 75, 23))
        self.renamebutton.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.renamebutton.setObjectName("renamebutton")
        self.renamebutton.clicked.connect(self.folderrename)
        self.renamebutton.clicked.connect(Dialog.done)
        self.retranslateUi_r(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)
        Dialog.show()
        Dialog.exec_()

    def folderrename(self):
        if 'savetofolderpath' in globals():
            try:
                e=savetofolderpath.rfind('/')
                os.rename(savetofolderpath,savetofolderpath[0:e]+'/'+self.renamefolder.text())
            except:
                pass
        else:
            msg = QMessageBox(QMessageBox.Warning, "Warning",
                              "Select a folder to rename",
                              QMessageBox.Ok)
            icon = QtGui.QIcon()
            icon.addPixmap(QtGui.QPixmap("ico/027.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
            msg.setWindowIcon(icon)
            msg.exec_()

    def deletefold(self):
        Dialog_delete = QtWidgets.QDialog()
        Dialog_delete.setObjectName("Dialog_delete")
        Dialog_delete.resize(394, 127)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("ico/027.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        Dialog_delete.setWindowIcon(icon)
        Dialog_delete.setStyleSheet("background-color: rgb(194, 195, 255);")
        self.label = QtWidgets.QLabel(Dialog_delete)
        self.label.setGeometry(QtCore.QRect(30, 0, 391, 78))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.deleteb = QtWidgets.QPushButton(Dialog_delete)
        self.deleteb.setGeometry(QtCore.QRect(150, 90, 75, 23))
        self.deleteb.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.deleteb.setObjectName("deleteb")
        self.cancelb = QtWidgets.QPushButton(Dialog_delete)
        self.cancelb.setGeometry(QtCore.QRect(240, 90, 75, 23))
        self.cancelb.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.cancelb.setObjectName("cancelb")
        #self.cancelb.clicked(Dialog_delete.close())
        self.deleteb.clicked.connect(self.deleteselectedfolder)
        self.retranslateUi_delete(Dialog_delete)
        QtCore.QMetaObject.connectSlotsByName(Dialog_delete)
        self.Dialog_delete=Dialog_delete
        Dialog_delete.show()

        print('deleted')

    def deleteselectedfolder(self):
        if 'savetofolderpath' in globals():
            try:
                shutil.rmtree(savetofolderpath)
                self.Dialog_delete.close()

            except:
                pass
        else:
            msg = QMessageBox(QMessageBox.Warning, "Warning",
                              "Select a folder to delete",
                              QMessageBox.Ok)
            icon = QtGui.QIcon()
            icon.addPixmap(QtGui.QPixmap("ico/027.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
            msg.setWindowIcon(icon)
            msg.exec_()


    def filenametrigger(self, action):
        renamepref=action.text()
        pickle.dump(renamepref, open(docpath+"\syslog2.pkl", "wb"))
        print(action.text())
    def storagetrigger(self):
        self.path = QFileDialog.getExistingDirectory(None, "Open Directory", "C:/",
                                                           QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks)
        pickle.dump(self.path, open(docpath+"\syslog1.pkl", "wb"))
        self.tree.setRootIndex(self.model.index(self.path))
        print(self.path)

    def retranslateUi_delete(self, Dialog_delete):
        _translate = QtCore.QCoreApplication.translate
        Dialog_delete.setWindowTitle(_translate("Dialog_delete", "Warning"))
        self.label.setText(
            _translate("Dialog_delete", "Deleting a folder will delete all the files. Wish to continue?"))
        self.deleteb.setText(_translate("Dialog_delete", "Delete"))
        self.cancelb.setText(_translate("Dialog_delete", "Cancel"))

    def retranslateUi_add(self, AddDialog):
        _translate = QtCore.QCoreApplication.translate
        AddDialog.setWindowTitle(_translate("AddDialog", "Add from local"))
        self.label.setText(_translate("AddDialog", "File directory"))
        self.openfiledialog.setToolTip(_translate("AddDialog", "File dialog"))
        self.openfiledialog.setText(_translate("AddDialog", "..."))
        self.import_2.setToolTip(_translate("AddDialog", "Import the selected file"))
        self.import_2.setText(_translate("AddDialog", "Import"))
        self.label_2.setText(_translate("AddDialog", "Enter DOI"))
        self.enterdoi.setPlaceholderText(_translate("AddDialog", "Enter DOI"))
        self.label_3.setText(_translate("AddDialog", "                                                    OR"))
        self.typemanually.setToolTip(_translate("AddDialog", "Use this only if you dont find DOI"))
        self.typemanually.setText(_translate("AddDialog", "Type Manually"))

    def retranslateUi_man(self, manualentry):
        _translate = QtCore.QCoreApplication.translate
        manualentry.setWindowTitle(_translate("manualentry", "Manual Entry"))
        self.label.setText(_translate("manualentry", "           Title"))
        self.mtitle.setPlaceholderText(_translate("manualentry", "Enter title"))
        self.label_2.setText(_translate("manualentry", "         Authors"))
        self.mauthors.setPlaceholderText(_translate("manualentry", "Use comma to include authors"))
        self.label_3.setText(_translate("manualentry", "         Journal"))
        self.mjournal.setPlaceholderText(_translate("manualentry", "Enter journal"))
        self.label_4.setText(_translate("manualentry", "          Year"))
        self.myear.setPlaceholderText(_translate("manualentry", "Enter Year"))
        self.label_5.setText(_translate("manualentry", "          Page"))
        self.mpage.setPlaceholderText(_translate("manualentry", "Enter Page number"))
        self.label_6.setText(_translate("manualentry", "          Issue"))
        self.missue.setPlaceholderText(_translate("manualentry", "Enter Issie number"))
        self.label_7.setText(_translate("manualentry", "        Volume"))
        self.mvolume.setPlaceholderText(_translate("manualentry", "Enter volume"))
        self.label_8.setText(_translate("manualentry", "          ISSN"))
        self.missn.setPlaceholderText(_translate("manualentry", "Enter ISSN number"))
        self.label_9.setText(_translate("manualentry", "           DOI"))
        self.mdoi.setPlaceholderText(_translate("manualentry", "Enter DOI"))
        self.label_10.setText(_translate("manualentry", "           URL"))
        self.murl.setPlaceholderText(_translate("manualentry", "Enter URL"))


    def retranslateUi_d(self, Dialog_d):
        _translate = QtCore.QCoreApplication.translate
        Dialog_d.setWindowTitle(_translate("Dialog_d", "Enter DOI"))
        self.label.setText(_translate("Dialog_d", "Enter DOI"))
        self.pastedoi.setPlaceholderText(_translate("Dialog_d", "Paste the DOI of the Article"))
        self.getdoi.setToolTip(_translate("Dialog_d", "Click to download and import"))
        self.getdoi.setText(_translate("Dialog_d", "Download"))
        self.typemanual.setToolTip(_translate("Dialog_d", "Enter all the details manually"))
        self.typemanual.setText(_translate("Dialog_d", "Type Manually"))


    def retranslateUi_r(self,Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Rename folder"))
        self.label.setText(_translate("Dialog", "Enter folder name"))
        self.renamebutton.setText(_translate("Dialog", "Rename"))
    def retranslateUi_c(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Create folder"))
        self.label.setText(_translate("Dialog", "Enter folder name"))
        self.newfoldercreate.setText(_translate("Dialog", "Create"))
        self.radiobutton_c.setToolTip(_translate("Dialog", "Creates folder in your main directory"))
        self.radiobutton_c.setText(_translate("Dialog", "Create in Main"))

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Download status"))
        self.qbutton.setText(_translate("Dialog", "Done"))



class External(QThread,QtWidgets.QErrorMessage):
    """
    Runs a counter thread.
    """
    countChanged = pyqtSignal(int)




    def run(self):
        if 'link' and 'savetofolderpath' in globals() is not None:
            print(link)
            print(savetofolderpath)
            threadactive = True
            # link='https://www.pnas.org/content/105/38/14262.short'
            count = 0
            self.countChanged.emit(count)
            # if savetofolder is None:
            URL = 'https://sci-hub.tw/'
            sreq = requests.Session()
            count = 20
            self.countChanged.emit(count)
            soup = BeautifulSoup(sreq.get(URL).content, features="html5lib")
            form = soup.find('form')
            print(form)
            fields = form.findAll('input')
            print(fields)
            if threadactive == True:
                count = 30
                self.countChanged.emit(count)
                formdata = dict((field.get('name'), field.get('value')) for field in fields)
                formdata['request'] = link
                posturl = urljoin(URL, form['action'])
                print(posturl)

            if threadactive == True:
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
                print(src)
                if src[0:2]=='//':
                    src='https:'+src
                print(src)
                r = requests.get(src, allow_redirects=True)
                pdfl = savetofolderpath + '/test.pdf'
                print(pdfl)
                open(pdfl, 'wb').write(r.content)
                pattern = re.compile(r"var doi = '(.*?)';$", re.MULTILINE | re.DOTALL)
                script = soups.find("script", text=pattern)
                doi = pattern.search(script.text).group(1)
                count = 70
                self.countChanged.emit(count)
                print(doi)

            if threadactive == True:
                works = Works()
                meta = works.doi(doi)
                count = 80
                self.countChanged.emit(count)
                try:
                    title = meta['title']
                    title = title[0]
                    title=title.replace('/','')
                    title=title.replace(':','')
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
                        author[i]=author[i].replace('/','')
                except KeyError:
                    author = None
                count = 90
                self.countChanged.emit(count)
                try:
                    journal = meta['container-title']
                    journal = journal[0]
                    journal=journal.replace('/','')
                except KeyError:
                    journal = None
                try:
                    yr = meta['created']
                    yrs = yr['date-time']
                    year = yrs[:4]
                    year=year.replace('/','')
                except KeyError:
                    year = None
                try:
                    page=meta['page']
                    page=page.replace('/','')
                except KeyError:
                    page=None
                try:
                    issue=meta['issue']
                    issue=issue.replace('/','')
                except KeyError:
                    issue=None
                try:
                    volume=meta['volume']
                    volume=volume.replace('/','')
                except KeyError:
                    volume=None
                try:
                    issn=meta['ISSN']
                    issn=issn[0]
                    issn=issn.replace('/','')
                except KeyError:
                    issn=None
                try:
                    url=meta['URL']

                except KeyError:
                    url=None
                
                filerename=pickle.load(open(docpath+"\syslog2.pkl", "rb"))
                print(filerename)
                read = PdfReader(pdfl)
                read.Info
                if author is None:
                    author=['XXX','COULD NOT FETCH AUTHOR DETAILS','ADD MANUALLY']
                metadatain = PdfDict(Xauthor=author,Xdoi=doi,Xtitle=title,Xjournal=journal,Xyear=year,Xpage=page,Xissue=issue,Xvolume=volume,Xissn=issn,Xurl=url,Xdate=date.today())
                print('me')
                read.Info.update(metadatain)
                print(journal)
                print(author)
                print(year)
                print(title)
                
                if title is None:
                    title=''
                if journal is None:
                    journal=''
                if year is None:
                    year=''
                if filerename=='Author-Title-Journal-Year':
                    print(savetofolderpath+'/'+author[0]+'--'+title+'--'+journal+'--'+year+'.pdf')
                    PdfWriter().write(savetofolderpath+'/'+author[0]+'--'+title+'--'+journal+'--'+year+'.pdf',read)
                    #PdfWriter().write('C:/Users/LeBert/Desktop/testdd.pdf',read)

                if filerename=='Title-Author-Journal-Year':
                    PdfWriter().write(savetofolderpath+'/'+title+'--'+author[0]+'--'+journal+'--'+year+'.pdf',read)
                if filerename=='Journal-Author-Title-Year':
                    PdfWriter().write(savetofolderpath+'/'+journal+'--'+author[0]+'--'+title+'--'+year+'.pdf',readd)
                if filerename=='Year-Author-Title-Journal':
                    PdfWriter().write(savetofolderpath+'/'+year+'--'+author[0]+'--'+title+'--'+journal+'.pdf',read)
                if filerename=='Year-Journal-Author-Title':
                    PdfWriter().write(savetofolderpath+'/'+year+'--'+journal+'--'+author[0]+'--'+title+'.pdf',read)
                os.remove(pdfl)
                #self.tree.connect(self.fileview)
                count = 100
                self.countChanged.emit(count)
        else:
            pass

class trialstart(QtWidgets.QMainWindow):
    def __init__(self):
        print("Trial days remaining %d" % trial_days)
        msg = QMessageBox(QMessageBox.Warning, "SciX beta",
                          "Trial days remaining %d"%trial_days,
                          QMessageBox.Ok)
        # msg.setWindowIcon(QIcon(":/icons/app.svg"
        msg.exec_()
        start()
class trialend(QtWidgets.QMainWindow):
    def __init__(self):
        print("There are no trial days remaining. You must activate now to continue to use this app.")
        msg = QMessageBox(QMessageBox.Warning, "Trial Expired",
                          "Trial days remaining %d" % trial_days,
                          QMessageBox.Ok)
        # msg.setWindowIcon(QIcon(":/icons/app.svg"
        msg.exec_()
        #time.sleep(1)
        #exit()
class trialerror(QtWidgets.QMainWindow):
    def __init__(self):
        msg = QMessageBox(QMessageBox.Warning, "Error",
                          "Check your Internet",
                          QMessageBox.Ok)
        # msg.setWindowIcon(QIcon(":/icons/app.svg"
        msg.exec_()
        #time.sleep(1)
        #exit()

class start():
    def __init__(self):
        app = QtWidgets.QApplication(sys.argv)
        window = Ui()

        app.exec_()



DAYS_BETWEEN_CHECKS = 90
GRACE_PERIOD_LENGTH = 14
isGenuine = False
trial_days = 0
verified_trial = True

try:
    # TODO: go to the version page at LimeLM and
        # paste this GUID here
    ta = TurboActivate('wrhcbncwucprfbtdcos2a3bfczgh4ly', TA_USER)

        # Check if we're activated, and every 90 days verify it with the activation servers
        # In this example we won't show an error if the activation was done offline
        # (see the 3rd parameter of the IsGenuine() function)
        # https://wyday.com/limelm/help/offline-activation/
    gen_r = ta.is_genuine_ex(DAYS_BETWEEN_CHECKS, GRACE_PERIOD_LENGTH, True)

    isGenuine = (gen_r == IsGenuineResult.Genuine
                     or gen_r == IsGenuineResult.GenuineFeaturesChanged

                     # an internet error means the user is activated but
                     # TurboActivate failed to contact the LimeLM servers
                     or gen_r == IsGenuineResult.InternetError
                     )
    print(isGenuine)
except TurboActivateError as e:
    sys.exit("Failed to check if activated: " + str(e))

if not isGenuine:
    try:
        # Start or re-validate the trial if it has already started.
        # This need to be called at least once before you can use
        # any other trial functions.
        ta.use_trial(verified_trial)

        # Get the number of trial days remaining.
        trial_days = ta.trial_days_remaining(verified_trial)
        #trial_days=0
        if trial_days > 0:
            apps = QtWidgets.QApplication(sys.argv)
            window = trialstart()

            apps.exec_()


        else:
            appen = QtWidgets.QApplication(sys.argv)
            window = trialend()

            appen.exec_()

    except TurboActivateTrialExpiredError as e:
        print("There are no trial days remaining. You must activate now to continue to use this app.")
        appen = QtWidgets.QApplication(sys.argv)
        window = trialend()

        appen.exec_()
    except TurboActivateError as e:
        print("Failed to start the trial: " + str(e))
        apper = QtWidgets.QApplication(sys.argv)
        window = trialerror()

        apper.exec_()




