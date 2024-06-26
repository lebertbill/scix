# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'delete.ui'
#
# Created by: PyQt5 UI code generator 5.15.0
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Dialog_delete(object):
    def setupUi(self, Dialog_delete):
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

        self.retranslateUi(Dialog_delete)
        QtCore.QMetaObject.connectSlotsByName(Dialog_delete)

    def retranslateUi(self, Dialog_delete):
        _translate = QtCore.QCoreApplication.translate
        Dialog_delete.setWindowTitle(_translate("Dialog_delete", "Warning"))
        self.label.setText(_translate("Dialog_delete", "Deleting a folder will delete all the files. Wish to continue?"))
        self.deleteb.setText(_translate("Dialog_delete", "Delete"))
        self.cancelb.setText(_translate("Dialog_delete", "Cancel"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Dialog_delete = QtWidgets.QDialog()
    ui = Ui_Dialog_delete()
    ui.setupUi(Dialog_delete)
    Dialog_delete.show()
    sys.exit(app.exec_())
