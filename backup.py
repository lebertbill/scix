# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'backup.ui'
#
# Created by: PyQt5 UI code generator 5.15.0
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_backupDialog(object):
    def setupUi(self, backupDialog):
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

        self.retranslateUi_backup(backupDialog)
        QtCore.QMetaObject.connectSlotsByName(backupDialog)

    def retranslateUi_backup(self, backupDialog):
        _translate = QtCore.QCoreApplication.translate
        backupDialog.setWindowTitle(_translate("backupDialog", "Dialog"))
        self.label.setText(_translate("backupDialog", " Output Folder"))
        self.selectbackup.setText(_translate("backupDialog", "..."))
        self.backup.setText(_translate("backupDialog", "Backup"))
        self.bakclose.setText(_translate("backupDialog", "Close"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    backupDialog = QtWidgets.QDialog()
    ui = Ui_backupDialog()
    ui.setupUi(backupDialog)
    backupDialog.show()
    sys.exit(app.exec_())