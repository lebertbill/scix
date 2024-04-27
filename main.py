#-*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function,
                        unicode_literals, generator_stop)
import os
os.environ["QT_MAC_WANTS_LAYER"] = "1"
from PyQt5 import uic, QtGui
from PyQt5.QtCore import QThread, pyqtSignal, QDir
from PyQt5.QtWidgets import *
from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtCore import *
import zipfile
import sys
import time
import requests
from bs4 import BeautifulSoup
import unicodedata
import os
import json
import textwrap
from urllib.parse import urlparse
from urllib.request import urljoin, urlopen, Request
import re
from crossref.restful import Works, Etiquette
from habanero import counts
from habanero import Crossref
import shutil
import pickle
import pikepdf
from pdfrw import PdfReader, PdfWriter, PdfDict,PdfParseError
import PyPDF2
from datetime import date
from hurry.filesize import size, si
#from win32com.shell import shell, shellcon
import warnings
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QFileDialog,\
    QMessageBox
from PyQt5 import QtCore
from PyQt5 import QtWidgets
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from oauth2client.service_account import ServiceAccountCredentials
from google.auth.transport.requests import Request
import platform
from difflib import SequenceMatcher
import subprocess
import pyAesCrypt
import webbrowser
import clipboard

#pyAesCrypt.decryptFile(r'exthread.dll',r'download.py','',64*1024)

from download import Externalthread
from pdftitle import get_title_from_file

warnings.filterwarnings("ignore")
global tempcurrentid
tempcurrentid=None
global docpath
#docpath = shell.SHGetFolderPath(0, shellcon.CSIDL_PERSONAL, None, 0)
docpath = '/Users/lebertsambillgates/Documents/SciX/alpha' + '/SciX'
print(docpath)

try:
    os.mkdir(docpath)
except:
    pass

try:
  os.remove(docpath+'\currentid.txt')
except:
   pass



class Ui(QtWidgets.QMainWindow,QWidget):

    def __init__(self,*args, **kwargs):

        super(Ui, self).__init__(*args, **kwargs)
        uic.loadUi('/Users/lebertsambillgates/PycharmProjects/SciX/color.ui', self)
        #############toolbar#############################
        sys.excepthook = self.show_exception_and_exit
        self.setMaximumHeight(1800)
        self.setMaximumWidth(2560)
        self.timer=QTimer()
        self.adobecheck=False
        self.openadobe.changed.connect(self.setadobe)
        self.actiondelete.triggered.connect(self.deletefiledialog)
        self.actionLocalbackup.triggered.connect(self.backuptrigger)
        self.actionCount_Citation.triggered.connect(self.citecount)
        self.actionOpen_Explorer.triggered.connect(self.openexplorer)
        self.actionRefresh_2.triggered.connect(self.refreshmsg)
        self.actionTerms_and_conditions.triggered.connect(self.openterms)
        self.actionUser_Guide.triggered.connect(self.openuserguide)
        self.actionPrivacy_policy.triggered.connect(self.openprivacy)
        self.actionDonate.triggered.connect(self.opendonate)
        self.actionFeedback.triggered.connect(self.openfeedback)
        self.actionAbout.triggered.connect(self.openabout)
        self.actionExit.triggered.connect(sys.exit)
        app.aboutToQuit.connect(self.CloseEvent)
        ##########shortcut##############

        self.squery.setShortcut("Ctrl+Return")
        self.downloadbutton.setShortcut("Space")

        self.sfind = QShortcut(QtGui.QKeySequence("Ctrl+f"), self)
        self.sfind.activated.connect(self.sstring.setFocus)
        
        #########Download section################
        self.button = self.findChild(QtWidgets.QToolButton, 'downloadbutton')  # Find the button
        self.input = self.findChild(QtWidgets.QLineEdit, 'inputurl')
        self.button.clicked.connect(self.scidexe)  # Remember to pass the definition/method, not the return value!
        ##########Explorer###################
        global maintab
        maintab=self.maintab
        self.maintab.tabBar().setTabButton(0, QtWidgets.QTabBar.RightSide, None)
        self.maintab.tabBar().setTabButton(1, QtWidgets.QTabBar.RightSide, None)
        self.maintab.tabBar().setTabButton(2, QtWidgets.QTabBar.RightSide, None)
        self.maintab.tabCloseRequested.connect(self.closetab)
        self.model = QFileSystemModel()
        self.model.setRootPath(QDir.rootPath())
        self.model.setReadOnly(False)
        self.model.setFilter(QtCore.QDir.AllDirs | QtCore.QDir.NoDotAndDotDot)
        self.tree.setModel(self.model)
        try:
            rootset = pickle.load(open(docpath + "\syslog1.pkl", "rb"))
            self.tree.setRootIndex(self.model.index(rootset))
        except:
            self.tree.setRootIndex(self.model.index("C:"))



        self.tree.clicked.connect(self.fileview)

        # self.tree.setSelectionMode(QtWidgets.QAbstractItemView.ContiguousSelection) unselect
        self.tree.setAnimated(False)
        self.tree.setIndentation(20)
        self.tree.setSortingEnabled(True)
        for i in range(1, self.tree.model().columnCount()):
            self.tree.header().hideSection(i)
        ##########FILELIST###########################
        self.modellist = QtGui.QStandardItemModel()
        self.modellist.setHorizontalHeaderLabels(['Author', 'Title', 'Journal', 'Year', 'Added on'])
        self.filelist.setModel(self.modellist)
        self.filelist.setContextMenuPolicy(Qt.CustomContextMenu)
        self.filelist.customContextMenuRequested.connect(self.customMenu)
        self.doiupdate.clicked.connect(self.upbydoi)
        #self.collapsebutton.clicked.connect(self.collapsedetailstab)
        self.tabwidgetflag = False
        ############COMBO############
        self.filtercombo = self.findChild(QtWidgets.QComboBox, 'filtercombo')
        self.filtercombo.currentIndexChanged.connect(self.combo)
        self.sortlist = self.findChild(QtWidgets.QListWidget, 'sortlist')

        self.newfolder = self.findChild(QtWidgets.QToolButton, 'newfolder')
        self.newfolder.clicked.connect(self.makedir)
        self.deletefolder = self.findChild(QtWidgets.QToolButton, 'deletefolder')
        self.deletefolder.clicked.connect(self.deletefold)
        self.renamefolder.clicked.connect(self.folderrename_ui)
        self.actionStorage_Location.triggered.connect(self.storagetrigger)
        group = QActionGroup(self.menuRename_preference)
        texts = ["Author-Title-Journal-Year", "Title-Author-Journal-Year", "Journal-Author-Title-Year",
                 "Year-Author-Title-Journal", "Year-Journal-Author-Title"]
        self.notessave.clicked.connect(self.savenotes)
        self.savetag.clicked.connect(self.searchtag)
        try:
            renamepref = pickle.load(open(docpath + "\syslog2.pkl", "rb"))
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
        self.feed=QWebEngineView()
        self.feed.contextMenuEvent=self.feedcontext
        try:
            link = str(pickle.load(open(docpath + "\link.pkl", "rb"))).strip("''")
            self.feed.load(QUrl(link))
            self.feedlayout.addWidget(self.feed)
        except:
            link=QUrl.fromLocalFile(os.path.dirname(__file__)+"/ico/053.jpg")
            self.feed.load(QUrl(link))
            self.feedlayout.addWidget(self.feed)

        #################SearchX###############################################
        self.searchx.setMovable(False)
        self.searchx.setDocumentMode(True)
        self.tabnumber=0
        self.browser = []
        self.searchx.tabBarDoubleClicked.connect(self.tab_open_doubleclick)
        self.searchx.currentChanged.connect(self.current_tab_changed)
        self.searchx.setTabsClosable(True)
        self.searchx.tabCloseRequested.connect(self.close_current_tab)
        self.addtab.clicked.connect(lambda _: self.add_new_tab(QUrl('https://google.com/'), 'Google'))
        self.add_new_tab(QUrl('https://scholar.google.com/'), 'Homepage')
        self.urlbox.returnPressed.connect(self.navigate_to_url)
        self.back.clicked.connect(lambda: self.searchx.currentWidget().back())
        self.forward.clicked.connect(lambda: self.searchx.currentWidget().forward())
        self.refresh.clicked.connect(lambda: self.searchx.currentWidget().reload())
        self.home.clicked.connect(self.navigate_home)
        self.stop.clicked.connect(lambda: self.searchx.currentWidget().stop())

        #myevent = PatternMatchingEventHandler("*", "", False, True)
        #myevent.on_created = self.checkwordT
        #myevent.on_modified = self.checkwordT
        #myevent.on_deleted = self.checkwordF
        #obs = Observer()
        #obs.schedule(myevent, docpath, True)
        #obs.start()
     #####################Searchquery##########################3
        self.squery.clicked.connect(self.searchquery)
        self.saveedit.clicked.connect(self.editsave)
    #####################updates######################
        QApplication.processEvents()
        self.startnoti()
        self.extensionthread()
    def extensionthread(self):
        self.sciexten = scixexthread()
        self.sciexten.start()
        self.sciexten.runx.connect(self.runfromextension)
    def runfromextension(self,value):
        print(value)
        self.inputurl.setText(value)
        self.scidexe()
    def startnoti(self):
        #sys.excepthook = self.show_exception_and_exit
        self.upnoti=notithread()
        self.upnoti.start()
        self.upnoti.msg.connect(self.notiupdate)
        #self.notithread.start(notiwork)
    def customMenu(self,point):
        sys.excepthook = self.show_exception_and_exit
        self.contexttree=QtWidgets.QMenu(self.filelist)
        aropen=self.contexttree.addAction("Open")
        arcut=self.contexttree.addAction('Cut')
        arcopy=self.contexttree.addAction('Copy')
        arpaste=self.contexttree.addAction('Paste')
        ardelete=self.contexttree.addAction("Delete")
        arcopy.triggered.connect(self.rightcopy)
        arpaste.triggered.connect(self.rightpaste)
        arcut.triggered.connect(self.rightcut)
        aropen.triggered.connect(self.openrightclicked)
        ardelete.triggered.connect(self.deleterightclicked)
        self.contexttree.exec_(self.filelist.mapToGlobal(point))
    def rightcopy(self):
        sys.excepthook = self.show_exception_and_exit
        indexes = self.filelist.selectedIndexes()
        print(indexes)
        dupfile = None
        self.copylist=[]
        self.copylistname=[]
        for index in indexes:
            item = self.modellist.itemFromIndex(index)
            file = self.dict[str(item)]
            self.copylist.append(self.savetofolderpath + '/' + file)
            self.copylistname.append(file)
        self.cutflag=False
    def rightcut(self):
        sys.excepthook = self.show_exception_and_exit
        indexes = self.filelist.selectedIndexes()
        print(indexes)
        dupfile = None
        self.copylist = []
        self.copylistname = []
        for index in indexes:
            item = self.modellist.itemFromIndex(index)
            file = self.dict[str(item)]
            self.copylist.append(self.savetofolderpath + '/' + file)
            self.copylistname.append(file)
        self.cutflag=True
    def rightpaste(self):
        sys.excepthook = self.show_exception_and_exit
        dupfile = None
        if self.cutflag==False:
            for i in range(len(self.copylist)):
                self.statusBar.setStyleSheet('background-color: rgb(67, 211, 255);')
                self.statusBar.showMessage('Copying:'+self.copylist[i])
                self.statusBar.show()
                qApp.processEvents()
                self.timer.singleShot(10000, self.statusBar.hide)
                if self.copylist[i] != dupfile:
                    shutil.copyfile(self.copylist[i], self.savetofolderpath + '/' + self.copylistname[i])
                    try:
                        shutil.copyfile(self.copylist[i].strip('.pdf') + '.bib',
                                        self.savetofolderpath + '/' + self.copylistname[i].strip('.pdf') + '.bib')
                    except:
                        pass
                    dupfile = self.copylist[i]
        else:
            for i in range(len(self.copylist)):
                self.statusBar.setStyleSheet('background-color: rgb(67, 211, 255);')
                self.statusBar.showMessage('Moving:' + self.copylist[i])
                self.statusBar.show()
                qApp.processEvents()
                self.timer.singleShot(10000, self.statusBar.hide)
                if self.copylist[i] != dupfile:
                    shutil.move(self.copylist[i], self.savetofolderpath + '/' + self.copylistname[i])
                    try:
                        shutil.move(self.copylist[i].strip('.pdf') + '.bib',
                                        self.savetofolderpath + '/' + self.copylistname[i].strip('.pdf') + '.bib')
                    except:
                        pass
                    dupfile = self.copylist[i]
        self.statusBar.setStyleSheet('background-color: rgb(30, 255, 82);')
        self.statusBar.showMessage('Done', msecs=10000)
        self.statusBar.show()
        qApp.processEvents()
        self.timer.singleShot(10000, self.statusBar.hide)
        self.fileview(indexx=self.indexx)
    def deleterightclicked(self):
        sys.excepthook = self.show_exception_and_exit
        index = self.filelist.currentIndex()
        self.rightdeletefile()
    def openrightclicked(self):
        sys.excepthook = self.show_exception_and_exit
        index = self.filelist.currentIndex()
        self.treeitemdoubleClicked(index)
    def editsave(self):
        sys.excepthook = self.show_exception_and_exit
        li=self.authorinfo.toPlainText().split('  ')
        s=str(li[0])
        author=list(s.splitlines())
        title=self.titleinfo.toPlainText()
        journal=self.journalinfo.toPlainText()
        issn=self.issninfo.toPlainText()
        doi=self.doiinfo.toPlainText()
        url=self.urlinfo.toPlainText()
        item = self.modellist.itemFromIndex(self.notesindex)
        global file
        file = self.dict[str(item)]
        print(file)
        read=PdfReader(self.savetofolderpath+'/'+file)
        metadatain = PdfDict(Xauthor=author, Xdoi=doi, Xtitle=title, Xjournal=journal,Xissn=issn, Xurl=url)
        print('me')
        read.Info.update(metadatain)
        print(read.Info)
        PdfWriter().write(self.savetofolderpath + '/' + file, read)
        self.statusBar.setStyleSheet('background-color: rgb(30, 255, 82);')
        self.statusBar.showMessage('Done editing', msecs=10000)
        self.statusBar.show()
        qApp.processEvents()
        self.timer.singleShot(10000, self.statusBar.hide)
        self.fileview(indexx=self.indexx)
    def add_new_tab(self, qurl=None, label="Blank"):
        sys.excepthook = self.show_exception_and_exit
        if qurl is None:
            qurl = QUrl('')

        self.browser.append(QWebEngineView())
        self.browser[self.tabnumber].setUrl(qurl)
        i = self.searchx.addTab(self.browser[self.tabnumber], label)
        print(i)
        self.searchx.setCurrentIndex(i)
        self.browser[i].urlChanged.connect(lambda qurl, browser=self.browser[i]:
                                        self.update_urlbar(qurl, self.browser[i]))

        self.browser[i].loadFinished.connect(lambda _, i=i, browser=self.browser[i]:
                                          self.searchx.setTabText(i, self.browser[i].page().title()))
        self.browser[i].contextMenuEvent=self.searchxcontext
        self.tabnumber=self.tabnumber+1
        print(self.tabnumber)
    def feedcontext(self,event):
        sys.excepthook = self.show_exception_and_exit
        searchxmenu = QtWidgets.QMenu(self)
        back = searchxmenu.addAction("Back")
        forward = searchxmenu.addAction("Forward")
        refresh=searchxmenu.addAction("Refresh")
        openext = searchxmenu.addAction("Open in External browser")
        forward.triggered.connect(self.feedforward)
        openext.triggered.connect(self.feedopenext)
        back.triggered.connect(self.feedbackward)
        refresh.triggered.connect(self.feedrefresh)
        searchxmenu.exec_(event.globalPos())
    def feedforward(self):
        sys.excepthook = self.show_exception_and_exit
        self.feed.forward()
    def feedopenext(self):
        sys.excepthook = self.show_exception_and_exit
        url=self.feed.page().url()
        url = url.toString()
        webbrowser.open_new_tab(url)
    def feedbackward(self):
        sys.excepthook = self.show_exception_and_exit
        self.feed.back()
    def feedrefresh(self):
        sys.excepthook = self.show_exception_and_exit
        self.feed.reload()
    def searchxcontext(self,event):
        sys.excepthook = self.show_exception_and_exit
        searchxmenu=QtWidgets.QMenu(self)
        openinnew=searchxmenu.addAction("Open in new tab")
        openext=searchxmenu.addAction("Open in External browser")
        copylink=searchxmenu.addAction("Copy link")
        openinnew.triggered.connect(self.rightclicknewtab)
        openext.triggered.connect(self.openext)
        copylink.triggered.connect(self.linkcopy)
        searchxmenu.exec_(event.globalPos())
    def rightclicknewtab(self):
        sys.excepthook = self.show_exception_and_exit
        num=self.searchx.currentIndex()
        qurl=self.browser[num].page().contextMenuData().linkUrl()
        print(qurl)
        self.add_new_tab(qurl=qurl,label="Loading...")
    def openext(self):
        sys.excepthook = self.show_exception_and_exit
        num = self.searchx.currentIndex()
        qurl = self.browser[num].page().contextMenuData().linkUrl()
        qurl=qurl.toString()
        webbrowser.open_new_tab(qurl)
    def linkcopy(self):
        sys.excepthook = self.show_exception_and_exit
        num = self.searchx.currentIndex()
        qurl = self.browser[num].page().contextMenuData().linkUrl()
        qurl = qurl.toString()
        clipboard.copy(qurl)
    def tab_open_doubleclick(self, i):
        sys.excepthook = self.show_exception_and_exit
        if i == -1:  # No tab under the click
            self.add_new_tab()
    def current_tab_changed(self, i):
        sys.excepthook = self.show_exception_and_exit
        qurl = self.searchx.currentWidget().url()
        self.update_urlbar(qurl, self.searchx.currentWidget())
        self.update_title(self.searchx.currentWidget())
    def close_current_tab(self, i):
        sys.excepthook = self.show_exception_and_exit
        if self.searchx.count() < 2:
            return

        self.searchx.removeTab(i)
    def update_title(self, browser):
        sys.excepthook = self.show_exception_and_exit
        if browser != self.searchx.currentWidget():
            # If this signal is not from the current tab, ignore
            return

        title = self.searchx.currentWidget().page().title()
    def about(self):
        sys.excepthook = self.show_exception_and_exit
        dlg = AboutDialog()
        dlg.exec_()
    def open_file(self):
        sys.excepthook = self.show_exception_and_exit
        filename, _ = QFileDialog.getOpenFileName(self, "Open file", "",
                                                  "Hypertext Markup Language (*.htm *.html);;"
                                                  "All files (*.*)")

        if filename:
            with open(filename, 'r') as f:
                html = f.read()

            self.searchx.currentWidget().setHtml(html)
            self.urlbox.setText(filename)
    def save_file(self):
        sys.excepthook = self.show_exception_and_exit
        filename, _ = QFileDialog.getSaveFileName(self, "Save Page As", "",
                                                  "Hypertext Markup Language (*.htm *html);;"
                                                  "All files (*.*)")

        if filename:
            html = self.searchx.currentWidget().page().toHtml()
            with open(filename, 'w') as f:
                f.write(html.encode('utf8'))
    def print_page(self):
        sys.excepthook = self.show_exception_and_exit
        dlg = QPrintPreviewDialog()
        dlg.paintRequested.connect(self.browser.print_)
        dlg.exec_()
    def navigate_home(self):
        sys.excepthook = self.show_exception_and_exit
        self.searchx.currentWidget().setUrl(QUrl("http://www.google.com"))
    def navigate_to_url(self):  # Does not receive the Url
        sys.excepthook = self.show_exception_and_exit
        q = QUrl(self.urlbox.text())
        if q.scheme() == "":
            q.setScheme("http")

        self.searchx.currentWidget().setUrl(q)
    def update_urlbar(self, q, browser=None):
        sys.excepthook = self.show_exception_and_exit
        ic = QtGui.QIcon()
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
    def combo(self, findex):
        sys.excepthook = self.show_exception_and_exit
        try:
            self.sortlist.clear()
            self.findex = findex
            print('combo')
            pdffiles = []
            for dirpath, dirnames, filenames in os.walk(savetofolderpath):
                for filename in [f for f in filenames if f.endswith(".pdf" or ".PDF")]:
                    pdffiles.append(filename)
            #print(pdffiles)
            if findex == 0:
                try:
                    self.fileview(indexx=self.indexx)
                except:
                    pass
            if findex == 1:
                auth = []
                print('auth')
                for i in range(len(pdffiles)):

                    try:
                        readd = PdfReader(savetofolderpath + '/' + pdffiles[i])
                        if readd.Info.Xauthor!=None:
                            for j in range(len(readd.Info.Xauthor)):
                                auth.append(readd.Info.Xauthor[j].decode().strip('()'))
                    except:
                        pass

                fauth = []
                fauth = list(dict.fromkeys(auth))
                print(fauth)
                self.sortlist.addItems(fauth)
                print(auth)

            if findex == 2:
                journ = []
                for i in range(len(pdffiles)):
                    try:
                        readd = PdfReader(savetofolderpath + '/' + pdffiles[i])
                        if readd.Info.Xjournal!=None:
                            journ.append(readd.Info.Xjournal.decode().strip('()'))
                    except:
                        pass
                fjourn = []
                fjourn = list(dict.fromkeys(journ))
                self.sortlist.addItems(fjourn)
              #  print(journ)
            if findex == 3:
                yer = []
                for i in range(len(pdffiles)):
                    try:
                        readd = PdfReader(savetofolderpath + '/' + pdffiles[i])
                        if readd.Info.Xyear!=None:
                            yer.append(readd.Info.Xyear.decode().strip('()'))
                    except:
                        pass
                fyer = []
                fyer = list(dict.fromkeys(yer))
                self.sortlist.addItems(fyer)
                #print(yer)
            # self.sortlist.itemSelectionChanged.connect(self.filterview)
            # self.sortlist.itemActivated.connect(self.filterview)
            self.sortlist.itemClicked.connect(self.filterview)
            self.sortitem_dup = None
        except:
            pass
    def scidexe(self):
       # sys.excepthook = self.show_exception_and_exit
        global link
        link = (self.input.text())
        if len(link) > 0:
            if 'savetofolderpath' in globals():
                icon = QtGui.QIcon()
                icon.addPixmap(QtGui.QPixmap("ico/008.png"), QtGui.QIcon.Normal,
                               QtGui.QIcon.Off)
                Dialog = QDialog(None, QtCore.Qt.WindowSystemMenuHint | QtCore.Qt.WindowTitleHint)
                Dialog.setObjectName("Dialog")
                Dialog.setWindowModality(QtCore.Qt.WindowModal)
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
                self.Dialog = Dialog
                self.progressBar = QtWidgets.QProgressBar(Dialog)
                self.progressBar.setGeometry(QtCore.QRect(30, 60, 271, 16))
                self.progressBar.setProperty("value", 0)
                self.progressBar.setTextVisible(True)
                self.progressBar.setInvertedAppearance(False)
                self.progressBar.setTextDirection(QtWidgets.QProgressBar.TopToBottom)
                self.progressBar.setObjectName("progressBar")
                self.doned = QtWidgets.QToolButton(Dialog)
                self.doned.setGeometry(QtCore.QRect(210, 102, 61, 24))
                font = QtGui.QFont()
                font.setBold(False)
                font.setWeight(50)
                self.doned.setFont(font)
                self.doned.setStyleSheet("background-color: rgb(255, 255, 255);")
                self.doned.setObjectName("doned")
                self.canceld = QtWidgets.QToolButton(Dialog)
                self.canceld.setGeometry(QtCore.QRect(120, 102, 61, 24))
                self.canceld.setStyleSheet("background-color: rgb(255, 255, 255);")
                self.canceld.setObjectName("canceld")
                self.downloadstatus = QtWidgets.QLabel(Dialog)
                self.downloadstatus.setGeometry(QtCore.QRect(4, 135, 200, 13))
                self.downloadstatus.setObjectName("downloadstatus")
                self.doned.clicked.connect(self.hidedownload)
                self.doned.clicked.connect(Dialog.done)
                self.canceld.clicked.connect(self.dexit)
                self.hideflag=False
                Dialog.show()
                self.retranslateUi(Dialog)
                QtCore.QMetaObject.connectSlotsByName(Dialog)
                try:
                    self.calc = Externalthread(link=link, path=savetofolderpath)
                    self.calc.start()
                    self.calc.countChanged.connect(self.onCountChanged)
                    self.calc.statusChanged.connect(self.statusChanged)
                    self.calc.senddoi.connect(self.onsenddoi)
                    self.calc.sendfile.connect(self.extdowncompleted)
                    self.calc.stopsignal.connect(self.dstop)

                except:
                    pass

            else:
                self.statusBar.setStyleSheet('background-color: rgb(255, 28, 28);')
                self.statusBar.showMessage('Select a folder to download')
                self.statusBar.show()
                qApp.processEvents()
                self.timer.singleShot(10000, self.statusBar.hide)

        else:
            self.statusBar.setStyleSheet('background-color: rgb(255, 28, 28);')
            self.statusBar.showMessage('Enter a proper link')
            self.statusBar.show()
            qApp.processEvents()
            self.timer.singleShot(10000, self.statusBar.hide)
    def onsenddoi(self,value):
       # sys.excepthook = self.show_exception_and_exit
        self.doifromthread=value
    def extdowncompleted(self,value):
       # sys.excepthook = self.show_exception_and_exit
        print('here')
        print(os.path.isfile(value))
        self.contcalc=downloadthread(path=value,doi=self.doifromthread,savepath=savetofolderpath)
        self.contcalc.countChanged.connect(self.onCountChanged)
        self.contcalc.statusChanged.connect(self.statusChanged)
        self.contcalc.start()
    def dstop(self):
        sys.excepthook = self.show_exception_and_exit
        print('exit')
        self.calc.exit()
        self.doned.setDisabled(True)
    def statusChanged(self,value):
        #sys.excepthook = self.show_exception_and_exit
        self.downloadstatus.setText(value)
    def dexit(self):
        sys.excepthook = self.show_exception_and_exit
        print('exit')
        try:
            self.contcalc.exit()
        except:
            pass
        self.Dialog.close()
        self.fileview(indexx=self.indexx)
        self.calc.exit()
    def ref(self):
        sys.excepthook = self.show_exception_and_exit
        try:
            self.Dialog.close()
        except:
            pass
        try:
            self.fileview(indexx=self.indexx)
        except:
            pass
    def hidedownload(self):
        sys.excepthook = self.show_exception_and_exit
        self.hideflag=True
    def onCountChanged(self, value):
       # sys.excepthook = self.show_exception_and_exit
        if value==100:
            self.progressBar.setValue(value)
            try:
                self.contcalc.exit()
            except:
                pass
            self.ref()
            self.statusBar.setStyleSheet('background-color: rgb(30, 255, 82);')
            self.statusBar.showMessage('Download completed!')
            self.statusBar.show()
            qApp.processEvents()
          #  self.timer.singleShot(10000, self.statusBar.hide)
        else:
            self.progressBar.setValue(value)
            if self.hideflag==True:
                self.statusBar.setStyleSheet('background-color: rgb(30, 255, 82);')
                self.statusBar.showMessage('Downloading progress: %s' % str(value) + '%')
                self.statusBar.show()
                qApp.processEvents()
                self.timer.singleShot(10000, self.statusBar.hide)
    def filterview(self, itemm):
        sys.excepthook = self.show_exception_and_exit
        sortitem = itemm.text()
        print('filter')
        if sortitem != self.sortitem_dup:
            self.sortitem_dup = sortitem
            print(sortitem)
            print(self.findex)
            print(savetofolderpath)
            self.modellist.clear()
            self.modellist = QtGui.QStandardItemModel()
            self.modellist.setHorizontalHeaderLabels(['Author', 'Title', 'Journal', 'Year', 'Added on'])
            if self.findex == 1:
                pdffiles = []
                for dirpath, dirnames, filenames in os.walk(savetofolderpath):
                    for filename in [f for f in filenames if f.endswith(".pdf" or ".PDF")]:
                        pdffiles.append(filename)
                print(pdffiles)
                self.dict = {}
                for row in range(len(pdffiles)):
                    try:
                        read = PdfReader(savetofolderpath + "/" + pdffiles[row])
                        for j in range(len(read.Info.Xauthor)):
                            if read.Info.Xauthor[j].decode().strip('()') == sortitem:
                                try:
                                    for column in range(5):

                                        Xauthors = ' '
                                        for i in range(len(read.Info.Xauthor)):
                                            Xauthors = Xauthors + read.Info.Xauthor[i].decode().strip('()') + ';'
                                            data = [Xauthors, read.Info.Xtitle.decode().strip('()'),
                                                    read.Info.Xjournal.decode().strip('()'),
                                                    read.Info.Xyear.decode().strip('()'), read.Info.Xdate.strip('()')]
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
                    except:
                        pass



                for i in reversed(range(self.modellist.rowCount())):
                    print(i)
                    if self.modellist.takeItem(i, 4) == None:
                        print('none')
                        self.modellist.removeRow(i)
            if self.findex == 2:

                pdffiles = []
                for dirpath, dirnames, filenames in os.walk(savetofolderpath):
                    for filename in [f for f in filenames if f.endswith(".pdf" or ".PDF")]:
                        pdffiles.append(filename)
                print(pdffiles)
                self.dict = {}
                for row in range(len(pdffiles)):
                    try:
                        read = PdfReader(savetofolderpath + "/" + pdffiles[row])
                        if read.Info.Xjournal.decode().strip('()') == sortitem:
                            try:
                                for column in range(5):

                                    Xauthors = ' '
                                    for i in range(len(read.Info.Xauthor)):
                                        Xauthors = Xauthors + read.Info.Xauthor[i].decode().strip('()') + ';'
                                    data = [Xauthors, read.Info.Xtitle.decode().strip('()'),
                                            read.Info.Xjournal.decode().strip('()'),
                                            read.Info.Xyear.decode().strip('()'), read.Info.Xdate.strip('()')]
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
                    except:
                        pass

                for i in reversed(range(self.modellist.rowCount())):
                    print(i)
                    if self.modellist.takeItem(i, 4) == None:
                        print('none')
                        self.modellist.removeRow(i)
            if self.findex == 3:
                pdffiles = []
                for dirpath, dirnames, filenames in os.walk(savetofolderpath):
                    for filename in [f for f in filenames if f.endswith(".pdf" or ".PDF")]:
                        pdffiles.append(filename)
                print(pdffiles)
                self.dict = {}
                for row in range(len(pdffiles)):
                    try:
                        read = PdfReader(savetofolderpath + "/" + pdffiles[row])
                        if read.Info.Xyear.strip('()') == sortitem:
                            try:
                                for column in range(5):

                                    Xauthors = ' '
                                    for i in range(len(read.Info.Xauthor)):
                                        Xauthors = Xauthors + read.Info.Xauthor[i].decode().strip('()') + ';'
                                    data = [Xauthors, read.Info.Xtitle.decode().strip('()'),
                                            read.Info.Xjournal.decode().strip('()'),
                                            read.Info.Xyear.decode().strip('()'), read.Info.Xdate.strip('()')]
                                    item = QtGui.QStandardItem(data[column])
                                    self.modellist.setItem(row, column, item)
                                    self.dict[str(item)] = pdffiles[row]
                                    # print(item.row())
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
                    except:
                        pass

                for i in reversed(range(self.modellist.rowCount())):
                    print(i)
                    if self.modellist.takeItem(i, 4) == None:
                        print('none')
                        self.modellist.removeRow(i)
        else:
            pass

        self.filelist.setModel(self.modellist)
        self.filelist.header().resizeSection(0, 180)
        self.filelist.header().resizeSection(1, 340)
        self.filelist.header().resizeSection(2, 120)
        self.filelist.header().resizeSection(3, 50)
        self.filelist.header().resizeSection(4, 50)
        self.filedup = None
        self.filelist.doubleClicked.connect(self.treeitemdoubleClicked)
    def fileview(self, indexx):
        sys.excepthook = self.show_exception_and_exit
        self.indexx = indexx
        self.modellist.clear()
        self.modellist = QtGui.QStandardItemModel()
        self.modellist.setHorizontalHeaderLabels(['Author', 'Title', 'Journal', 'Year', 'Added on'])
        self.filelist.setModel(self.modellist)
        self.filelist.header().resizeSection(0,250)
        self.filelist.header().resizeSection(1, 500)
        self.filelist.header().resizeSection(2, 150)
        self.filelist.header().resizeSection(3, 50)
        self.filelist.header().resizeSection(4, 50)
        #self.filelist.columnResized(1, 5, 1000)


        global savetofolderpath
        savetofolderpath = self.model.filePath(indexx)
        self.savetofolderpath = savetofolderpath
        #print(savetofolderpath)

        pdffiles = []
        filenames=[f for f in os.listdir(savetofolderpath) if os.path.isfile(os.path.join(savetofolderpath,f))]
        for filename in [f for f in filenames if f.endswith(".pdf" or ".PDF")]:
            pdffiles.append(filename)

        self.dict = {}
        for row in range(len(pdffiles)):
           # print(len(pdffiles))
            for column in range(5):

                Xauthors = ' '
                try:
                    read = PdfReader(savetofolderpath + "/" + pdffiles[row])
                    for i in range(len(read.Info.Xauthor)):
                        Xauthors = Xauthors + read.Info.Xauthor[i].decode().strip('()') + ';'
                    data = [Xauthors, read.Info.Xtitle.decode().strip('()'),
                            read.Info.Xjournal.decode().strip('()'),
                            read.Info.Xyear.decode().strip('()'), read.Info.Xdate.strip('()')]
                    # print(data)

                    item = QtGui.QStandardItem(data[column])
                    self.modellist.setItem(row, column, item)
                    item.setEditable(False)

                    if column == 0:
                        item.setIcon(QtGui.QIcon('ico/023.png'))
                    else:
                        pass
                except:
                    #print('read:' + pdffiles[row])
                    if column==0:
                        item = QtGui.QStandardItem('')
                        item.setEditable(False)
                        self.modellist.setItem(row, column, item)
                        item.setIcon(QtGui.QIcon('ico/042.png'))
                    elif column == 1:
                        item = QtGui.QStandardItem(pdffiles[row].strip('.pdf'))
                        item.setEditable(False)
                        self.modellist.setItem(row, column, item)
                        #print('read:' + pdffiles[row])
                    else:
                        item = QtGui.QStandardItem('')
                        item.setEditable(False)
                        self.modellist.setItem(row, column, item)
                try:
                    #self.modellist.setItem(row, column, item)
                    self.dict[str(item)] = pdffiles[row]
                   # print('read:' + pdffiles[row])
                    #print(self.dict)
                except:
                    pass
       # print(self.dict)
       # print(len(self.dict))
        self.filtercombo.setCurrentIndex(0)
        self.filedup = None
        self.filelist.doubleClicked.connect(self.treeitemdoubleClicked)
        self.filelist.clicked.connect(self.treeitemsingleclicked)
        self.authorinfo.clear()
        self.titleinfo.clear()
        self.journalinfo.clear()
        self.issninfo.clear()
        self.doiinfo.clear()
        self.urlinfo.clear()
        self.noteswriter.clear()
        self.stringtag.clear()
    def treeitemsingleclicked(self, index):
        sys.excepthook = self.show_exception_and_exit
        self.notesindex=index
        item = self.modellist.itemFromIndex(index)
        global file
        file = self.dict[str(item)]
        if self.filedup != file:
            self.filedup = file
            print(file)
            row = item.row()
            print(row)
            read = PdfReader(self.savetofolderpath + "/" + file)
            global citedoi
            try:
                citedoi = read.Info.Xdoi.decode().strip('()')
            except:
                pass
            self.noteswriter.clear()
            try:
                self.noteswriter.insertPlainText(str(read.Info.Xnotes.decode()).strip('()'))
            except:
                self.noteswriter.insertPlainText("")
            self.stringtag.clear()
            try:
                for i in range(len(read.Info.Xtag)):
                    self.stringtag.insertPlainText('#'+str(read.Info.Xtag[i].decode()).strip('()')+" ")
            except:
                self.stringtag.insertPlainText("")
            try:
                self.statusBar.setStyleSheet('background-color: rgb(255, 238, 49);')
                self.statusBar.showMessage('%s' % str(read.Info.Xtitle.decode()).strip('()'))
                self.statusBar.show()
                qApp.processEvents()
                self.timer.singleShot(5000, self.statusBar.hide)
                self.titleinfo.setText(str(read.Info.Xtitle.decode()).strip('()'))
                self.journalinfo.setText(str(read.Info.Xjournal.decode()).strip('()'))
                self.issninfo.setText(str(read.Info.Xissn.decode()).strip('()'))
                self.urlinfo.setText(str(read.Info.Xurl.decode()).strip('()'))
                self.doiinfo.setText(str(read.Info.Xdoi.decode()).strip('()'))
                self.authorinfo.clear()
                for i in range(len(read.Info.Xauthor)):
                    self.authorinfo.append(str(read.Info.Xauthor[i].decode()).strip('()'))
            except:
                self.titleinfo.clear()
                self.journalinfo.clear()
                self.issninfo.clear()
                self.urlinfo.clear()
                self.doiinfo.clear()
                self.authorinfo.clear()
            self.filedup = None
            #QtWidgets.QTabWidget.setMaximumWidth(0)
            self.tabWidget.setMaximumWidth(16777215)
            self.collapsebutton.setIcon(QtGui.QIcon('ico/055.png'))
            self.tabwidgetflag=True
    def treeitemdoubleClicked(self, index):
        sys.excepthook = self.show_exception_and_exit
        print(index)
        item = self.modellist.itemFromIndex(index)
        print(item)
        print(self.dict)
        self.notesindex=index
        if self.adobecheck==False:
            item = self.modellist.itemFromIndex(index)
            print(item)
            global file
            file = self.dict[str(item)]
            if self.filedup != file:
                self.filedup = file
                print(file)
                row = item.row()
                print(row)
                read = PdfReader(self.savetofolderpath + "/" + file)
                global citedoi
                try:
                    citedoi = read.Info.Xdoi.decode().strip('()')
                except:
                    pass
                self.noteswriter.clear()
                try:
                    self.noteswriter.insertPlainText(str(read.Info.Xnotes.decode()).strip('()'))
                except:
                    self.noteswriter.insertPlainText("")
                self.stringtag.clear()
                try:
                    for i in range(len(read.Info.Xtag)):
                        self.stringtag.insertPlainText('#' + str(read.Info.Xtag[i].decode()).strip('()') + " ")
                except:
                    self.stringtag.insertPlainText("")
                try:
                    self.statusBar.setStyleSheet('background-color: rgb(255, 238, 49);')
                    self.statusBar.showMessage('%s' % str(read.Info.Xtitle.decode()).strip('()'))
                    self.statusBar.show()
                    qApp.processEvents()
                    self.timer.singleShot(5000, self.statusBar.hide)
                    self.titleinfo.setText(str(read.Info.Xtitle.decode()).strip('()'))
                    self.journalinfo.setText(str(read.Info.Xjournal.decode()).strip('()'))
                    self.issninfo.setText(str(read.Info.Xissn.decode()).strip('()'))
                    self.urlinfo.setText(str(read.Info.Xurl.decode()).strip('()'))
                    self.doiinfo.setText(str(read.Info.Xdoi.decode()).strip('()'))
                    self.authorinfo.clear()
                    for i in range(len(read.Info.Xauthor)):
                        self.authorinfo.append(str(read.Info.Xauthor[i].decode()).strip('()'))
                except:
                    self.titleinfo.clear()
                    self.journalinfo.clear()
                    self.issninfo.clear()
                    self.urlinfo.clear()
                    self.doiinfo.clear()
                    self.authorinfo.clear()
                PDFJS = 'file:///web/viewer.html'
                PDF = 'file://' + self.savetofolderpath + '/' + file
                print(PDF)
                self.tab_3 = QWebEngineView()
                # self.tab_2 = QtWidgets.QWidget()
                self.tab_3.setObjectName("tab_2")
                tab3 = self.maintab.addTab(self.tab_3, file)
                self.maintab.setTabIcon(tab3,
                                        QtGui.QIcon('ico/024.png'))
                self.tab_3.load(QtCore.QUrl.fromUserInput('%s?file=%s' % (PDFJS, PDF)))

            else:
                print("nodo")
                pass
        else:

            item = self.modellist.itemFromIndex(index)

            file = self.dict[str(item)]
            print(file)
            if self.filedup != file:
                self.filedup = file
                subprocess.call(["open",self.savetofolderpath + '/' + file])
                #os.system(self.savetofolderpath + '/' + file)
            else:
                pass
    def collapsedetailstab(self):
        #QPushButton.isEnabled()
        if self.tabwidgetflag==False:
            self.tabWidget.setMaximumWidth(16777215)
            self.collapsebutton.setIcon(QtGui.QIcon('ico/055.png'))
            self.filelist.header().resizeSection(0, 150)
            self.filelist.header().resizeSection(1, 340)
            self.filelist.header().resizeSection(2, 120)
            self.filelist.header().resizeSection(3, 50)
            self.filelist.header().resizeSection(4, 50)
            self.tabwidgetflag=True
        else:
            self.tabWidget.setMaximumWidth(0)
            self.tabwidgetflag=False
            self.collapsebutton.setIcon(QtGui.QIcon('ico/054.png'))
            self.filelist.header().resizeSection(0, 250)
            self.filelist.header().resizeSection(1, 500)
            self.filelist.header().resizeSection(2, 150)
            self.filelist.header().resizeSection(3, 50)
            self.filelist.header().resizeSection(4, 50)


    def setadobe(self):
        sys.excepthook = self.show_exception_and_exit
        self.adobecheck=self.openadobe.isChecked()
        print(self.adobecheck)
    def closetab(self, index):
        sys.excepthook = self.show_exception_and_exit
        # index=self.maintab.currentIndex()
        # print(index)
        self.maintab.removeTab(index)
    def savetofolder(self, index):
        sys.excepthook = self.show_exception_and_exit
        global savetofolderpath
        savetofolderpath = self.model.filePath(index)

        print(savetofolderpath)
    def makedir(self):
        sys.excepthook = self.show_exception_and_exit
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
        sys.excepthook = self.show_exception_and_exit
        print('created')
        print('create')
        if self.radiobutton_c.isChecked() == False:
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
            store = pickle.load(open(docpath + "\syslog1.pkl", "rb"))
            path = os.path.join(store, directory)
            os.mkdir(path)
    def folderrename_ui(self):
        sys.excepthook = self.show_exception_and_exit
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
        sys.excepthook = self.show_exception_and_exit
        if 'savetofolderpath' in globals():
            try:
                e = savetofolderpath.rfind('/')
                os.rename(savetofolderpath, savetofolderpath[0:e] + '/' + self.renamefolder.text())
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
        sys.excepthook = self.show_exception_and_exit
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
        # self.cancelb.clicked(Dialog_delete.close())
        self.deleteb.clicked.connect(self.deleteselectedfolder)
        self.retranslateUi_delete(Dialog_delete)
        QtCore.QMetaObject.connectSlotsByName(Dialog_delete)
        self.Dialog_delete = Dialog_delete
        Dialog_delete.show()

        print('deleted')
    def deleteselectedfolder(self):
        sys.excepthook = self.show_exception_and_exit
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
    def deletefiledialog(self):
        sys.excepthook = self.show_exception_and_exit
        Dialog_deletefile = QtWidgets.QDialog()
        Dialog_deletefile.setObjectName("Dialog_deletefile")
        Dialog_deletefile.resize(394, 127)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("ico/027.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        Dialog_deletefile.setWindowIcon(icon)
        Dialog_deletefile.setStyleSheet("background-color: rgb(194, 195, 255);")
        self.label = QtWidgets.QLabel(Dialog_deletefile)
        self.label.setGeometry(QtCore.QRect(30, 0, 391, 78))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.deleteb = QtWidgets.QPushButton(Dialog_deletefile)
        self.deleteb.setGeometry(QtCore.QRect(150, 90, 75, 23))
        self.deleteb.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.deleteb.setObjectName("deleteb")
        self.cancelb = QtWidgets.QPushButton(Dialog_deletefile)
        self.cancelb.setGeometry(QtCore.QRect(240, 90, 75, 23))
        self.cancelb.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.cancelb.setObjectName("cancelb")
        # self.cancelb.clicked(Dialog_delete.close())
        self.deleteb.clicked.connect(self.deleteselectedfile)
        self.cancelb.clicked.connect(Dialog_deletefile.close)
        self.retranslateUi_deletefile(Dialog_deletefile)
        QtCore.QMetaObject.connectSlotsByName(Dialog_deletefile)
        self.Dialog_deletefile = Dialog_deletefile
        Dialog_deletefile.show()
    def rightdeletefile(self):
        sys.excepthook = self.show_exception_and_exit
       # QTreeView.selectedIndexes()
        indexes=self.filelist.selectedIndexes()
        print(indexes)
        dupfile=None
        for index in indexes:
            item = self.modellist.itemFromIndex(index)
            file = self.dict[str(item)]
            print(self.savetofolderpath + '/' + file)
            if file!=dupfile:
                os.remove(self.savetofolderpath + '/' + file)
                try:
                    os.remove(self.savetofolderpath + '/' + file.strip('.pdf')+'.bib')
                except:
                    pass
                dupfile=file
        self.fileview(indexx=self.indexx)
        self.statusBar.setStyleSheet('background-color: rgb(30, 255, 82);')
        self.statusBar.showMessage('Files deleted', msecs=10000)
        self.statusBar.show()
        qApp.processEvents()
        self.timer.singleShot(10000, self.statusBar.hide)
    def deleteselectedfile(self):
        sys.excepthook = self.show_exception_and_exit
        indexes = self.filelist.selectedIndexes()
        print(indexes)
        dupfile = None
        for index in indexes:
            item = self.modellist.itemFromIndex(index)
            file = self.dict[str(item)]
            print(self.savetofolderpath + '/' + file)
            if file != dupfile:
                os.remove(self.savetofolderpath + '/' + file)
                try:
                    os.remove(self.savetofolderpath + '/' + file.strip('.pdf')+'.bib')
                except:
                    pass
                dupfile = file
        self.fileview(indexx=self.indexx)
        self.statusBar.setStyleSheet('background-color: rgb(30, 255, 82);')
        self.statusBar.showMessage('Files deleted', msecs=10000)
        self.statusBar.show()
        qApp.processEvents()
        self.timer.singleShot(10000, self.statusBar.hide)
        self.Dialog_deletefile.close()
        #try:
         #   print(file)
          #  os.remove(self.savetofolderpath + '/' + file)
           # self.Dialog_deletefile.close()
            #self.fileview(indexx=self.indexx)
        #except:
         #   self.Dialog_deletefile.close()
    def filenametrigger(self, action):
        sys.excepthook = self.show_exception_and_exit
        renamepref = action.text()
        pickle.dump(renamepref, open(docpath + "\syslog2.pkl", "wb"))
        print(action.text())
    def storagetrigger(self):
        sys.excepthook = self.show_exception_and_exit
        self.path = QFileDialog.getExistingDirectory(None, "Open Directory", "C:/",
                                                     QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks)
        pickle.dump(self.path, open(docpath + "\syslog1.pkl", "wb"))
        self.tree.setRootIndex(self.model.index(self.path))
        print(self.path)
    def openexplorer(self):
        sys.excepthook = self.show_exception_and_exit
        try:
            print(self.savetofolderpath)
            path = os.path.realpath(self.savetofolderpath)
            os.startfile(path)
        except:
            p=pickle.load(open(docpath + "\syslog1.pkl", "rb"))
            path = os.path.realpath(p)
            os.startfile(path)
    def savenotes(self):
        sys.excepthook = self.show_exception_and_exit
        print(self.noteswriter.document().toPlainText())
        item = self.modellist.itemFromIndex(self.notesindex)
        file = self.dict[str(item)]
        read=PdfReader(self.savetofolderpath+'/'+file)
        metadatain = PdfDict(Xnotes=self.noteswriter.document().toPlainText())
        read.Info.update(metadatain)
        PdfWriter().write(self.savetofolderpath + '/' + file, read)
    def searchtag(self):
        sys.excepthook = self.show_exception_and_exit
        tags=self.stringtag.document().toPlainText()
        tagset={tag.strip('#') for tag in tags.split() if tag.startswith('#')}
        taglist=list(tagset)
        item = self.modellist.itemFromIndex(self.notesindex)
        file = self.dict[str(item)]
        read = PdfReader(self.savetofolderpath + '/' + file)
        metadatain = PdfDict(Xtag=taglist)
        read.Info.update(metadatain)
        PdfWriter().write(self.savetofolderpath + '/' + file, read)
    def searchquery(self):
        sys.excepthook = self.show_exception_and_exit
        self.statusBar.setStyleSheet('background-color: rgb(67, 211, 255);')
        self.statusBar.showMessage('Searching.......')
        self.statusBar.show()
        qApp.processEvents()
        if self.sstring.text().startswith('#'):
            self.searchtagquery()
        else:
            self.searchqueries()
    def searchtagquery(self):
        sys.excepthook = self.show_exception_and_exit
        pdffiles = []
        matchedfiles = []
        for dirpath, dirnames, filenames in os.walk(self.savetofolderpath):
            for filename in [f for f in filenames if f.endswith(".pdf" or ".PDF")]:
                pdffiles.append(filename)
        print(pdffiles)
        String = self.sstring.text()
        String=String.strip('#')
        for j in range(len(pdffiles)):
            self.statusBar.setStyleSheet('background-color: rgb(67, 211, 255);')
            self.statusBar.showMessage('Searching tag in %s' % pdffiles[j].strip('.pdf'))
            self.statusBar.show()
            qApp.processEvents()
            try:
                read = PdfReader(self.savetofolderpath + '/' + pdffiles[j])
                for i in range(len(read.Info.Xtag)):
                    if String == str(read.Info.Xtag[i].decode()).strip('()'):
                        matchedfiles.append(pdffiles[j])
                    else:
                        pass
            except:
                pass


        if len(matchedfiles)>0:
            #self.indexx = indexx
            self.modellist.clear()
            self.modellist = QtGui.QStandardItemModel()
            self.modellist.setHorizontalHeaderLabels(['Author', 'Title', 'Journal', 'Year', 'Added on'])
            self.filelist.setModel(self.modellist)
            self.filelist.header().resizeSection(0, 180)
            self.filelist.header().resizeSection(1, 340)
            self.filelist.header().resizeSection(2, 120)
            self.filelist.header().resizeSection(3, 50)
            self.filelist.header().resizeSection(4, 50)

            self.dict = {}
            for row in range(len(matchedfiles)):
                # self.dictl=[]
                for column in range(5):
                    Xauthors = ' '
                    try:
                        read = PdfReader(self.savetofolderpath + "/" + matchedfiles[row])
                        for i in range(len(read.Info.Xauthor)):
                            Xauthors = Xauthors + read.Info.Xauthor[i].decode().strip('()') + ';'
                        data = [Xauthors, read.Info.Xtitle.decode().strip('()'),
                                read.Info.Xjournal.decode().strip('()'),
                                read.Info.Xyear.decode().strip('()'), read.Info.Xdate.strip('()')]
                        # print(data)

                        item = QtGui.QStandardItem(data[column])
                        self.modellist.setItem(row, column, item)
                        item.setEditable(False)

                        if column == 0:
                            item.setIcon(QtGui.QIcon('ico/023.png'))
                        else:
                            pass
                    except:
                        # print('read:' + pdffiles[row])
                        if column == 0:
                            item = QtGui.QStandardItem('')
                            item.setEditable(False)
                            self.modellist.setItem(row, column, item)
                            item.setIcon(QtGui.QIcon('ico/042.png'))
                        elif column == 1:
                            item = QtGui.QStandardItem(matchedfiles[row])
                            item.setEditable(False)
                            self.modellist.setItem(row, column, item)
                            # print('read:' + pdffiles[row])
                        else:
                            item = QtGui.QStandardItem('')
                            item.setEditable(False)
                            self.modellist.setItem(row, column, item)
                    try:
                        # self.modellist.setItem(row, column, item)
                        self.dict[str(item)] = matchedfiles[row]
                    # print('read:' + pdffiles[row])
                    # print(self.dict)
                    except:
                        pass

            print(self.dict)
            print(len(self.dict))
            self.filtercombo.setCurrentIndex(0)
            self.filedup = None
            self.filelist.doubleClicked.connect(self.treeitemdoubleClicked)
            self.filelist.clicked.connect(self.treeitemsingleclicked)
            self.statusBar.setStyleSheet('background-color: rgb(30, 255, 82);')
            self.statusBar.showMessage('Tag Search Completed!', msecs=10000)
            self.statusBar.show()
            qApp.processEvents()
            self.timer.singleShot(10000,self.statusBar.hide)
        else:
            self.statusBar.setStyleSheet('background-color: rgb(255, 28, 28);')
            self.statusBar.showMessage('No results found!')
            self.statusBar.show()
            qApp.processEvents()
            self.timer.singleShot(10000, self.statusBar.hide)
    def searchmatch(self,value):
        sys.excepthook = self.show_exception_and_exit
        print(value)
        self.smatchedfiles.append(value)
    def searchqueries(self):
        sys.excepthook = self.show_exception_and_exit
        pdffiles = []
        self.smatchedfiles = []
        string=self.sstring.text()
        for dirpath, dirnames, filenames in os.walk(self.savetofolderpath):
            for filename in [f for f in filenames if f.endswith(".pdf" or ".PDF")]:
                pdffiles.append(filename)
       # print(pdffiles)

        for j in range(len(pdffiles)):
            self.statusBar.setStyleSheet('background-color: rgb(67, 211, 255);')
            self.statusBar.showMessage('Searching in %s' % pdffiles[j].strip('.pdf'))
            self.statusBar.show()
            qApp.processEvents()
            try:
                self.pagethread = searchpagethread(savetofolderpath=self.savetofolderpath, pdffile=pdffiles[j],
                                                   string=string)
                self.pagethread.matchedfile.connect(self.searchmatch)
                self.pagethread.start()
                self.pagethread.wait()
            except:
                pass
            self.pagethread.exit()

        #self.pagethread.quit()
        print('done')
        #print(len(matchedfiles))
        print(self.smatchedfiles)
        matchedfiles=self.smatchedfiles
        if len(matchedfiles)>0:
            print('1')
            #self.indexx = indexx
            self.modellist.clear()
            self.modellist = QtGui.QStandardItemModel()
            self.modellist.setHorizontalHeaderLabels(['Author', 'Title', 'Journal', 'Year', 'Added on'])
            self.filelist.setModel(self.modellist)
            self.filelist.header().resizeSection(0, 180)
            self.filelist.header().resizeSection(1, 340)
            self.filelist.header().resizeSection(2, 120)
            self.filelist.header().resizeSection(3, 50)
            self.filelist.header().resizeSection(4, 50)
            print('2')
            self.dict = {}
            for row in range(len(matchedfiles)):
                # self.dictl=[]
                for column in range(5):
                    print('3')
                    Xauthors = ' '
                    try:
                        read = PdfReader(self.savetofolderpath + "/" + matchedfiles[row])
                        for i in range(len(read.Info.Xauthor)):
                            Xauthors = Xauthors + read.Info.Xauthor[i].decode().strip('()') + ';'
                        data = [Xauthors, read.Info.Xtitle.decode().strip('()'),
                                read.Info.Xjournal.decode().strip('()'),
                                read.Info.Xyear.decode().strip('()'), read.Info.Xdate.strip('()')]
                        # print(data)

                        item = QtGui.QStandardItem(data[column])
                        self.modellist.setItem(row, column, item)
                        item.setEditable(False)

                        if column == 0:
                            item.setIcon(QtGui.QIcon('ico/023.png'))
                        else:
                            pass
                    except:
                        # print('read:' + pdffiles[row])
                        if column == 0:
                            item = QtGui.QStandardItem('')
                            item.setEditable(False)
                            self.modellist.setItem(row, column, item)
                            item.setIcon(QtGui.QIcon('ico/042.png'))
                        elif column == 1:
                            item = QtGui.QStandardItem(matchedfiles[row])
                            item.setEditable(False)
                            self.modellist.setItem(row, column, item)
                            # print('read:' + pdffiles[row])
                        else:
                            item = QtGui.QStandardItem('')
                            item.setEditable(False)
                            self.modellist.setItem(row, column, item)
                    try:
                        # self.modellist.setItem(row, column, item)
                        self.dict[str(item)] = matchedfiles[row]
                    # print('read:' + pdffiles[row])
                    # print(self.dict)
                    except:
                        pass

            print(self.dict)
            print(len(self.dict))
            self.filtercombo.setCurrentIndex(0)
            self.filedup = None
            self.filelist.doubleClicked.connect(self.treeitemdoubleClicked)
            self.filelist.clicked.connect(self.treeitemsingleclicked)
            self.statusBar.setStyleSheet('background-color: rgb(30, 255, 82);')
            self.statusBar.showMessage('Search Completed!', msecs=10000)
            self.statusBar.show()
            qApp.processEvents()
            self.timer.singleShot(10000,self.statusBar.hide)
        else:
            self.statusBar.setStyleSheet('background-color: rgb(255, 28, 28);')
            self.statusBar.showMessage('No results found!')
            self.statusBar.show()
            qApp.processEvents()

            self.timer.singleShot(10000, self.statusBar.hide)
    def backuptrigger(self):
        sys.excepthook = self.show_exception_and_exit
        backupDialog=QDialog()
        backupDialog.setObjectName("backupDialog")
        backupDialog.resize(435, 80)
        backupDialog.setMinimumSize(QtCore.QSize(435, 80))
        backupDialog.setMaximumSize(QtCore.QSize(435, 80))
        backupDialog.setStyleSheet("background-color: rgb(194, 195, 255);")
        self.horizontalLayoutWidget = QtWidgets.QWidget(backupDialog)
        self.horizontalLayoutWidget.setGeometry(QtCore.QRect(0, 0, 421, 80))
        self.horizontalLayoutWidget.setObjectName("horizontalLayoutWidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.horizontalLayoutWidget)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label = QtWidgets.QLabel(self.horizontalLayoutWidget)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)
        self.backupfolder = QtWidgets.QLineEdit(self.horizontalLayoutWidget)
        self.backupfolder.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.backupfolder.setObjectName("backupfolder")
        self.horizontalLayout.addWidget(self.backupfolder)
        self.selectbackup = QtWidgets.QToolButton(self.horizontalLayoutWidget)
        self.selectbackup.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.selectbackup.setObjectName("selectbackup")
        self.horizontalLayout.addWidget(self.selectbackup)
        self.backup = QtWidgets.QPushButton(self.horizontalLayoutWidget)
        self.backup.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.backup.setObjectName("backup")
        self.horizontalLayout.addWidget(self.backup)
        self.bakclose = QtWidgets.QPushButton(self.horizontalLayoutWidget)
        self.bakclose.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.bakclose.setObjectName("bakclose")
        self.horizontalLayout.addWidget(self.bakclose)
        self.bakclose.clicked.connect(backupDialog.close)
        self.retranslateUi_backup(backupDialog)
        QtCore.QMetaObject.connectSlotsByName(backupDialog)
        self.selectbackup.clicked.connect(self.sbackupfolder)
        self.backup.clicked.connect(self.startbackup)
        backupDialog.show()
        backupDialog.exec_()
    def sbackupfolder(self):
        sys.excepthook = self.show_exception_and_exit
        self.bpath = QFileDialog.getExistingDirectory(None, "Open Directory", "C:/",
                                                     QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks)
        self.backupfolder.setText(self.bpath)
    def startbackup(self):
        sys.excepthook = self.show_exception_and_exit
        self.statusBar.setStyleSheet('background-color: rgb(67, 211, 255);')
        self.statusBar.showMessage('Preparing for backup. Please wait...')
        self.statusBar.show()
        qApp.processEvents()
        self.bakclose.setDisabled(True)
        self.backup.setDisabled(True)
        zipf = zipfile.ZipFile(self.bpath+'/SciX_backup.zip', 'w', zipfile.ZIP_DEFLATED)
        for root, dirs, files in os.walk(pickle.load(open(docpath + "\syslog1.pkl", "rb"))):
            for file in files:
                self.statusBar.setStyleSheet('background-color: rgb(67, 211, 255);')
                self.statusBar.showMessage('Zipping up %s' % file)
                self.statusBar.show()
                qApp.processEvents()
                zipf.write(os.path.join(root, file))
        self.statusBar.setStyleSheet('background-color: rgb(30, 255, 82);')
        self.statusBar.showMessage('Backup completed!', msecs=10000)
        self.statusBar.show()
        qApp.processEvents()
        self.timer.singleShot(10000, self.statusBar.hide)
        self.bakclose.setEnabled(True)
    def citecount(self):
        sys.excepthook = self.show_exception_and_exit
        doi=self.doiinfo.toPlainText()
        self.statusBar.setStyleSheet('background-color: rgb(30, 255, 82);')
        self.statusBar.showMessage('Times Cited: '+str(counts.citation_count(doi=doi)), msecs=10000)
        self.statusBar.show()
        qApp.processEvents()
        self.timer.singleShot(10000, self.statusBar.hide)
    def retranslateUi_backup(self, backupDialog):
        sys.excepthook = self.show_exception_and_exit
        _translate = QtCore.QCoreApplication.translate
        backupDialog.setWindowTitle(_translate("backupDialog", "Dialog"))
        self.label.setText(_translate("backupDialog", " Output Folder"))
        self.selectbackup.setText(_translate("backupDialog", "..."))
        self.backup.setText(_translate("backupDialog", "Backup"))
        self.bakclose.setText(_translate("backupDialog", "Close"))
    def retranslateUi_deletefile(self, Dialog_deletefile):
        sys.excepthook = self.show_exception_and_exit
        _translate = QtCore.QCoreApplication.translate
        Dialog_deletefile.setWindowTitle(_translate("Dialog_delete", "Warning"))
        try:
            self.label.setText(
                _translate("Dialog_delete", "Are you sure to delete ' %s...' ?" % file[:32]))
        except:
            self.label.setText(
                _translate("Dialog_delete", "Make sure to select the file for deleting" ))
        self.deleteb.setText(_translate("Dialog_delete", "Delete"))
        self.cancelb.setText(_translate("Dialog_delete", "Cancel"))
    def retranslateUi_delete(self, Dialog_delete):
        sys.excepthook = self.show_exception_and_exit
        _translate = QtCore.QCoreApplication.translate
        Dialog_delete.setWindowTitle(_translate("Dialog_delete", "Warning"))
        self.label.setText(
            _translate("Dialog_delete", "Deleting a folder will delete all the files. Wish to continue?"))
        self.deleteb.setText(_translate("Dialog_delete", "Delete"))
        self.cancelb.setText(_translate("Dialog_delete", "Cancel"))
    def retranslateUi_add(self, AddDialog):
        sys.excepthook = self.show_exception_and_exit
        _translate = QtCore.QCoreApplication.translate
        AddDialog.setWindowTitle(_translate("AddDialog", "Add from local"))
        self.label.setText(_translate("AddDialog", "File directory"))
        self.openfiledialog.setToolTip(_translate("AddDialog", "File dialog"))
        self.openfiledialog.setText(_translate("AddDialog", "..."))
        self.import_2.setToolTip(_translate("AddDialog", "Import the selected file"))
        self.import_2.setText(_translate("AddDialog", "Import"))
    def retranslateUi_man(self, manualentry):
        sys.excepthook = self.show_exception_and_exit
        _translate = QtCore.QCoreApplication.translate
        manualentry.setWindowTitle(_translate("manualentry", "Manual Entry"))
        self.label_11.setText(_translate("manualentry", "     Enter DOI"))
        self.onlydoi.setToolTip(_translate("manualentry", "Enter DOI or Type entries manually"))
        self.onlydoi.setPlaceholderText(_translate("manualentry", "Enter DOI or Type Entries below"))
        self.label_12.setText(_translate("manualentry", "                            OR"))
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
        sys.excepthook = self.show_exception_and_exit
        _translate = QtCore.QCoreApplication.translate
        Dialog_d.setWindowTitle(_translate("Dialog_d", "Enter DOI"))
        self.label.setText(_translate("Dialog_d", "Enter DOI"))
        self.pastedoi.setPlaceholderText(_translate("Dialog_d", "Paste the DOI of the Article"))
        self.getdoi.setToolTip(_translate("Dialog_d", "Click to download and import"))
        self.getdoi.setText(_translate("Dialog_d", "Download"))
        self.typemanual.setToolTip(_translate("Dialog_d", "Enter all the details manually"))
        self.typemanual.setText(_translate("Dialog_d", "Type Manually"))
    def retranslateUi_r(self, Dialog):
        sys.excepthook = self.show_exception_and_exit
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Rename folder"))
        self.label.setText(_translate("Dialog", "Enter folder name"))
        self.renamebutton.setText(_translate("Dialog", "Rename"))
    def retranslateUi_c(self, Dialog):
        sys.excepthook = self.show_exception_and_exit
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Create folder"))
        self.label.setText(_translate("Dialog", "Enter folder name"))
        self.newfoldercreate.setText(_translate("Dialog", "Create"))
        self.radiobutton_c.setToolTip(_translate("Dialog", "Creates folder in your main directory"))
        self.radiobutton_c.setText(_translate("Dialog", "Create in Main"))
    def retranslateUi(self, Dialog):
        sys.excepthook = self.show_exception_and_exit
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Download status"))
        self.doned.setText(_translate("Dialog", "Hide"))
        self.canceld.setText(_translate("Dialog", "Cancel"))
        self.downloadstatus.setText(_translate("Dialog", "Progress"))
    def retranslateUi_style(self, Dialog_style):
        sys.excepthook = self.show_exception_and_exit
        _translate = QtCore.QCoreApplication.translate
        Dialog_style.setWindowTitle(_translate("Dialog_style", "Select Style"))
        self.stylecombo.setToolTip(_translate("Dialog_style", "Select the style"))
        self.label.setText(_translate("Dialog_style", "Formatting style"))
        self.styleapply.setToolTip(_translate("Dialog_style", "Set the selected style"))
        self.styleapply.setText(_translate("Dialog_style", "Apply"))
        self.stylecancel.setToolTip(_translate("Dialog_style", "Cancel"))
        self.stylecancel.setText(_translate("Dialog_style", "Cancel"))
    def openterms(self):
        sys.excepthook = self.show_exception_and_exit
        os.startfile("Terms and Conditions.txt")
    def openuserguide(self):
        sys.excepthook = self.show_exception_and_exit
        webbrowser.open_new_tab("https://scix.in/tutorial")
    def openprivacy(self):
        sys.excepthook = self.show_exception_and_exit
        webbrowser.open_new_tab("https://scix.in/terms")
    def opendonate(self):
        sys.excepthook = self.show_exception_and_exit
        webbrowser.open_new_tab("https://scix.in/donate")
    def openfeedback(self):
        sys.excepthook = self.show_exception_and_exit
        webbrowser.open_new_tab("https://scix.in/contact")
    def openabout(self):
        sys.excepthook = self.show_exception_and_exit
        webbrowser.open_new_tab("https://scix.in/about")
    def refreshmsg(self):
        sys.excepthook = self.show_exception_and_exit
       # QMessageBox.Apply()
        msgr=QMessageBox()
        msgr.setText("Copy all your non-SciX pdfs into the current SciX folder using file explorer. Click 'Ok' to convert into SciX pdfs. (Note: If any pdf is not converted, enter the doi of the pdf and click update in 'Details' tab.")
        msgr.setIcon(QMessageBox.Information)
        msgr.setWindowTitle('Refresh folder')
        msgr.setStandardButtons(QMessageBox.Ok|QMessageBox.Cancel)
        msgr.buttonClicked.connect(self.refreshfiles)
        msgr.exec_()
    def refreshfiles(self):
        #sys.excepthook = self.show_exception_and_exit
        self.refthread=refreshthread(savepath=savetofolderpath)
        self.refthread.currentfile.connect(self.refthreadnoti)
        self.refthread.start()
    def refthreadnoti(self,value):
        #sys.excepthook = self.show_exception_and_exit
        if value=='Done':
            try:
                self.fileview(self.indexx)
            except:
                pass
        else:
            if value[0] == 'U':
                self.statusBar.setStyleSheet('background-color: rgb(67, 211, 255);')
            else:
                self.statusBar.setStyleSheet('background-color: rgb(255, 28, 28);')
            self.statusBar.showMessage(value)
            self.statusBar.show()
            qApp.processEvents()
            self.timer.singleShot(10000, self.statusBar.hide)
    def upbydoi(self):
        #sys.excepthook = self.show_exception_and_exit
        #print(self.doiinfo.toPlainText())
        if self.doiinfo.toPlainText()!='':
            print('ent')
            print(file)
            print(savetofolderpath)
            self.updoithread=upthread(file=file,doi=self.doiinfo.toPlainText(),savepath=savetofolderpath)
            self.updoithread.upstatus.connect(self.updoinoti)
            self.updoithread.start()
    def updoinoti(self,value):
        #sys.excepthook = self.show_exception_and_exit
        if value == 'Updated':
            self.fileview(indexx=self.indexx)
        self.statusBar.setStyleSheet('background-color: rgb(67, 211, 255);')
        self.statusBar.showMessage(value)
        self.statusBar.show()
        qApp.processEvents()
        self.timer.singleShot(20000, self.statusBar.hide)
    def notiupdate(self,msg):
        #sys.excepthook = self.show_exception_and_exit
        msg=msg.strip("''")
        if msg=='Ready. Connected to Internet':
            self.statusBar.setStyleSheet('background-color: rgb(30, 255, 82);')
        elif msg=='Not Connected to Internet':
            self.statusBar.setStyleSheet('background-color: rgb(255, 28, 28);')
        else:
            self.statusBar.setStyleSheet('background-color: rgb(255, 125, 11);')
        self.statusBar.showMessage(msg)
        self.statusBar.show()
        qApp.processEvents()
        self.timer.singleShot(10000, self.statusBar.hide)
    def msgbox(self):
        sys.excepthook = self.show_exception_and_exit
        global msgb
        msgb = QMessageBox(QMessageBox.Warning, "Warning",
                           "Select a folder to download",
                           QMessageBox.Ok)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("ico/027.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        msgb.setWindowIcon(icon)
        msgb.exec_()
    def errorstatus(self,error):

        sys.excepthook = self.show_exception_and_exit
        self.statusBar.setStyleSheet('background-color: rgb(255, 28, 28);')
        self.statusBar.showMessage('ERROR OCCURED')
        self.statusBar.show()
        qApp.processEvents()
       # QTimer.stop()
        self.timer.singleShot(10000, self.statusBar.hide)
    def CloseEvent(self):
        sys.excepthook = self.show_exception_and_exit
        print('close')
       # os.remove('download.py')
        os.remove('service.json')
    def show_exception_and_exit(self,exc_type, exc_value, tb):
        import traceback
        # traceback.print_exception(exc_type, exc_value,tb))
        a = traceback.format_tb(tb)
        print(type(a))
        print('hhhhhh')
        print(''.join(a))

        f = open(docpath + '\ERROR LOG.txt', 'a')
        f.write(str(exc_value))
        f.write("\n")
        f.write("Details:")
        f.write(''.join(a))
        f.write("\n")
        f.write("\n")
        f.close()
        self.errorstatus(str(exc_value))
        # window.errorstatusclose()
        #self.errorstatus(str(exc_value))

class searchpagethread(QThread):
    matchedfile=pyqtSignal(str)
    def __init__(self,savetofolderpath,pdffile,string):
        super(searchpagethread, self).__init__()
        print('matchthread')
        self.savetofolderpath=savetofolderpath
        self.pdffile=pdffile
        self.sstring=string
    def run(self):
        try:
            print(self.pdffile)
            object = PyPDF2.PdfFileReader(self.savetofolderpath + '/' + self.pdffile)
            NumPages = object.getNumPages()
            String = self.sstring
            flag = False
            for i in range(0, NumPages):
                if flag == False:
                    PageObj = object.getPage(i)
                    print("this is page " + str(i))
                    Text = PageObj.extractText()
                    #print(Text)
                    ResSearch = re.search(String, Text)
                    #print(ResSearch)
                    if ResSearch is not None:
                       # matchedfiles.append(pdffiles[j])
                       # self.matchedfile.emit('sssssss')
                        self.matchedfile.emit(self.pdffile)
                        flag = True
                    else:
                        pass
                else:
                    pass
        except:
            pass
class upthread(QThread):
    upstatus = pyqtSignal(str)

    def __init__(self,file,doi,savepath):
        super(upthread, self).__init__()
        print('update')
        self.file=file
        self.doi=doi
        self.savetofolderpath=savepath
    def show_exception_and_exits(self,exc_type, exc_value, tb):
        import traceback
        # traceback.print_exception(exc_type, exc_value,tb))
        a = traceback.format_tb(tb)
        print(''.join(a))

        f = open(docpath + '\ERROR LOG.txt', 'a')
        f.write(str(exc_value))
        f.write("\n")
        f.write("Details:")
        f.write(''.join(a))
        f.write("\n")
        f.write("\n")
        f.close()
    def run(self):
        sys.excepthook = self.show_exception_and_exits
        self.upstatus.emit('Updating:'+self.file)
        upthread = downloadthread(path=self.savetofolderpath + '/' + self.file, doi=self.doi,
                                  savepath=self.savetofolderpath)
        upthread.start()
        upthread.wait()
        self.upstatus.emit('Updated')
class refreshthread(QThread):
    currentfile=pyqtSignal(str)
    def __init__(self, savepath):
        super(refreshthread, self).__init__()
        self.savepath=savepath
    def run(self):
        sys.excepthook = self.show_exception_and_exits
        pdffiles = []
        filenames = [f for f in os.listdir(self.savepath) if os.path.isfile(os.path.join(self.savepath, f))]
        for filename in [f for f in filenames if f.endswith(".pdf" or ".PDF")]:
            pdffiles.append(filename)

        for row in range(len(pdffiles)):
            flagtitle=True
            try:
                try:
                    read = PdfReader(self.savepath + "/" + pdffiles[row])
                    print(pdffiles[row])
                except PdfParseError:
                    with pikepdf.open(self.savepath + "/" + pdffiles[row],allow_overwriting_input=True) as pdf:
                        pdf.save(self.savepath + "/" + pdffiles[row])
                    read = PdfReader(self.savepath + "/" + pdffiles[row])
                    print(pdffiles[row])

                if read.Info.Xdoi == None and read.Info.doi != None:
                    self.currentfile.emit('Updating:' + pdffiles[row])
                    self.reupdate = downloadthread(path=savetofolderpath + "/" + pdffiles[row],
                                                   doi=read.Info.doi.strip('()'),
                                                   savepath=savetofolderpath)
                    self.reupdate.start()
                    self.reupdate.wait()
                    self.currentfile.emit('Updated:' + pdffiles[row])
                    time.sleep(1)
                else:
                    try:
                        Title=read.Info.Title
                        if Title!=None:
                            Title=Title.strip('()')
                            if Title[:4]=='doi:' and len(Title)>8:
                                self.currentfile.emit('Updating:' + pdffiles[row])
                                self.reupdate = downloadthread(path=savetofolderpath + "/" + pdffiles[row],
                                                               doi=Title[4:],
                                                               savepath=savetofolderpath)
                                self.reupdate.start()
                                self.reupdate.wait()
                                self.currentfile.emit('Updated:' + pdffiles[row])
                                time.sleep(1)
                            elif len(Title)>6:
                                title_temp = Title
                                print(title_temp)
                                cr = Crossref()
                                x = cr.works(query=title_temp)
                                doi = x['message']['items'][0]['DOI']
                                my_etiquette = Etiquette('SciX', '1.0', 'www.scix.in', 'service@scix.in')
                                works = Works(my_etiquette)
                                meta = works.doi(doi)
                                title = meta['title']
                                title = title[0]
                                title = title.replace('/', '')
                                print(title)
                                if title_temp == title:
                                    print('st')
                                    self.currentfile.emit('Updating:' + pdffiles[row])
                                    self.reupdate = downloadthread(path=savetofolderpath + "/" + pdffiles[row],
                                                                   doi=doi,
                                                                   savepath=savetofolderpath)
                                    self.reupdate.start()
                                    self.reupdate.wait()
                                    self.currentfile.emit('Updated:' + pdffiles[row])
                                    time.sleep(1)
                                else:
                                    print('nt')
                                    match = SequenceMatcher(None, title_temp, title)
                                    matchper = match.ratio() * 100
                                    if matchper >= 90:
                                        print('matched')
                                        self.currentfile.emit('Updating:' + pdffiles[row])
                                        self.reupdate = downloadthread(path=savetofolderpath + "/" + pdffiles[row],
                                                                       doi=doi,
                                                                       savepath=savetofolderpath)
                                        self.reupdate.start()
                                        self.reupdate.wait()
                                        self.currentfile.emit('Updated:' + pdffiles[row])
                                        time.sleep(1)
                                    else:
                                        flagtitle=False
                                        self.currentfile.emit('Could not Update:' + pdffiles[row])
                                        time.sleep(1)
                            else:
                                flagtitle=False
                        else:
                            flagtitle=False
                    except:
                        flagtitle=False


                if flagtitle==False:
                    title_temp = get_title_from_file(self.savepath + "/" + pdffiles[row])
                    print(title_temp)
                    cr = Crossref()
                    x = cr.works(query=title_temp)
                    doi = x['message']['items'][0]['DOI']
                    my_etiquette = Etiquette('SciX', '1.0', 'www.scix.in', 'service@scix.in')
                    works = Works(my_etiquette)
                    meta = works.doi(doi)
                    title = meta['title']
                    title = title[0]
                    title = title.replace('/', '')
                    print(title)
                    if title_temp == title:
                        print('st')
                        self.currentfile.emit('Updating:' + pdffiles[row])
                        self.reupdate = downloadthread(path=savetofolderpath + "/" + pdffiles[row],
                                                       doi=doi,
                                                       savepath=savetofolderpath)
                        self.reupdate.start()
                        self.reupdate.wait()
                        self.currentfile.emit('Updated:' + pdffiles[row])
                        time.sleep(1)
                    else:
                        print('nt')
                        match = SequenceMatcher(None, title_temp, title)
                        matchper = match.ratio() * 100
                        if matchper >= 90:
                            print('matched')
                            self.currentfile.emit('Updating:' + pdffiles[row])
                            self.reupdate = downloadthread(path=savetofolderpath + "/" + pdffiles[row],
                                                           doi=doi,
                                                           savepath=savetofolderpath)
                            self.reupdate.start()
                            self.reupdate.wait()
                            self.currentfile.emit('Updated:' + pdffiles[row])
                            time.sleep(1)
                        else:
                            self.currentfile.emit('Could not Update:' + pdffiles[row])
                            time.sleep(1)
            except:
                pass

        self.currentfile.emit('Done')
    def show_exception_and_exits(self,exc_type, exc_value, tb):
        import traceback
        # traceback.print_exception(exc_type, exc_value,tb))
        a = traceback.format_tb(tb)
        print(''.join(a))

        f = open(docpath + '\ERROR LOG.txt', 'a')
        f.write(str(exc_value))
        f.write("\n")
        f.write("Details:")
        f.write(''.join(a))
        f.write("\n")
        f.write("\n")
        f.close()
class downloadthread(QThread):
    countChanged = pyqtSignal(int)
    statusChanged = pyqtSignal(str)

    def __init__(self,path,doi,savepath):
        super(downloadthread, self).__init__()
        print('dthread')
        print(path)
        print(os.path.isfile(path))
        self.path=path
        self.doi=doi
        self.savepath=savepath
    def run(self):
        sys.excepthook = self.show_exception_and_exits
        if self.doi!='' and self.doi!=None:
            print(os.path.isfile(self.path))
            doi=self.doi
            filepath=self.path
            savetofolderpath=self.savepath
            my_etiquette = Etiquette('SciX', '1.0', 'www.scix.in', 'service@scix.in')
            works = Works(my_etiquette)
            meta = works.doi(doi)
            count = 70
            self.countChanged.emit(count)
            self.statusChanged.emit('Fetching data...')
            print('70')
            print(os.path.isfile(filepath))
            try:
                title = meta['title']
                print(title)
                title = title[0]
                title = title.replace('/', '')
            except:
                title = None
            try:
                authors = meta['author']
                print(authors)
                authordict = []
                for i in range(len(authors)):
                    authordict.append(authors[i])
                author = []
                for i in range(len(authordict)):
                    author.append(authordict[i]['given'] + authordict[i]['family'])
                    author[i] = author[i].replace('/', '')
            except:
                author = None
            count = 75
            self.countChanged.emit(count)
            print('75')
            print(os.path.isfile(filepath))
            try:
                journal = meta['container-title']
                journal = journal[0]
                journal = journal.replace('/', '')
            except:
                journal = None
            try:
                yr = meta['created']
                yrs = yr['date-time']
                year = yrs[:4]
                year = year.replace('/', '')
            except:
                year = None
            try:
                page = meta['page']
                page = page.replace('/', '')
            except:
                page = None
            try:
                issue = meta['issue']
                issue = issue.replace('/', '')
            except:
                issue = None
            try:
                volume = meta['volume']
                volume = volume.replace('/', '')
            except:
                volume = None
            try:
                issn = meta['ISSN']
                issn = issn[0]
                issn = issn.replace('/', '')
            except:
                issn = None
            try:
                url = meta['URL']

            except:
                url = None
            count = 80
            self.countChanged.emit(count)
            print('80')
            print(os.path.isfile(filepath))
            try:
                filerename = pickle.load(open(docpath + "\syslog2.pkl", "rb"))
            except:
                filerename = 'Author-Title-Journal-Year'
            print(filerename)
            self.statusChanged.emit('Checking your rename preference...')
            print(os.path.isfile(filepath))
            read = PdfReader(filepath)

            if author is None:
                author = ['XXX', 'COULD NOT FETCH AUTHOR DETAILS', 'ADD MANUALLY']
            metadatain = PdfDict(Xauthor=author, Xdoi=doi, Xtitle=title, Xjournal=journal, Xyear=year,
                                 Xpage=page, Xissue=issue, Xvolume=volume, Xissn=issn, Xurl=url,
                                 Xdate=date.today())
            print('me')
            read.Info.update(metadatain)
            print(journal)
            print(author)
            print(year)
            print(title)

            if title is None:
                title = ''
            else:
                if len(title) > 100:
                    title = textwrap.shorten(title, width=100, placeholder='..')
            if journal is None:
                journal = ''
            if year is None:
                year = ''
            count = 85
            self.countChanged.emit(count)
            self.statusChanged.emit('Updating pdf...')
            if filerename == 'Author-Title-Journal-Year':
                count = 90
                self.countChanged.emit(count)
                filename = author[0] + '--' + title + '--' + journal + '--' + year + '.pdf'
                filename = ''.join(c for c in filename if c not in "/\:*?<>|")
                print(savetofolderpath + '/' + filename)
                PdfWriter().write(savetofolderpath + '/' + filename, read)
                flag = True
            if filerename == 'Title-Author-Journal-Year':
                count = 90
                self.countChanged.emit(count)
                filename = title + '--' + author[0] + '--' + journal + '--' + year + '.pdf'
                filename = ''.join(c for c in filename if c not in "/\:*?<>|")
                print(savetofolderpath + '/' + filename)
                PdfWriter().write(savetofolderpath + '/' + filename, read)
                flag = True
            if filerename == 'Journal-Author-Title-Year':
                count = 90
                self.countChanged.emit(count)
                filename = journal + '--' + author[0] + '--' + title + '--' + year + '.pdf'
                filename = ''.join(c for c in filename if c not in "/\:*?<>|")
                print(savetofolderpath + '/' + filename)
                PdfWriter().write(savetofolderpath + '/' + filename, read)
                flag = True
            if filerename == 'Year-Author-Title-Journal':
                count = 90
                self.countChanged.emit(count)
                filename = year + '--' + author[0] + '--' + title + '--' + journal + '.pdf'
                filename = ''.join(c for c in filename if c not in "/\:*?<>|")
                print(savetofolderpath + '/' + filename)
                PdfWriter().write(savetofolderpath + '/' + filename, read)
                flag = True
            if filerename == 'Year-Journal-Author-Title':
                count = 90
                self.countChanged.emit(count)
                filename = year + '--' + journal + '--' + author[0] + '--' + title + '.pdf'
                filename = ''.join(c for c in filename if c not in "/\:*?<>|")
                print(savetofolderpath + '/' + filename)
                PdfWriter().write(savetofolderpath + '/' + filename, read)
                flag = True
            if filepath !=savetofolderpath + '/' + filename:
                os.remove(filepath)
            count = 95
            self.countChanged.emit(count)
            self.statusChanged.emit('Fetching bib file...')
            try:
                BibEntries = BibEntry()
                out = open(savetofolderpath + '/' + filename.strip('.pdf') + '.bib', 'w',
                           encoding='utf-8')
                out.write(BibEntries.doiToBib(doi).ToString())
                out.close()
            except:
                self.statusChanged.emit('Failed to get bib file')
            self.statusChanged.emit('Import completed. ')
            count = 100
            self.countChanged.emit(count)
        else:
            self.countChanged.emit(99)
            self.statusChanged.emit('Downloaded.Failed to update')

    def show_exception_and_exits(self,exc_type, exc_value, tb):
        import traceback
        # traceback.print_exception(exc_type, exc_value,tb))
        a = traceback.format_tb(tb)
        print(''.join(a))

        f = open(docpath + '\ERROR LOG.txt', 'a')
        f.write(str(exc_value))
        f.write("\n")
        f.write("Details:")
        f.write(''.join(a))
        f.write("\n")
        f.write("\n")
        f.close()
        self.countChanged.emit(0)
        self.statusChanged.emit('Failed to update')
class BibEntry:
    """A bibtex entry object for an article"""
    type = "article"
    number = ""
    pages = ""
    month = ""
    note = ""
    key = ""

    def __init__(self, URL="", doi="", author="", title="", journal="", year="", volume=""):
        self.author = author
        print(self.author)
        self.doi = doi
        print(self.doi)
        self.title = title
        self.journal = journal
        self.year = year
        self.reference = author + year
        self.volume = volume
        self.URL = URL

    def ToString(self):
        # reload(sys)
        # sys.setdefaultencoding("utf-8")
        output = "@Article{" + self.doi + ",\n"
        output += "author = {" + self.author + "},\n"
        output += "title = {" + self.title + "},\n"
        output += "journal = {" + self.journal + "},\n"
        output += "year = " + self.year + ",\n"

        if self.number != "":
            output += "number = " + self.number + ",\n"

        if self.pages != "":
            output += 'pages = "' + self.pages + '+",\n'

        if self.month != "":
            output += "month = " + self.month + ",\n"

        if self.note != "":
            output += "note = {" + self.note + "},\n"
        if self.volume != "":
            output += "volume = " + self.volume + ",\n"

        if self.doi != "":
            output += "doi = {" + self.doi + "},\n"

        if self.URL != "":
            output += "URL = {" + self.URL + "\n}}"

        return output

    def doiToJson(self, doi):
        """Returns metadata associated with given DOI string in JSON format

        :param doi: a string of the DOI
        :returns: -- JSON metadata for reference
        """
        url = 'http://data.crossref.org/' + doi
        headers = {'Accept': 'application/citeproc+json'}
        r = requests.get(url, headers=headers)
        meta = json.loads(r.content)
        return meta

    def doiToBib(self, doi):
        """Turns metadata from given DOI string into a bibtex object

        :param doi: a string of the DOI
        :returns: -- bibtex object of metadata
        """
        print(doi)
        meta = self.doiToJson(doi)
        data = meta.items()
        print(data)
        journal = self.getField("container-title", data)
        author = self.getAuthor(data)
        year, month = self.getYearMonth(data)
        title = self.getField("title", data)
        volume = self.getField("volume", data)
        URL = 'http://dx.doi.org/' + doi
        print(URL)
        entry = BibEntry(URL=URL, doi=doi, author=author, year=year, journal=journal, title=title, volume=volume)
        entry.number = self.getField("issue", data)
        entry.pages = self.getField("page", data)
        entry.month = month
        return entry

    def getField(self, field, data):
        """Returns the value of the given field name from the given data

        :param field: the name of the field needed
        :param data: the JSON.items() object containing the field
        :returns: -- the value of the field if found, or "" otherwise
        """
        output = ""
        for key, value in data:
            if key == field:
                output = value
        return output

    def getAuthor(self, data):
        """Returns the authors in the correct format for bibtex from the data.

        :param data: the JSON.items() object containing the author data
        :returns: -- a string of the authors in suitable format for bibtex entry
        """
        output = ""
        for key, value in data:
            if key == "author":
                authors = value
                # Parse each author in turn
                for aval in authors:
                    firstname = aval['given'].strip('')
                    lastname = aval['family'].strip('')
                    output += "%s, %s and " % (lastname, firstname)
                output = output.strip(" and ")
        return output

    def getYearMonth(self, data):
        """Returns the year and month from given json data in format for bibtex entry

        :param data: the JSON.items() object containing the data
        :returns: a value pair (year, month)
        """
        year = ""
        month = ""
        verbose_date = self.getField("published-print", data)

        if verbose_date == "":
            verbose_date = self.getField("published-online", data)

        if verbose_date == "":
            verbose_date = self.getField("issued", data)

        if verbose_date != "":
            date_parts = verbose_date.get('date-parts')
            if (len(date_parts) > 0):
                if (len(date_parts[0]) > 1):
                    year = "%i" % date_parts[0][0]
                    month = "%i" % date_parts[0][1]
                else:
                    year = "%i" % date_parts[0][0]
        return year, month
class registry():
    def __init__(self):
        print('reg')

class notithread(QThread):
    msg= pyqtSignal(str)
    def show_exception_and_exits(self,exc_type, exc_value, tb):
        import traceback
        # traceback.print_exception(exc_type, exc_value,tb))
        a = traceback.format_tb(tb)
        print(''.join(a))

        f = open(docpath + '\ERROR LOG.txt', 'a')
        f.write(str(exc_value))
        f.write("\n")
        f.write("Details:")
        f.write(''.join(a))
        f.write("\n")
        f.write("\n")
        f.close()
    def run(self):
        sys.excepthook = self.show_exception_and_exits
        pyAesCrypt.decryptFile(r"service.dll", r"service.json", 'xservicex', 64 * 1024)
        print('thread start')
        net = False
        try:
            requests.get('https://www.google.com/').status_code
            count='Ready. Connected to Internet'
            self.msg.emit(count)
            net = True
        except:
            count='Not Connected to Internet'
            self.msg.emit(count)
        if net == True:
            try:
                pickle.load(open(docpath + "\start.pkl", "rb"))
            except:
                self.firstregister()
            try:
                dateinfile=pickle.load(open(docpath+"\currentreg.pkl","rb"))
            except:
                pickle.dump(str(date.today().day), open(docpath + "\currentreg.pkl", "wb"))
                self.currentregister()
                dateinfile = pickle.load(open(docpath + "\currentreg.pkl", "rb"))
            if dateinfile!=str(date.today().day):
                self.currentregister()
            while True:
                self.getnoti()
                time.sleep(120)
    def getnoti(self):
        sys.excepthook = self.show_exception_and_exits
        try:
            try:
                print(self.msgs)
            except:
                self.msgs = self.notification()
            for i in range(len(self.msgs)):
                if i==0:
                    pickle.dump(str(self.msgs[0]).strip('[]'), open(docpath + "\link.pkl", "wb"))
                else:
                    self.msg.emit(str(self.msgs[i]).strip('[]'))
                    time.sleep(15)

        except:
            pass
    def currentregister(self):
        sys.excepthook = self.show_exception_and_exits
        try:
            os = ''
            version = ''
            release = ''
            ip = ''
            country = ''
            region = ''
            city = ''
            todate = str(date.today().day)
            toyear = str(date.today().year)
            tomonth = str(date.today().month)
            try:
                os = platform.system()
                version = platform.version()
                release = platform.release()
            except:
                pass
            url = "https://freegeoip.app/json/"
            headers = {
                'accept': "application/json",
                'content-type': "application/json"
            }
            response = requests.request("GET", url, headers=headers)
            res = json.loads(response.text)
            ip = res['ip']
            country = res['country_name']
            region = res['region_name']
            city = res['city']
            ver = '1.0'
            values = (
                (todate, tomonth, toyear, ip, city, ver, country, region, os, version, release),
            )

            self.sendtobase('15o39VCF486957LN32dIhOhBFcKtQC_EyXiI-4CgN2hw', 'Sheet1', values)
            pickle.dump(todate, open(docpath + "\currentreg.pkl", "wb"))
        except:
            pass
    def firstregister(self):
        sys.excepthook = self.show_exception_and_exits
        os=''
        version=''
        release=''
        processor=''
        ip=''
        country=''
        region=''
        city=''
        try:
            os=platform.system()
            version=platform.version()
            release=platform.release()
            processor=platform.processor()
        except:
            pass
        url = "https://freegeoip.app/json/"
        headers = {
            'accept': "application/json",
            'content-type': "application/json"
        }
        response = requests.request("GET", url, headers=headers)
        res=json.loads(response.text)
        ip=res['ip']
        country=res['country_name']
        region=res['region_name']
        city=res['city']
        ver='1.0'
        values=(
            (ip,city,ver,country,region,os,version,release,processor),
        )

        self.sendtobase('1J1v0a1yJqnX3lZb7vnQcPosUntfGja-0POe7MbthXQM','Main',values)
        pickle.dump('done', open(docpath + "\start.pkl", "wb"))
    def sendtobase(self,id,sheetname,values):
        sys.excepthook = self.show_exception_and_exits
        creds = None
        print(values)
        print(sheetname)
        SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
        creds = ServiceAccountCredentials.from_json_keyfile_name('service.json', SCOPES)
        service = build('sheets', 'v4', credentials=creds)
        sheet = service.spreadsheets()

        valuebody = {
            'majorDimension': 'ROWS',
            'values': values
        }
        sheet.values().append(
            spreadsheetId=id,
            valueInputOption='USER_ENTERED',
            range=sheetname,
            body=valuebody
        ).execute()
        return
    def notification(self):
        sys.excepthook = self.show_exception_and_exits
        SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
        creds = ServiceAccountCredentials.from_json_keyfile_name('service.json', SCOPES)
        service = build('sheets', 'v4', credentials=creds)
        sheet = service.spreadsheets()
        result = sheet.values().get(spreadsheetId='1JQMkTVLZY_P5j5twRA6ecjnNg-u42rjgdHMTcJDebCI',
                                    range='Main').execute()
        value = result.get('values')
        return value
class scixexthread(QThread):
    runx = pyqtSignal(str)
    def __init__(self):
        super(scixexthread, self).__init__()
        print('extstart')
    def show_exception_and_exits(self,exc_type, exc_value, tb):
        import traceback
        # traceback.print_exception(exc_type, exc_value,tb))
        a = traceback.format_tb(tb)
        print(''.join(a))

        f = open(docpath + '\ERROR LOG.txt', 'a')
        f.write(str(exc_value))
        f.write("\n")
        f.write("Details:")
        f.write(''.join(a))
        f.write("\n")
        f.write("\n")
        f.close()
    def run(self):
        sys.excepthook = self.show_exception_and_exits
        QApplication.clipboard().dataChanged.connect(self.changed)
    def changed(self):
        sys.excepthook = self.show_exception_and_exits
        link=clipboard.paste()
        if link[:7]=='scix_ex':
            self.runx.emit(link[7:])
        else:
            pass
#if hasattr(QtCore.Qt,'AA_EnableHighDpiScaling'):
 #   QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling,True)
#if hasattr(QtCore.Qt,'AA_UseHighDpiPixmaps'):
 #   QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps,True)

os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
#qapp = QApplication(sys.argv)
app = QtWidgets.QApplication(sys.argv)
app.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)
screenrect=app.desktop().screenGeometry()
screenheight,screenwidth=screenrect.height(),screenrect.width()

window = Ui()
#window.setMaximumSize(screenwidth,screenheight)
window.showMaximized()

#sys.excepthook=window.show_exception_and_exit
app.exec_()
