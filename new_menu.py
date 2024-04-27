# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'new_menu.ui'
#
# Created by: PyQt5 UI code generator 5.13.2
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QUrl
from PyQt5.QtWidgets import *
from PyQt5.QtWebEngineWidgets import *
import pickle

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1241, 668)
        MainWindow.setToolButtonStyle(QtCore.Qt.ToolButtonIconOnly)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.centralwidget.sizePolicy().hasHeightForWidth())
        self.centralwidget.setSizePolicy(sizePolicy)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setSizeConstraint(QtWidgets.QLayout.SetMinimumSize)
        self.gridLayout.setObjectName("gridLayout")
        self.groupBox = QtWidgets.QGroupBox(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupBox.sizePolicy().hasHeightForWidth())
        self.groupBox.setSizePolicy(sizePolicy)
        self.groupBox.setStyleSheet("")
        self.groupBox.setAlignment(QtCore.Qt.AlignCenter)
        self.groupBox.setFlat(False)
        self.groupBox.setCheckable(False)
        self.groupBox.setChecked(False)
        self.groupBox.setObjectName("groupBox")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.groupBox)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setSizeConstraint(QtWidgets.QLayout.SetDefaultConstraint)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label = QtWidgets.QLabel(self.groupBox)
        self.label.setText("")
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)
        self.label_3 = QtWidgets.QLabel(self.groupBox)
        self.label_3.setText("")
        self.label_3.setObjectName("label_3")
        self.horizontalLayout.addWidget(self.label_3)
        self.inputurl = QtWidgets.QLineEdit(self.groupBox)
        self.inputurl.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.inputurl.setDragEnabled(True)
        self.inputurl.setObjectName("inputurl")
        self.horizontalLayout.addWidget(self.inputurl)
        self.downloadbutton = QtWidgets.QToolButton(self.groupBox)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/new/img_71049.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.downloadbutton.setIcon(icon)
        self.downloadbutton.setIconSize(QtCore.QSize(20, 21))
        self.downloadbutton.setCheckable(False)
        self.downloadbutton.setToolButtonStyle(QtCore.Qt.ToolButtonTextBesideIcon)
        self.downloadbutton.setObjectName("downloadbutton")
        self.downloadbutton.clicked.connect(self.scidexe)
        self.horizontalLayout.addWidget(self.downloadbutton)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.folderlist = QtWidgets.QListWidget(self.groupBox)
        self.folderlist.setObjectName("folderlist")
        self.verticalLayout.addWidget(self.folderlist)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.label_2 = QtWidgets.QLabel(self.groupBox)
        self.label_2.setScaledContents(False)
        self.label_2.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_2.setObjectName("label_2")
        self.horizontalLayout_2.addWidget(self.label_2)
        self.filtercombo = QtWidgets.QComboBox(self.groupBox)
        self.filtercombo.setCurrentText("")
        self.filtercombo.setObjectName("filtercombo")
        self.horizontalLayout_2.addWidget(self.filtercombo)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.sortlist = QtWidgets.QListWidget(self.groupBox)
        self.sortlist.setObjectName("sortlist")
        self.verticalLayout.addWidget(self.sortlist)
        self.gridLayout.addWidget(self.groupBox, 0, 1, 1, 1)
        self.tab_3 = QtWidgets.QTabWidget(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(4)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tab_3.sizePolicy().hasHeightForWidth())
        self.tab_3.setSizePolicy(sizePolicy)
        self.tab_3.setObjectName("tab_3")
        self.tab = QtWidgets.QWidget()
        self.tab.setObjectName("tab")
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout(self.tab)
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.filelist = QtWidgets.QTreeWidget(self.tab)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.filelist.sizePolicy().hasHeightForWidth())
        self.filelist.setSizePolicy(sizePolicy)
        self.filelist.setMinimumSize(QtCore.QSize(0, 0))
        self.filelist.setObjectName("filelist")
        self.horizontalLayout_4.addWidget(self.filelist)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.horizontalLayout_4.addLayout(self.verticalLayout_2)
        self.tab_3.addTab(self.tab, "")
        PDFJS = 'file:///C:/Users/LeBert/Desktop/web/viewer.html'
        # PDFJS = 'file:///usr/share/pdf.js/web/viewer.html'
        PDF = 'file:///C:/Users/LeBert/Desktop/balamurugan2019.pdf'


        self.tab_2 = QWebEngineView()
        #self.tab_2 = QtWidgets.QWidget()
        self.tab_2.setObjectName("tab_2")
        self.tab_3.addTab(self.tab_2, "")

        self.tab_2.load(QtCore.QUrl.fromUserInput('%s?file=%s'%(PDFJS, PDF)))
        #self.centralwidget(self.tab_2)

        #self.show()
        self.gridLayout.addWidget(self.tab_3, 0, 0, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1241, 21))
        self.menubar.setObjectName("menubar")
        self.menuFile = QtWidgets.QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")
        self.menuTools = QtWidgets.QMenu(self.menubar)
        self.menuTools.setObjectName("menuTools")
        self.menuRename_preference = QtWidgets.QMenu(self.menuTools)
        self.menuRename_preference.setToolTipDuration(1)
        self.menuRename_preference.setTearOffEnabled(False)
        self.menuRename_preference.setToolTipsVisible(True)
        self.menuRename_preference.setObjectName("menuRename_preference")
        self.menuHelp = QtWidgets.QMenu(self.menubar)
        self.menuHelp.setObjectName("menuHelp")
        MainWindow.setMenuBar(self.menubar)
        self.statusBar = QtWidgets.QStatusBar(MainWindow)
        self.statusBar.setObjectName("statusBar")
        MainWindow.setStatusBar(self.statusBar)
        self.toolBar = QtWidgets.QToolBar(MainWindow)
        self.toolBar.setObjectName("toolBar")
        MainWindow.addToolBar(QtCore.Qt.TopToolBarArea, self.toolBar)
        self.actionAdd_from_local = QtWidgets.QAction(MainWindow)
        self.actionAdd_from_local.setObjectName("actionAdd_from_local")
        self.actionAdd_from_local_2 = QtWidgets.QAction(MainWindow)
        self.actionAdd_from_local_2.setObjectName("actionAdd_from_local_2")
        self.actionExit = QtWidgets.QAction(MainWindow)
        self.actionExit.setObjectName("actionExit")
        group = QActionGroup(self.menuRename_preference)
        texts = ["actionAuthor_Title_Journal_Year", "Noncash Payment", "Cash on Delivery", "Bank Transfer"]

        try:
            renamepref=pickle.load(open("name.pkl","rb"))
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
        group.triggered.connect(self.onTriggered)
        self.menuTools.addMenu(self.menuRename_preference)
        self.actionAbout = QtWidgets.QAction(MainWindow)
        self.actionAbout.setObjectName("actionAbout")
        self.actionDeveloper = QtWidgets.QAction(MainWindow)
        self.actionDeveloper.setObjectName("actionDeveloper")
        self.actionUser_Guide = QtWidgets.QAction(MainWindow)
        self.actionUser_Guide.setObjectName("actionUser_Guide")
        self.actionStorage_Location = QtWidgets.QAction(MainWindow)
        self.actionStorage_Location.setObjectName("actionStorage_Location")
        self.actionStorage_Location.triggered.connect(self.storagetrigger)
        self.menuFile.addAction(self.actionAdd_from_local_2)
        self.menuFile.addAction(self.actionExit)
        self.menuTools.addAction(self.actionStorage_Location)
        self.menuHelp.addAction(self.actionAbout)
        self.menuHelp.addAction(self.actionDeveloper)
        self.menuHelp.addAction(self.actionUser_Guide)
        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuTools.menuAction())
        self.menubar.addAction(self.menuHelp.menuAction())

        self.retranslateUi(MainWindow)
        self.tab_3.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.groupBox.setTitle(_translate("MainWindow", "Resource browser"))
        self.inputurl.setPlaceholderText(_translate("MainWindow", "Enter URL/DOI/PMID"))
        self.downloadbutton.setText(_translate("MainWindow", "Download"))
        self.label_2.setText(_translate("MainWindow", "Filter by"))
        self.filelist.headerItem().setText(0, _translate("MainWindow", "Author"))
        self.filelist.headerItem().setText(1, _translate("MainWindow", "Title"))
        self.filelist.headerItem().setText(2, _translate("MainWindow", "Journal"))
        self.filelist.headerItem().setText(3, _translate("MainWindow", "Year"))

        self.tab_3.setTabText(self.tab_3.indexOf(self.tab), _translate("MainWindow", "Tab 1"))
        self.tab_3.setTabText(self.tab_3.indexOf(self.tab_2), _translate("MainWindow", "Tab 2"))
        self.menuFile.setTitle(_translate("MainWindow", "File"))
        self.menuTools.setTitle(_translate("MainWindow", "Tools"))
        self.menuRename_preference.setToolTip(_translate("MainWindow", "Select the order for renaming PDF"))
        self.menuRename_preference.setTitle(_translate("MainWindow", "Rename preference"))
        self.menuHelp.setTitle(_translate("MainWindow", "Help"))
        self.toolBar.setWindowTitle(_translate("MainWindow", "toolBar"))
        self.actionAdd_from_local.setText(_translate("MainWindow", "Add from local"))
        self.actionAdd_from_local_2.setText(_translate("MainWindow", "Add from local"))
        self.actionExit.setText(_translate("MainWindow", "Exit"))

        self.actionAbout.setText(_translate("MainWindow", "About"))
        self.actionDeveloper.setText(_translate("MainWindow", "Developer"))
        self.actionUser_Guide.setText(_translate("MainWindow", "User Guide"))
        self.actionStorage_Location.setText(_translate("MainWindow", "Storage Location"))

    def onTriggered(self, action):
        renamepref=action.text()
        pickle.dump(renamepref, open("name.pkl", "wb"))
        print(action.text())
    def storagetrigger(self):
        self.path = QFileDialog.getExistingDirectory(None, "Open Directory", "C:/",
                                                           QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks)
        pickle.dump(self.path, open("Datafolderpath.pkl", "wb"))
        print(self.path)
    def scidexe(self):
        # This is executed when the button is pressed
        print('Input text:' + self.inputurl.text())
        from sciscrap import scrap
        scrap(self.inputurl.text())

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
