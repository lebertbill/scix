from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QUrl
from PyQt5.QtWidgets import *
from PyQt5.QtWebEngineWidgets import *
def browser(self):
    self.tab_2 = QWebEngineView()
    self.tab_2.setObjectName("tab_2")
    self.tab_2.setUrl(QUrl("http://www.google.com"))