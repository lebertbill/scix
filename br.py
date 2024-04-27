import sys
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWebKit import *
from PyQt5.QtNetwork import *
from PyQt5.QtGui import QGridLayout, QLineEdit, QWidget

class UrlInput(QLineEdit):

        def __init__(self, browser):

            super(UrlInput, self).__init__()
            self.browser = browser
            self.returnPressed.connect(self._return_pressed)

        def _return_pressed(self):
                browser.setHtml('Loading...')
                data = self.text()
                url = QUrl(data)
                browser.load(url)

if __name__ == "__main__":
        app = QApplication(sys.argv)

        grid = QGridLayout()
        browser = QWebView()
        url_input = UrlInput(browser)
        grid.addWidget(url_input, 1, 0)
        grid.addWidget(browser, 2, 0)
        main_frame = QWidget()
        main_frame.setLayout(grid)
        main_frame.show()
        sys.exit(app.exec_())