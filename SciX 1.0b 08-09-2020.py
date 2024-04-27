#-*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function,
                        unicode_literals, generator_stop)
from citeproc.py2compat import *
from citeproc.source.bibtex import BibTeX
from citeproc import CitationStylesStyle, CitationStylesBibliography
from citeproc import formatter
from citeproc import Citation, CitationItem
from PyQt5.QAxContainer import QAxWidget
from PyQt5 import QtWidgets, uic, QtCore, QtGui, QtWebEngineWidgets
from PyQt5.QtCore import QThread, pyqtSignal, QDir
from PyQt5.QtWidgets import *
from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtCore import *
import zipfile
import sys
import time
from datetime import date
from bs4 import BeautifulSoup
import requests
import unicodedata
import os
import json
import textwrap
from urllib.parse import urlparse
from urllib.request import urljoin, urlopen, Request
import re
from crossref.restful import Works
from habanero import counts
import shutil
import pickle
from pdfrw import PdfReader, PdfWriter, PdfDict
import PyPDF2
from datetime import date
from hurry.filesize import size, si
from win32com.shell import shell, shellcon
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler
import warnings
from PyQt5.QAxContainer import QAxWidget
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QFileDialog,\
    QMessageBox
from PyQt5 import QtCore
from PyQt5 import QtWidgets
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from oauth2client.service_account import ServiceAccountCredentials
from google.auth.transport.requests import Request
import platform
import signal


warnings.filterwarnings("ignore")
global tempcurrentid
tempcurrentid=None
global docpath
docpath = shell.SHGetFolderPath(0, shellcon.CSIDL_PERSONAL, None, 0)
docpath = docpath + '\SciX'
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
        uic.loadUi('scix_1_alter.ui', self)
        #############toolbar#############################
        sys.excepthook = self.show_exception_and_exit
        self.timer=QTimer()
        self.addfromlocal.triggered.connect(self.funaddfromlocal)
        self.addfromlocalf.triggered.connect(self.funaddfromlocal)
        self.actionStyle.setEnabled(False)
       # self.actioncite.setEnabled(False)
        self.actionbiblio.setEnabled(False)
      #  self.actionRefresh.setEnabled(False)
        self.actionStyle.triggered.connect(self.setstyles)
        self.adobecheck=False
        self.openadobe.changed.connect(self.setadobe)
        self.actionbiblio.triggered.connect(References.getbiblio)
       # self.actionRefresh.triggered.connect(References.refreshall)
        self.actiondelete.triggered.connect(self.deletefiledialog)
        self.actionLocalbackup.triggered.connect(self.backuptrigger)
        self.actionCount_Citation.triggered.connect(self.citecount)
       # self.actionRefresh_2.triggered.connect(self.refresh)
        self.actionExit.triggered.connect(sys.exit)
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
        #self.filelist=QTreeView()
        #self.filelist.header().setDefaultSectionSize(150)
       # self.filelist.header().resizeSection(1,2520)
        self.filelist.header().sectionSizeFromContents(3)
        #self.filelist.resizeColumnToContents(0)
        self.filelist.setModel(self.modellist)
        self.filelist.setContextMenuPolicy(Qt.CustomContextMenu)
        self.filelist.customContextMenuRequested.connect(self.customMenu)
       # QTreeView.setContextMenuPolicy(Qt.CustomContextMenu)
       # QTreeView.customContextMenuRequested.connect(self.customMenu)
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

        #################SearchX###############################################
        self.searchx.setDocumentMode(True)
        self.searchx.tabBarDoubleClicked.connect(self.tab_open_doubleclick)
        self.searchx.currentChanged.connect(self.current_tab_changed)
        self.searchx.setTabsClosable(True)
        self.searchx.tabCloseRequested.connect(self.close_current_tab)
        self.addtab.clicked.connect(lambda _: self.add_new_tab())
        self.add_new_tab(QUrl('https://scholar.google.com/'), 'Homepage')
        self.urlbox.returnPressed.connect(self.navigate_to_url)
        self.back.clicked.connect(lambda: self.searchx.currentWidget().back())
        self.forward.clicked.connect(lambda: self.searchx.currentWidget().forward())
        self.refresh.clicked.connect(lambda: self.searchx.currentWidget().reload())
        self.home.clicked.connect(self.navigate_home)
        self.stop.clicked.connect(lambda: self.searchx.currentWidget().stop())

        myevent = PatternMatchingEventHandler("*", "", False, True)
        myevent.on_created = self.checkwordT
        myevent.on_modified = self.checkwordT
        myevent.on_deleted = self.checkwordF
        obs = Observer()
        obs.schedule(myevent, docpath, True)
        obs.start()
     #####################Searchquery##########################3
        self.squery.clicked.connect(self.searchquery)
        self.saveedit.clicked.connect(self.editsave)
    #####################updates######################
        QApplication.processEvents()
        self.startnoti()



    def startnoti(self):
        self.upnoti=notithread()
        self.upnoti.msg.connect(self.notiupdate)
        self.upnoti.start()
        #self.notithread.start(notiwork)
    def customMenu(self,point):
        self.contexttree=QtWidgets.QMenu(self.filelist)
        aropen=self.contexttree.addAction("Open")
        ardelete=self.contexttree.addAction("Delete")
        aropen.triggered.connect(self.openrightclicked)
        ardelete.triggered.connect(self.deleterightclicked)
        self.contexttree.exec_(self.filelist.mapToGlobal(point))
    def deleterightclicked(self):
        index = self.filelist.currentIndex()
        self.rightdeletefile()
    def openrightclicked(self):
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
    def checkwordT(self, event):
        sys.excepthook = self.show_exception_and_exit
        if event.src_path == docpath + '\currentid.txt':
            self.actionStyle.setEnabled(True)
            self.actioncite.setEnabled(True)
            self.actionbiblio.setEnabled(True)
            self.actionRefresh.setEnabled(True)

    def checkwordF(self, event):
        sys.excepthook = self.show_exception_and_exit
        if event.src_path == docpath + '\currentid.txt':
            self.actionStyle.setEnabled(False)
            self.actioncite.setEnabled(False)
            self.actionbiblio.setEnabled(False)
            self.actionRefresh.setEnabled(False)

    def setstyles(self):
        sys.excepthook = self.show_exception_and_exit
        Dialog_style = QtWidgets.QDialog()
        Dialog_style.setObjectName("Dialog_style")
        Dialog_style.resize(483, 150)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Dialog_style.sizePolicy().hasHeightForWidth())
        Dialog_style.setSizePolicy(sizePolicy)
        Dialog_style.setMaximumSize(QtCore.QSize(483, 150))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("ico/036.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        Dialog_style.setWindowIcon(icon)
        Dialog_style.setStyleSheet("background-color: rgb(194, 195, 255);")
        self.stylecombo = QtWidgets.QComboBox(Dialog_style)
        self.stylecombo.setGeometry(QtCore.QRect(127, 30, 331, 18))
        self.stylecombo.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.stylecombo.setEditable(True)
        self.stylecombo.setObjectName("stylecombo")
        self.label = QtWidgets.QLabel(Dialog_style)
        self.label.setGeometry(QtCore.QRect(20, 23, 98, 31))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(10)
        font.setBold(False)
        font.setWeight(50)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.styleapply = QtWidgets.QToolButton(Dialog_style)
        self.styleapply.setGeometry(QtCore.QRect(354, 81, 60, 25))
        self.styleapply.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.styleapply.setObjectName("styleapply")
        self.stylecancel = QtWidgets.QToolButton(Dialog_style)
        self.stylecancel.setGeometry(QtCore.QRect(268, 81, 60, 25))
        self.stylecancel.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.stylecancel.setObjectName("stylecancel")
        self.styleapply.clicked.connect(self.selectstyle)
        self.stylecancel.clicked.connect(Dialog_style.close)
        stylefiles = []
        for dirpath, dirnames, filenames in os.walk('styles'):
            for filename in [f for f in filenames if f.endswith(".csl")]:
                stylefiles.append(filename)
        print(stylefiles)
        self.combomodel = QtGui.QStandardItemModel()
        for i in range(len(stylefiles)):
            comboitem = QtGui.QStandardItem(stylefiles[i].strip('.csl'))
            self.combomodel.appendRow(comboitem)
        # current=self.combomodel.findItems(pickle.load(open(docpath+"\style.pkl", "rb")))
        self.stylecombo.setModel(self.combomodel)
        try:
            self.stylecombo.setCurrentText(pickle.load(open(docpath + "\style.pkl", "rb")))
        except:
            pass
        self.Dialog_style = Dialog_style
        self.retranslateUi_style(Dialog_style)
        QtCore.QMetaObject.connectSlotsByName(Dialog_style)
        Dialog_style.show()
        Dialog_style.exec_()

    def selectstyle(self):
        sys.excepthook = self.show_exception_and_exit
        print(self.stylecombo.currentText())
        pickle.dump(self.stylecombo.currentText(), open(docpath + "\style.pkl", "wb"))
        self.Dialog_style.close()

    def funaddfromlocal(self):
        sys.excepthook = self.show_exception_and_exit
        AddDialog=QtWidgets.QDialog()
        AddDialog.setObjectName("AddDialog")
        AddDialog.resize(389, 126)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("icons/187904-folders/png/folders-35.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
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
        self.flagman = True
        self.openfiledialog.clicked.connect(self.openfd)
       # self.typemanually.clicked.connect(self.manent)
        self.import_2.clicked.connect(self.importfromlocal)
        self.retranslateUi_add(AddDialog)
        self.AddDialog = AddDialog
        QtCore.QMetaObject.connectSlotsByName(AddDialog)
        AddDialog.show()

    def importfromlocal(self):
        sys.excepthook = self.show_exception_and_exit
        try:
            print(self.savetofolderpath)
        except:
            self.savetofolderpath=None
        if self.lineEdit.text()!='' and self.savetofolderpath is not None:

            read=PdfReader(self.lineEdit.text())
            doi=None
            try:
                doi=read.Info.doi.strip('()')
            except:
                try:
                  string = read.Info.Subject.strip('()')
                  keyword='doi:'
                  before_keyword, keyword, after_keyword = string.partition(keyword)
                  doi=after_keyword
                except:
                        pass
            if doi is not None:
                works = Works()
                meta = works.doi(doi)
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

                filerename = pickle.load(open(docpath + "\syslog2.pkl", "rb"))
                print(filerename)

                if author is None:
                    author = ['XXX', 'COULD NOT FETCH AUTHOR DETAILS', 'ADD MANUALLY']
                metadatain = PdfDict(Xauthor=author, Xdoi=doi, Xtitle=title, Xjournal=journal, Xyear=year,
                                     Xpage=page, Xissue=issue, Xvolume=volume, Xissn=issn, Xurl=url,
                                     Xdate=date.today())
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
                if filerename == 'Author-Title-Journal-Year':
                    filename = author[0] + '--' + title + '--' + journal + '--' + year + '.pdf'
                    filename = ''.join(c for c in filename if c not in "/\:*?<>|")
                    print(savetofolderpath + '/' + filename)
                    PdfWriter().write(savetofolderpath + '/' + filename, read)
                if filerename == 'Title-Author-Journal-Year':
                    filename = title + '--' + author[0] + '--' + journal + '--' + year + '.pdf'
                    filename = ''.join(c for c in filename if c not in "/\:*?<>|")
                    print(savetofolderpath + '/' + filename)
                    PdfWriter().write(savetofolderpath + '/' + filename, read)
                if filerename == 'Journal-Author-Title-Year':
                    filename = journal + '--' + author[0] + '--' + title + '--' + year + '.pdf'
                    filename = ''.join(c for c in filename if c not in "/\:*?<>|")
                    print(savetofolderpath + '/' + filename)
                    PdfWriter().write(savetofolderpath + '/' + filename, read)
                if filerename == 'Year-Author-Title-Journal':
                    filename = year + '--' + author[0] + '--' + title + '--' + journal + '.pdf'
                    filename = ''.join(c for c in filename if c not in "/\:*?<>|")
                    print(savetofolderpath + '/' + filename)
                    PdfWriter().write(savetofolderpath + '/' + filename, read)
                if filerename == 'Year-Journal-Author-Title':
                    filename = year + '--' + journal + '--' + author[0] + '--' + title + '.pdf'
                    filename = ''.join(c for c in filename if c not in "/\:*?<>|")
                    print(savetofolderpath + '/' + filename)
                    PdfWriter().write(savetofolderpath + '/' + filename, read)
                os.remove(self.lineEdit.text())
                try:
                    BibEntries = BibEntry()
                    out = open(savetofolderpath + '/' + filename.strip('.pdf') + '.bib', 'w',
                               encoding='utf-8')
                    out.write(BibEntries.doiToBib(doi).ToString())
                    out.close()
                    self.AddDialog.close()
                    self.statusBar.setStyleSheet('background-color: rgb(30, 255, 82);')
                    self.statusBar.showMessage('Import Successful', msecs=10000)
                    self.statusBar.show()
                    qApp.processEvents()
                    self.timer.singleShot(10000, self.statusBar.hide)
                    self.fileview(indexx=self.indexx)
                except:
                    self.statusBar.setStyleSheet('background-color: rgb(255, 28, 28);')
                    self.statusBar.showMessage('PDF has been imported but failed to create its BibTex file.')
                    self.statusBar.show()
                    qApp.processEvents()
                    self.timer.singleShot(10000, self.statusBar.hide)
                    self.fileview(indexx=self.indexx)

            else:
                self.statusBar.setStyleSheet('background-color: rgb(255, 28, 28);')
                self.statusBar.showMessage('Sorry. Failed to extract DOI. You can type DOI manually or type entires manually.')
                self.statusBar.show()
                qApp.processEvents()
                self.timer.singleShot(10000, self.statusBar.hide)
                self.mflag=True
                self.manent()
    def importfromlocals(self):
        sys.excepthook = self.show_exception_and_exit
        flag = False
        if self.lineEdit.text() != '':
            if self.enterdoi.text() != '':
                doi = self.enterdoi.text()
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
                filerename = pickle.load(open(docpath + "\syslog2.pkl", "rb"))
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
                flag = True
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
                        read)
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
                filerename = pickle.load(open(docpath + "\syslog2.pkl", "rb"))
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
                        read)
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
        sys.excepthook = self.show_exception_and_exit
        path, _ = QtWidgets.QFileDialog.getOpenFileName(None, "Select pdf", "*." + 'pdf')
        self.fpath = path
        self.lineEdit.setText(path)

    def add_new_tab(self, qurl=None, label="Blank"):
        sys.excepthook = self.show_exception_and_exit
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
        sys.excepthook = self.show_exception_and_exit
        self.download = download
        old_path = self.download.path()
        print(old_path)
        suffix = QtCore.QFileInfo(old_path).suffix()
        print(suffix)
        # path='C:/Users/LeBert/Downloads/tst.pdf'
        if suffix == 'pdf' or suffix == 'PDF':
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
        sys.excepthook = self.show_exception_and_exit
        doi = self.pastedoi.text()
        if doi != '':
            print(doi)

            self.Dialog_d.close()

            works = Works()
            meta = works.doi(doi)
            print(meta)
            try:
                title = meta['title']
                title = title[0]
                title = title.replace('/', '')

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
            filerename = pickle.load(open(docpath + "\syslog2.pkl", "rb"))
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
                filename = author[0] + '--' + title + '--' + journal + '--' + year + '.pdf'
                filename = ''.join(c for c in filename if c not in "/\:*?<>|")
                print(savetofolderpath + '/' + filename)
                PdfWriter().write(savetofolderpath + '/' + filename, read)
                # PdfWriter().write('C:/Users/LeBert/Desktop/testdd.pdf',read)

            if filerename == 'Title-Author-Journal-Year':
                filename = title + '--' + author[0] + '--' + journal + '--' + year + '.pdf'
                filename = ''.join(c for c in filename if c not in "/\:*?<>|")
                print(savetofolderpath + '/' + filename)
                PdfWriter().write(savetofolderpath + '/' + filename, read)
            if filerename == 'Journal-Author-Title-Year':
                filename = journal + '--' + author[0] + '--' + title + '--' + year + '.pdf'
                filename = ''.join(c for c in filename if c not in "/\:*?<>|")
                print(savetofolderpath + '/' + filename)
                PdfWriter().write(savetofolderpath + '/' + filename, read)
            if filerename == 'Year-Author-Title-Journal':
                filename = year + '--' + author[0] + '--' + title + '--' + journal + '.pdf'
                filename = ''.join(c for c in filename if c not in "/\:*?<>|")
                print(savetofolderpath + '/' + filename)
                PdfWriter().write(savetofolderpath + '/' + filename, read)
            if filerename == 'Year-Journal-Author-Title':
                filename = year + '--' + journal + '--' + author[0] + '--' + title + '.pdf'
                filename = ''.join(c for c in filename if c not in "/\:*?<>|")
                print(savetofolderpath + '/' + filename)
                PdfWriter().write(savetofolderpath + '/' + filename, read)
            os.remove(self.path_)

        else:
            print('nodoi')
            msg = QMessageBox(QMessageBox.Warning, "Empty field",
                              "Enter the DOI",
                              QMessageBox.Ok)
            # msg.setWindowIcon(QIcon(":/icons/app.svg"))
            msg.exec_()

    def fooo(self):
        sys.excepthook = self.show_exception_and_exit
        print("finished")
        Dialog_d = QDialog()
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
        self.flagman = False
        self.typemanual.clicked.connect(self.manent)
        self.retranslateUi_d(Dialog_d)
        self.buttonBox.accepted.connect(Dialog_d.accept)
        self.buttonBox.rejected.connect(Dialog_d.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog_d)
        Dialog_d.show()
        self.getdoi.clicked.connect(self._download)
        self.Dialog_d = Dialog_d

    def manent(self):
        sys.excepthook = self.show_exception_and_exit
        manualentry=QtWidgets.QDialog()
        manualentry.setObjectName("manualentry")
        manualentry.resize(289, 346)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(manualentry.sizePolicy().hasHeightForWidth())
        manualentry.setSizePolicy(sizePolicy)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("icons/1040213-ui/png/036-edit.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        manualentry.setWindowIcon(icon)
        manualentry.setStyleSheet("background-color: rgb(194, 195, 255);")
        self.formLayout = QtWidgets.QFormLayout(manualentry)
        self.formLayout.setObjectName("formLayout")
        self.label_11 = QtWidgets.QLabel(manualentry)
        font = QtGui.QFont()
        font.setFamily("Segoe UI Semibold")
        font.setPointSize(11)
        font.setBold(True)
        font.setWeight(75)
        self.label_11.setFont(font)
        self.label_11.setObjectName("label_11")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.label_11)
        self.onlydoi = QtWidgets.QLineEdit(manualentry)
        self.onlydoi.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.onlydoi.setObjectName("onlydoi")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.onlydoi)
        self.label_12 = QtWidgets.QLabel(manualentry)
        font = QtGui.QFont()
        font.setPointSize(8)
        self.label_12.setFont(font)
        self.label_12.setObjectName("label_12")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.label_12)
        self.line = QtWidgets.QFrame(manualentry)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.line.sizePolicy().hasHeightForWidth())
        self.line.setSizePolicy(sizePolicy)
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.line)
        self.line_2 = QtWidgets.QFrame(manualentry)
        self.line_2.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_2.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_2.setObjectName("line_2")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.FieldRole, self.line_2)
        self.label = QtWidgets.QLabel(manualentry)
        font = QtGui.QFont()
        font.setFamily("Segoe UI Semibold")
        font.setPointSize(11)
        font.setBold(True)
        font.setWeight(75)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.formLayout.setWidget(4, QtWidgets.QFormLayout.LabelRole, self.label)
        self.mtitle = QtWidgets.QLineEdit(manualentry)
        self.mtitle.setToolTip("")
        self.mtitle.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.mtitle.setObjectName("mtitle")
        self.formLayout.setWidget(4, QtWidgets.QFormLayout.FieldRole, self.mtitle)
        self.label_2 = QtWidgets.QLabel(manualentry)
        font = QtGui.QFont()
        font.setFamily("Segoe UI Semibold")
        font.setPointSize(11)
        font.setBold(True)
        font.setWeight(75)
        self.label_2.setFont(font)
        self.label_2.setObjectName("label_2")
        self.formLayout.setWidget(5, QtWidgets.QFormLayout.LabelRole, self.label_2)
        self.mauthors = QtWidgets.QLineEdit(manualentry)
        self.mauthors.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.mauthors.setText("")
        self.mauthors.setObjectName("mauthors")
        self.formLayout.setWidget(5, QtWidgets.QFormLayout.FieldRole, self.mauthors)
        self.label_3 = QtWidgets.QLabel(manualentry)
        font = QtGui.QFont()
        font.setFamily("Segoe UI Semibold")
        font.setPointSize(11)
        font.setBold(True)
        font.setWeight(75)
        self.label_3.setFont(font)
        self.label_3.setObjectName("label_3")
        self.formLayout.setWidget(6, QtWidgets.QFormLayout.LabelRole, self.label_3)
        self.mjournal = QtWidgets.QLineEdit(manualentry)
        self.mjournal.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.mjournal.setText("")
        self.mjournal.setObjectName("mjournal")
        self.formLayout.setWidget(6, QtWidgets.QFormLayout.FieldRole, self.mjournal)
        self.label_4 = QtWidgets.QLabel(manualentry)
        font = QtGui.QFont()
        font.setFamily("Segoe UI Semibold")
        font.setPointSize(11)
        font.setBold(True)
        font.setWeight(75)
        self.label_4.setFont(font)
        self.label_4.setObjectName("label_4")
        self.formLayout.setWidget(7, QtWidgets.QFormLayout.LabelRole, self.label_4)
        self.myear = QtWidgets.QLineEdit(manualentry)
        self.myear.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.myear.setObjectName("myear")
        self.formLayout.setWidget(7, QtWidgets.QFormLayout.FieldRole, self.myear)
        self.label_5 = QtWidgets.QLabel(manualentry)
        font = QtGui.QFont()
        font.setFamily("Segoe UI Semibold")
        font.setPointSize(11)
        font.setBold(True)
        font.setWeight(75)
        self.label_5.setFont(font)
        self.label_5.setObjectName("label_5")
        self.formLayout.setWidget(8, QtWidgets.QFormLayout.LabelRole, self.label_5)
        self.mpage = QtWidgets.QLineEdit(manualentry)
        self.mpage.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.mpage.setObjectName("mpage")
        self.formLayout.setWidget(8, QtWidgets.QFormLayout.FieldRole, self.mpage)
        self.label_6 = QtWidgets.QLabel(manualentry)
        font = QtGui.QFont()
        font.setFamily("Segoe UI Semibold")
        font.setPointSize(11)
        font.setBold(True)
        font.setWeight(75)
        self.label_6.setFont(font)
        self.label_6.setObjectName("label_6")
        self.formLayout.setWidget(9, QtWidgets.QFormLayout.LabelRole, self.label_6)
        self.missue = QtWidgets.QLineEdit(manualentry)
        self.missue.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.missue.setObjectName("missue")
        self.formLayout.setWidget(9, QtWidgets.QFormLayout.FieldRole, self.missue)
        self.label_7 = QtWidgets.QLabel(manualentry)
        font = QtGui.QFont()
        font.setFamily("Segoe UI Semibold")
        font.setPointSize(11)
        font.setBold(True)
        font.setWeight(75)
        self.label_7.setFont(font)
        self.label_7.setObjectName("label_7")
        self.formLayout.setWidget(10, QtWidgets.QFormLayout.LabelRole, self.label_7)
        self.mvolume = QtWidgets.QLineEdit(manualentry)
        self.mvolume.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.mvolume.setObjectName("mvolume")
        self.formLayout.setWidget(10, QtWidgets.QFormLayout.FieldRole, self.mvolume)
        self.label_8 = QtWidgets.QLabel(manualentry)
        font = QtGui.QFont()
        font.setFamily("Segoe UI Semibold")
        font.setPointSize(11)
        font.setBold(True)
        font.setWeight(75)
        self.label_8.setFont(font)
        self.label_8.setObjectName("label_8")
        self.formLayout.setWidget(11, QtWidgets.QFormLayout.LabelRole, self.label_8)
        self.missn = QtWidgets.QLineEdit(manualentry)
        self.missn.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.missn.setObjectName("missn")
        self.formLayout.setWidget(11, QtWidgets.QFormLayout.FieldRole, self.missn)
        self.label_9 = QtWidgets.QLabel(manualentry)
        font = QtGui.QFont()
        font.setFamily("Segoe UI Semibold")
        font.setPointSize(11)
        font.setBold(True)
        font.setWeight(75)
        self.label_9.setFont(font)
        self.label_9.setObjectName("label_9")
        self.formLayout.setWidget(12, QtWidgets.QFormLayout.LabelRole, self.label_9)
        self.mdoi = QtWidgets.QLineEdit(manualentry)
        self.mdoi.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.mdoi.setObjectName("mdoi")
        self.formLayout.setWidget(12, QtWidgets.QFormLayout.FieldRole, self.mdoi)
        self.label_10 = QtWidgets.QLabel(manualentry)
        font = QtGui.QFont()
        font.setFamily("Segoe UI Semibold")
        font.setPointSize(11)
        font.setBold(True)
        font.setWeight(75)
        self.label_10.setFont(font)
        self.label_10.setObjectName("label_10")
        self.formLayout.setWidget(13, QtWidgets.QFormLayout.LabelRole, self.label_10)
        self.murl = QtWidgets.QLineEdit(manualentry)
        self.murl.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.murl.setObjectName("murl")
        self.formLayout.setWidget(13, QtWidgets.QFormLayout.FieldRole, self.murl)
        self.buttonBox = QtWidgets.QDialogButtonBox(manualentry)
        self.buttonBox.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel | QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.formLayout.setWidget(14, QtWidgets.QFormLayout.FieldRole, self.buttonBox)

        self.retranslateUi_man(manualentry)
        # self.buttonBox.accepted.connect(self.mandownload)
        if self.flagman == True:
            self.buttonBox.accepted.connect(self.manlocalimport)
        else:
            self.buttonBox.accepted.connect(self.mandownload)
        self.buttonBox.rejected.connect(manualentry.reject)
        QtCore.QMetaObject.connectSlotsByName(manualentry)
        manualentry.show()
        # manualentry.exec_()
        self.manualentry_d = manualentry
    def manlocalimport(self):
        sys.excepthook = self.show_exception_and_exit
        print('s')
        if self.onlydoi.text()!="":
            works = Works()
            meta = works.doi(self.onlydoi.text())
            print(meta)
            try:
                title = meta['title']
                title = title[0]
                title = title.replace('/', '')

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
        else:
            author = self.mauthors.text()
            author = author.split(',')
            print(author[0])
            doi = self.mdoi.text()
            title = self.mtitle.text()
            journal = self.mjournal.text()
            year = self.myear.text()
            page = self.mpage.text()
            issue = self.missue.text()
            volume = self.mvolume.text()
            issn = self.missn.text()
            url = self.murl.text()

        filerename = pickle.load(open(docpath + "\syslog2.pkl", "rb"))
        print(filerename)
        read = PdfReader(self.lineEdit.text())
        read.Info

        metadatain = PdfDict(Xauthor=author, Xdoi=self.onlydoi.text(), Xtitle=title, Xjournal=journal, Xyear=year,
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

        if filerename == 'Author-Title-Journal-Year':
            filename = author[0] + '--' + title + '--' + journal + '--' + year + '.pdf'
            filename = ''.join(c for c in filename if c not in "/\:*?<>|")
            print(savetofolderpath + '/' + filename)
            PdfWriter().write(savetofolderpath + '/' + filename, read)
        if filerename == 'Title-Author-Journal-Year':
            filename = title + '--' + author[0] + '--' + journal + '--' + year + '.pdf'
            filename = ''.join(c for c in filename if c not in "/\:*?<>|")
            print(savetofolderpath + '/' + filename)
            PdfWriter().write(savetofolderpath + '/' + filename, read)
        if filerename == 'Journal-Author-Title-Year':
            filename = journal + '--' + author[0] + '--' + title + '--' + year + '.pdf'
            filename = ''.join(c for c in filename if c not in "/\:*?<>|")
            print(savetofolderpath + '/' + filename)
            PdfWriter().write(savetofolderpath + '/' + filename, read)
        if filerename == 'Year-Author-Title-Journal':
            filename = year + '--' + author[0] + '--' + title + '--' + journal + '.pdf'
            filename = ''.join(c for c in filename if c not in "/\:*?<>|")
            print(savetofolderpath + '/' + filename)
            PdfWriter().write(savetofolderpath + '/' + filename, read)
        if filerename == 'Year-Journal-Author-Title':
            filename = year + '--' + journal + '--' + author[0] + '--' + title + '.pdf'
            filename = ''.join(c for c in filename if c not in "/\:*?<>|")
            print(savetofolderpath + '/' + filename)
            PdfWriter().write(savetofolderpath + '/' + filename, read)
        os.remove(self.lineEdit.text())

        try:
            BibEntries = BibEntry()
            out = open(savetofolderpath + '/' + filename.strip('.pdf') + '.bib', 'w',
                       encoding='utf-8')
            out.write(BibEntries.doiToBib(self.onlydoi.text()).ToString())
            out.close()
            self.statusBar.setStyleSheet('background-color: rgb(30, 255, 82);')
            self.statusBar.showMessage('Import Successful', msecs=10000)
            self.statusBar.show()
            qApp.processEvents()
            self.timer.singleShot(10000, self.statusBar.hide)
        except:
            self.statusBar.setStyleSheet('background-color: rgb(255, 28, 28);')
            self.statusBar.showMessage(
                'PDF has been imported but failed to create its BibTex.')
            self.statusBar.show()
            qApp.processEvents()
            self.timer.singleShot(10000, self.statusBar.hide)
        self.manualentry_d.close()
        self.AddDialog.close()
        self.fileview(indexx=self.indexx)
    def mandownload(self):
        sys.excepthook = self.show_exception_and_exit
        self.manualentry_d.close()
        filerename = pickle.load(open(docpath + "\syslog2.pkl", "rb"))
        print(filerename)
        read = PdfReader(self.path_)
        read.Info
        print('s')
        author = self.mauthors.text()
        author = author.split(',')
        print(author[0])
        doi = self.mdoi.text()
        title = self.mtitle.text()
        journal = self.mjournal.text()
        year = self.myear.text()
        page = self.mpage.text()
        issue = self.missue.text()
        volume = self.mvolume.text()
        issn = self.missn.text()
        url = self.murl.text()
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
                    savetofolderpath + '/' + journal + '--' + author[0] + '--' + title + '--' + year + '.pdf', read)
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

    # self.setWindowTitle("%s - Mozarella Ashbadger" % title)

    def navigate_mozarella(self):
        sys.excepthook = self.show_exception_and_exit
        self.searchx.currentWidget().setUrl(QUrl("https://www.udemy.com/522076"))

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
            print(savetofolderpath)
            pdffiles = []
            for dirpath, dirnames, filenames in os.walk(savetofolderpath):
                for filename in [f for f in filenames if f.endswith(".pdf" or ".PDF")]:
                    pdffiles.append(filename)
            print(pdffiles)
            if findex == 0:
                try:
                    self.fileview(indexx=self.indexx)
                except:
                    pass
            if findex == 1:
                auth = []
                for i in range(len(pdffiles)):
                    readd = PdfReader(savetofolderpath + '/' + pdffiles[i])
                    try:
                        for j in range(len(readd.Info.Xauthor)):
                            auth.append(readd.Info.Xauthor[j].decode().strip('()'))
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
                        journ.append(readd.Info.Xjournal.decode().strip('()'))
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
                        yer.append(readd.Info.Xyear.decode().strip('()'))
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
        sys.excepthook = self.show_exception_and_exit
        global link
        link = (self.input.text())
        # global savefolderpath
        # print(len(savefolderpath))
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
                icon.addPixmap(QtGui.QPixmap("icons/1040213-ui/png/028-download.png"), QtGui.QIcon.Normal,
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
                global downloadstatus
                downloadstatus = self.downloadstatus
                self.doned.clicked.connect(self.ref)
                self.canceld.clicked.connect(self.dexit)

                self.calc = External()
                self.calc.countChanged.connect(self.onCountChanged)
                # print('p='+self.calc.countChanged)
                self.calc.start()

                self.retranslateUi(Dialog)
                QtCore.QMetaObject.connectSlotsByName(Dialog)

                Dialog.show()
            else:
                msgb = QMessageBox(QMessageBox.Warning, "Warning",
                                   "Select a folder to download",
                                   QMessageBox.Ok)
                icon = QtGui.QIcon()
                icon.addPixmap(QtGui.QPixmap("ico/027.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
                msgb.setWindowIcon(icon)
                msgb.exec_()


        else:
            print('no link')
            msg = QMessageBox(QMessageBox.Warning, "Empty field",
                              "Enter a proper link!",
                              QMessageBox.Ok)
            # msg.setWindowIcon(QIcon(":/icons/app.svg"))
            msg.exec_()

    def dexit(self):
        sys.excepthook = self.show_exception_and_exit
        print('exit')
        self.calc.exit()
        self.Dialog.close()
        global threadactive
        threadactive = False

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

    def onCountChanged(self, value):
        sys.excepthook = self.show_exception_and_exit
        # print(value)
        self.progressBar.setValue(value)

    def filterview(self, itemm):
        sys.excepthook = self.show_exception_and_exit
        sortitem = itemm.text()
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
        self.filelist.header().resizeSection(0,180)
        self.filelist.header().resizeSection(1, 340)
        self.filelist.header().resizeSection(2, 120)
        self.filelist.header().resizeSection(3, 50)
        self.filelist.header().resizeSection(4, 50)

        global savetofolderpath
        savetofolderpath = self.model.filePath(indexx)
        self.savetofolderpath = savetofolderpath
        print(savetofolderpath)

        pdffiles = []
        for dirpath, dirnames, filenames in os.walk(savetofolderpath):
            for filename in [f for f in filenames if f.endswith(".pdf" or ".PDF")]:
                pdffiles.append(filename)
        print(pdffiles)
        self.dict = {}
        for row in range(len(pdffiles)):
            # self.dictl=[]
            try:
                for column in range(5):
                    read = PdfReader(savetofolderpath + "/" + pdffiles[row])
                    Xauthors = ' '
                    for i in range(len(read.Info.Xauthor)):
                        Xauthors = Xauthors + read.Info.Xauthor[i].decode().strip('()') + ';'
                    data = [Xauthors, read.Info.Xtitle.decode().strip('()'), read.Info.Xjournal.decode().strip('()'),
                            read.Info.Xyear.decode().strip('()'), read.Info.Xdate.strip('()')]
                    item = QtGui.QStandardItem(data[column])
                    self.modellist.setItem(row, column, item)
                    if column == 0:
                        item.setIcon(QtGui.QIcon('ico/023.png'))
                    else:
                        pass
                    # item.icon(QtGui.QIcon('C:/Users/LeBert/PycharmProjects/alpha/icons/1040213-ui/png/pdf.png'))
                    item.setEditable(False)
                    self.dict[str(item)] = pdffiles[row]
            except:
                pass

        print(self.dict)
        print(len(self.dict))
        self.filtercombo.setCurrentIndex(0)
        self.filedup = None
        self.filelist.doubleClicked.connect(self.treeitemdoubleClicked)
        self.filelist.clicked.connect(self.treeitemsingleclicked)
        #QShortcut(QtGui.QKeySequence("Return"), self.filelist,self.treeitemdoubleClicked(index=self.filelist.currentIndex()))

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
        sys.excepthook = self.show_exception_and_exit
        self.notesindex=index
        print(index)
        item = self.modellist.itemFromIndex(index)
        global file
        file = self.dict[str(item)]
        if self.filedup != file:
            self.filedup = file
            print(file)
            print(item)
            # loc=dict[item]
            # print(loc)
            row = item.row()
            print(row)
            print(self.savetofolderpath)
            read = PdfReader(self.savetofolderpath + "/" + file)
            print(read.Info)
            global citedoi
            citedoi = read.Info.Xdoi.decode().strip('()')
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
            self.statusBar.setStyleSheet('background-color: rgb(255, 238, 49);')
            self.statusBar.showMessage('%s'% str(read.Info.Xtitle.decode()).strip('()'))
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
            self.filedup = None
    def treeitemdoubleClicked(self, index):
        sys.excepthook = self.show_exception_and_exit
        self.notesindex=index
        if self.adobecheck==False:
            print(index)
            item = self.modellist.itemFromIndex(index)
            global file
            file = self.dict[str(item)]
            if self.filedup != file:
                self.filedup = file
                print(file)
                print(item)
                # loc=dict[item]
                # print(loc)
                row = item.row()
                print(row)
                print(self.savetofolderpath)
                read = PdfReader(self.savetofolderpath + "/" + file)
                print(read.Info)
                global citedoi
                citedoi = read.Info.Xdoi.decode().strip('()')
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
                self.titleinfo.setText(str(read.Info.Xtitle.decode()).strip('()'))
                self.journalinfo.setText(str(read.Info.Xjournal.decode()).strip('()'))
                self.issninfo.setText(str(read.Info.Xissn.decode()).strip('()'))
                self.urlinfo.setText(str(read.Info.Xurl.decode()).strip('()'))
                self.doiinfo.setText(str(read.Info.Xdoi.decode()).strip('()'))
                self.authorinfo.clear()
                for i in range(len(read.Info.Xauthor)):
                    self.authorinfo.append(str(read.Info.Xauthor[i].decode()).strip('()'))
                # self.fileinfo.setText(str(read.Info.Xauthor).strip('[]'))
                PDFJS = 'file:///web/viewer.html'
                PDF = 'file:///' + self.savetofolderpath + '/' + file

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
                self.axWidget = QAxWidget()
                self.axWidget.clear()
                tab3 = self.maintab.addTab(self.axWidget, file)
                self.maintab.setTabIcon(tab3,
                                        QtGui.QIcon('ico/041.png'))
                self.axWidget.setFocusPolicy(QtCore.Qt.StrongFocus)
                self.axWidget.clear()
                a = self.axWidget.setControl("Microsoft Web Browser")
                print(a)
                self.axWidget.dynamicCall('Navigate(const QString&)', self.savetofolderpath + '/' + file)

            else:
                pass


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
            read = PdfReader(self.savetofolderpath + '/' + pdffiles[j])
            try:
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
                try:
                    for column in range(5):
                        read = PdfReader(self.savetofolderpath + "/" + matchedfiles[row])
                        Xauthors = ' '
                        for i in range(len(read.Info.Xauthor)):
                            Xauthors = Xauthors + read.Info.Xauthor[i].decode().strip('()') + ';'
                        data = [Xauthors, read.Info.Xtitle.decode().strip('()'),
                                read.Info.Xjournal.decode().strip('()'),
                                read.Info.Xyear.decode().strip('()'), read.Info.Xdate.strip('()')]
                        item = QtGui.QStandardItem(data[column])
                        self.modellist.setItem(row, column, item)
                        if column == 0:
                            item.setIcon(QtGui.QIcon('ico/023.png'))
                        else:
                            pass
                        # item.icon(QtGui.QIcon('C:/Users/LeBert/PycharmProjects/alpha/icons/1040213-ui/png/pdf.png'))
                        item.setEditable(False)
                        self.dict[str(item)] = matchedfiles[row]
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

    def searchqueries(self):
        sys.excepthook = self.show_exception_and_exit
        pdffiles = []
        matchedfiles = []
        for dirpath, dirnames, filenames in os.walk(self.savetofolderpath):
            for filename in [f for f in filenames if f.endswith(".pdf" or ".PDF")]:
                pdffiles.append(filename)
        print(pdffiles)

        for j in range(len(pdffiles)):
            self.statusBar.setStyleSheet('background-color: rgb(67, 211, 255);')
            self.statusBar.showMessage('Searching in %s' % pdffiles[j].strip('.pdf'))
            self.statusBar.show()
            qApp.processEvents()
            try:
                object = PyPDF2.PdfFileReader(self.savetofolderpath + '/' + pdffiles[j])
                NumPages = object.getNumPages()
                String = self.sstring.text()
                flag = False
                for i in range(0, NumPages):
                    if flag == False:
                        PageObj = object.getPage(i)
                        print("this is page " + str(i))
                        Text = PageObj.extractText()
                        print(Text)
                        ResSearch = re.search(String, Text)
                        print(ResSearch)
                        if ResSearch is not None:
                            matchedfiles.append(pdffiles[j])
                            flag = True
                        else:
                            pass
                    else:
                        pass
            except:
                pass

        print(len(matchedfiles))
        print(matchedfiles)

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
                try:
                    for column in range(5):
                        read = PdfReader(self.savetofolderpath + "/" + matchedfiles[row])
                        Xauthors = ' '
                        for i in range(len(read.Info.Xauthor)):
                            Xauthors = Xauthors + read.Info.Xauthor[i].decode().strip('()') + ';'
                        data = [Xauthors, read.Info.Xtitle.decode().strip('()'),
                                read.Info.Xjournal.decode().strip('()'),
                                read.Info.Xyear.decode().strip('()'), read.Info.Xdate.strip('()')]
                        item = QtGui.QStandardItem(data[column])
                        self.modellist.setItem(row, column, item)
                        if column == 0:
                            item.setIcon(QtGui.QIcon('ico/023.png'))
                        else:
                            pass
                        # item.icon(QtGui.QIcon('C:/Users/LeBert/PycharmProjects/alpha/icons/1040213-ui/png/pdf.png'))
                        item.setEditable(False)
                        self.dict[str(item)] = matchedfiles[row]
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
    def refresh(self):
        sys.excepthook = self.show_exception_and_exit
        self.fileview(indexx=self.indexx)
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
        self.doned.setText(_translate("Dialog", "Done"))
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
    def notiupdate(self,msg):
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

       # sys.excepthook = self.show_exception_and_exit
        self.statusBar.setStyleSheet('background-color: rgb(255, 28, 28);')
        self.statusBar.showMessage('ERROR:'+error[:18])
        self.statusBar.show()
        qApp.processEvents()
       # QTimer.stop()
        self.timer.singleShot(10000, self.statusBar.hide)


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

class External(QThread, QtWidgets.QMessageBox,QMainWindow):
    """
    Runs a counter thread.
    """
    countChanged = pyqtSignal(int)

    def __init__(self,*args, **kwargs):

        super(External, self).__init__(*args, **kwargs)
        sys.excepthook = self.show_exception_and_exits
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
        downloadstatus.setText("ERROR:"+str(exc_value))
      #  window.errorstatus(error=str(exc_value))

    def run(self):
        sys.excepthook = self.show_exception_and_exits
        downloadstatus.setText('Initializing...')
        count = 0
        self.countChanged.emit(count)
        if 'link' and 'savetofolderpath' in globals() is not None:
            try:
                print(link)
                print(savetofolderpath)
                global threadactive
                threadactive = True
                check=False
                try:
                    req=requests.get(link,allow_redirects=True)
                except:
                    downloadstatus.setText('URL Error!')
                if req.headers['Content-Type']=='application/pdf' or req.headers['Content-Type']=='application/pdf;charset=UTF-8':
                    count = 20
                    self.countChanged.emit(count)
                    downloadstatus.setText('Downloading the pdf...')
                    try:
                        byte = req.headers['Content-Length']
                        print('siz')
                        siz = size(int(byte), system=si)
                    except:
                        siz = ''
                    downloadstatus.setText('Downloading pdf (size:%s)' % siz)
                    count = 40
                    self.countChanged.emit(count)
                    pdfl = savetofolderpath + '/test.pdf'
                    open(pdfl, 'wb').write(req.content)
                    read=PdfReader(pdfl)
                    doi = None
                    try:
                        doi = read.Info.doi.strip('()')
                    except:
                        try:
                            string = read.Info.Subject.strip('()')
                            keyword = 'doi:'
                            before_keyword, keyword, after_keyword = string.partition(keyword)
                            doi = after_keyword
                        except:
                            downloadstatus.setText('Trying again')
                            check=True
                else:
                    check=True
                if check==True:
                    downloadstatus.setText('Searching the web')
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
                    downloadstatus.setText('Searching the web...')
                    if threadactive == True:
                        count = 30
                        self.countChanged.emit(count)
                        formdata = dict((field.get('name'), field.get('value')) for field in fields)
                        formdata['request'] = link
                        posturl = urljoin(URL, form['action'])
                        print(posturl)
                        downloadstatus.setText('Fetching the url...')

                    if threadactive == True:
                        count = 40
                        self.countChanged.emit(count)
                        res = sreq.post(posturl, data=formdata)
                        soups = BeautifulSoup(res.text, features="html5lib")
                        src = soups.find('iframe')
                        count = 50
                        self.countChanged.emit(count)
                        src = src['src']
                        count = 55
                        self.countChanged.emit(count)
                        print(src)
                        if src[0:2] == '//':
                            src = 'https:' + src
                        print(src)
                        downloadstatus.setText('Please wait...')
                        try:
                            req = Request(src, method='HEAD')
                            f = urlopen(req)
                            print('f')
                            byte = f.headers['Content-Length']
                            print('siz')
                            siz = size(int(byte), system=si)
                        except:
                            siz = ''

                        downloadstatus.setText('Downloading pdf (size:%s)' % siz)
                        r = requests.get(src, allow_redirects=True)
                        pdfl = savetofolderpath + '/test.pdf'
                        print(pdfl)
                        open(pdfl, 'wb').write(r.content)
                        downloadstatus.setText('Download successful')
                        count = 60
                        self.countChanged.emit(count)
                        pattern = re.compile(r"var doi = '(.*?)';$", re.MULTILINE | re.DOTALL)
                        script = soups.find("script", text=pattern)
                        downloadstatus.setText('Fetching DOI...')
                        doi = pattern.search(script.text).group(1)
                        count = 65
                        self.countChanged.emit(count)
                        print(doi)
                        downloadstatus.setText('DOI:%s' % doi)

                if threadactive == True:
                    works = Works()
                    meta = works.doi(doi)
                    count = 70
                    self.countChanged.emit(count)
                    downloadstatus.setText('Fetching data...')
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
                    filerename = pickle.load(open(docpath + "\syslog2.pkl", "rb"))
                    print(filerename)
                    downloadstatus.setText('Checking your rename preference...')
                    read = PdfReader(pdfl)
                    read.Info
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
                    downloadstatus.setText('Updating pdf...')
                    if filerename == 'Author-Title-Journal-Year':
                        count = 90
                        self.countChanged.emit(count)
                        filename = author[0] + '--' + title + '--' + journal + '--' + year + '.pdf'
                        filename = ''.join(c for c in filename if c not in "/\:*?<>|")
                        print(savetofolderpath + '/' + filename)
                        PdfWriter().write(savetofolderpath + '/' + filename, read)
                    if filerename == 'Title-Author-Journal-Year':
                        count = 90
                        self.countChanged.emit(count)
                        filename = title + '--' + author[0] + '--' + journal + '--' + year + '.pdf'
                        filename = ''.join(c for c in filename if c not in "/\:*?<>|")
                        print(savetofolderpath + '/' + filename)
                        PdfWriter().write(savetofolderpath + '/' + filename, read)
                    if filerename == 'Journal-Author-Title-Year':
                        count = 90
                        self.countChanged.emit(count)
                        filename = journal + '--' + author[0] + '--' + title + '--' + year + '.pdf'
                        filename = ''.join(c for c in filename if c not in "/\:*?<>|")
                        print(savetofolderpath + '/' + filename)
                        PdfWriter().write(savetofolderpath + '/' + filename, read)
                    if filerename == 'Year-Author-Title-Journal':
                        count = 90
                        self.countChanged.emit(count)
                        filename = year + '--' + author[0] + '--' + title + '--' + journal + '.pdf'
                        filename = ''.join(c for c in filename if c not in "/\:*?<>|")
                        print(savetofolderpath + '/' + filename)
                        PdfWriter().write(savetofolderpath + '/' + filename, read)
                    if filerename == 'Year-Journal-Author-Title':
                        count = 90
                        self.countChanged.emit(count)
                        filename = year + '--' + journal + '--' + author[0] + '--' + title + '.pdf'
                        filename = ''.join(c for c in filename if c not in "/\:*?<>|")
                        print(savetofolderpath + '/' + filename)
                        PdfWriter().write(savetofolderpath + '/' + filename, read)
                    os.remove(pdfl)
                    count = 95
                    self.countChanged.emit(count)
                    downloadstatus.setText('Fetching bib file...')
                    try:
                        BibEntries = BibEntry()
                        out = open(savetofolderpath + '/' + filename.strip('.pdf') + '.bib', 'w',
                                   encoding='utf-8')
                        out.write(BibEntries.doiToBib(doi).ToString())
                        out.close()
                    except:
                        downloadstatus.setText('Failed to get bib file.')

                       # msg = QMessageBox(QMessageBox.Warning, "Not Found",
                        #                  "Could not fetch bib file",
                         #                 QMessageBox.Ok)
                        ##icon = QtGui.QIcon()
                        #icon.addPixmap(QtGui.QPixmap("ico/027.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
                        #msg.setWindowIcon(icon)
                        #msg.exec_()

                    downloadstatus.setText('Import completed. Click "Done" to close')
                    count = 100
                    self.countChanged.emit(count)

            except ConnectionError:
                downloadstatus.setText('Connection error. Check your internet!')
                count = 0
                self.countChanged.emit(count)
                #msg = QMessageBox(QMessageBox.Warning, "Download Failed",
                 #                 "Failed to download",
                  #                QMessageBox.Ok)
                #icon = QtGui.QIcon()
                #icon.addPixmap(QtGui.QPixmap("ico/027.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
                #msg.setWindowIcon(icon)
                #msg.exec_()
        else:
            pass


class registry():
    def __init__(self):
        print('reg')

class notithread(QThread):
    msg= pyqtSignal(str)
    def run(self):
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
        try:
            try:
                print(self.msgs)
            except:
                print('nr')
                self.msgs = self.notification()
            for i in range(len(self.msgs)):
                self.msg.emit(str(self.msgs[i]).strip('[]'))
                time.sleep(15)
        except:
            pass
    def currentregister(self):
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
            ver = '1.0b'
            values = (
                (todate, tomonth, toyear, ip, city, ver, country, region, os, version, release),
            )

            self.sendtobase('15o39VCF486957LN32dIhOhBFcKtQC_EyXiI-4CgN2hw', 'Sheet1', values)
            pickle.dump(todate, open(docpath + "\currentreg.pkl", "wb"))
        except:
            pass
    def firstregister(self):
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
        ver='1.0b'
        values=(
            (ip,city,ver,country,region,os,version,release,processor),
        )

        self.sendtobase('1J1v0a1yJqnX3lZb7vnQcPosUntfGja-0POe7MbthXQM','Main',values)
        pickle.dump('done', open(docpath + "\start.pkl", "wb"))
    def sendtobase(self,id,sheetname,values):
        creds = None
        print(values)
        print(sheetname)
        SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
        creds = ServiceAccountCredentials.from_json_keyfile_name('SciX service.json', SCOPES)
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
        SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
        creds = ServiceAccountCredentials.from_json_keyfile_name('SciX service.json', SCOPES)
        service = build('sheets', 'v4', credentials=creds)
        sheet = service.spreadsheets()
        result = sheet.values().get(spreadsheetId='1JQMkTVLZY_P5j5twRA6ecjnNg-u42rjgdHMTcJDebCI',
                                    range='Main').execute()
        value = result.get('values')
        return value
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


class References(QtWidgets.QMessageBox):

    def warn(citation_item):
        print("WARNING: Reference with key '{}' not found in the bibliography."
              .format(citation_item.key))

    def getcite(self):
        #read currentid
        idfile = open(docpath + "\currentid.txt", "r")
        global currentid
        currentid = idfile.read()
        print(int(currentid))
        idfile.close()
        print(savetofolderpath + '/' + file.strip('.pdf' or '.PDF') + ".bib")
        #read selected bib
        getbib = open(
            savetofolderpath + '/' + file.strip('.pdf' or '.PDF') + ".bib", "r")
        tempbib = getbib.read()
        getbib.close()

        #save to currentid selected bib
        print(docpath + "\\" + currentid + ".bib")
        newbib = open(docpath + "\\" + currentid + ".bib", "a")
        newbib.write(tempbib + "\n")
        newbib.close()
        #save currentid doi in order
        print("doilist")
        doic=open(docpath + "\\" + currentid + "_doilist.txt", "a")
        doic.write(citedoi+"\n")
        doic.close()
        print("mun")
        num_lines = sum(1 for line in open(docpath + "\\" + currentid + "_doilist.txt"))
        print(num_lines)
        lines = [line.rstrip() for line in open(docpath + "\\" + currentid + "_doilist.txt")]

        #format
        bibsource = BibTeX(docpath + "\\" + currentid + ".bib")
        style=pickle.load(open(docpath + "\style.pkl", "rb"))+".csl"
        print(style)
        bib_style = CitationStylesStyle(r'styles/'+style)
        bibliography = CitationStylesBibliography(bib_style, bibsource, formatter.plain)
        print(citedoi)
        print(lines)
        for i in range(len(lines)):
            cite = Citation([CitationItem(lines[i])])
            bibliography.register(cite)
            if i == len(lines)-1:
                print(str((bibliography.cite(cite, References.warn))))
                outcite=open(docpath + "\\" + currentid + "citeout.txt", "w")
                outcite.write(str(bibliography.cite(cite,References.warn)))
                outcite.close()
                newcit = open(docpath + "\\" + currentid + "_clist.txt", "a")
                newcit.write(str(bibliography.cite(cite,References.warn)+ "\n"))
                newcit.close()
        global items
        items = []
        for item in bibliography.bibliography():
            #print('ss')
            items.append(str(item))

        #print(''.join(items))
    def getbiblio(self):
        global items
        print(''.join(items))
        outbiblio = open(docpath + "\\" + currentid + "biblioout.txt", "w")
        outbiblio.write(''.join(items))
        outbiblio.close()
    def refreshall(self):
        #curntid
        idfile = open(docpath + "\currentid.txt", "r")
        global currentid
        currentid = idfile.read()
        idfile.close()
        print(currentid)
        #doilist
        lines = [line.rstrip() for line in open(docpath + "\\" + currentid + "_doilist.txt")]
        bibsource = BibTeX(docpath + "\\" + currentid + ".bib")
        style = pickle.load(open(docpath + "\style.pkl", "rb")) + ".csl"
        print(style)
        bib_style = CitationStylesStyle(r'styles/' + style)
        print('2231')
        bibliography = CitationStylesBibliography(bib_style, bibsource, formatter.plain)
        print("2233")
        try:
            os.remove((docpath + "\\" + currentid + "_clist_R.txt"))
        except:
            pass
        try:
            for i in range(len(lines)):
                cite = Citation([CitationItem(lines[i])])
                print(i)
                bibliography.register(cite)
                print((bibliography.cite(cite, References.warn)))
                newcit = open(docpath + "\\" + currentid + "_clist_R.txt", "a")
                newcit.write(str(bibliography.cite(cite, References.warn)) + "\n")
                newcit.close()
            global items
            items = []
            for item in bibliography.bibliography():
                # print('ss')
                items.append(str(item))
            print(''.join(items))
            outbiblio = open(docpath + "\\" + currentid + "biblioout_R.txt", "w")
            outbiblio.write(''.join(items))
            outbiblio.close()
        except:
            try:
                os.remove((docpath + "\\" + currentid + "_clist_R.txt"))
                os.remove((docpath + "\\" + currentid + "biblioout_R.txt"))
            except:
                pass
            msg = QMessageBox(QMessageBox.Warning, "Rendering Failed",
                              "Failed to render using selected style. Feel free to report",
                              QMessageBox.Ok)
            icon = QtGui.QIcon()
            icon.addPixmap(QtGui.QPixmap("ico/027.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
            msg.setWindowIcon(icon)
            msg.exec_()

if hasattr(QtCore.Qt,'AA_EnableHighDpiScaling'):
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling,True)
if hasattr(QtCore.Qt,'AA_UseHighDpiPixmaps'):
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps,True)
app = QtWidgets.QApplication(sys.argv)
window = Ui()
window.showMaximized()
#sys.excepthook=window.show_exception_and_exit
app.exec_()
