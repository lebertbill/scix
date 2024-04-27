# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'style.ui'
#
# Created by: PyQt5 UI code generator 5.15.0
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Dialog_style(object):
    def setupUi(self, Dialog_style):
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

        self.retranslateUi(Dialog_style)
        QtCore.QMetaObject.connectSlotsByName(Dialog_style)

    def retranslateUi(self, Dialog_style):
        _translate = QtCore.QCoreApplication.translate
        Dialog_style.setWindowTitle(_translate("Dialog_style", "Select Style"))
        self.stylecombo.setToolTip(_translate("Dialog_style", "Select the style"))
        self.label.setText(_translate("Dialog_style", "Formatting style"))
        self.styleapply.setToolTip(_translate("Dialog_style", "Set the selected style"))
        self.styleapply.setText(_translate("Dialog_style", "Apply"))
        self.stylecancel.setToolTip(_translate("Dialog_style", "Cancel"))
        self.stylecancel.setText(_translate("Dialog_style", "Cancel"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Dialog_style = QtWidgets.QDialog()
    ui = Ui_Dialog_style()
    ui.setupUi(Dialog_style)
    Dialog_style.show()
    sys.exit(app.exec_())
