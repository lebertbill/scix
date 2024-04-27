from PyQt5 import QtWidgets, uic, QtCore, QtGui
import sys
from bs4 import BeautifulSoup
import requests
from urllib.parse import urlparse
from urllib.request import urljoin
import re
from crossref.restful import Works


class Ui_Dialog(QtWidgets.QDialog):
    def __init__(self):
        super(Ui_Dialog, self).__init__()
        uic.loadUi('progressqdialog.ui', self)
        #self.bar = self.findChild(QtWidgets.QProgressBar, 'progressbar')
        #self.bar.setProperty("value",50)
        self.progressBar.setProperty("value", 0 )
        self.show()

    def scrap(link):
        URL = 'https://sci-hub.tw/'
        sreq = requests.Session()

        soup = BeautifulSoup(sreq.get(URL).content, features="html5lib")

        form = soup.find('form')
        print(form)
        fields = form.findAll('input')
        print(fields)
        formdata = dict((field.get('name'), field.get('value')) for field in fields)
        formdata['request'] = link
        posturl = urljoin(URL, form['action'])
        print(posturl)
        res = sreq.post(posturl, data=formdata)
        soups = BeautifulSoup(res.text, features="html5lib")
        src = soups.find('iframe')
        src = src['src']
        pattern = re.compile(r"var doi = '(.*?)';$", re.MULTILINE | re.DOTALL)
        script = soups.find("script", text=pattern)
        doi = pattern.search(script.text).group(1)

        works = Works()
        meta = works.doi(doi)

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
        print(journal)
        print(author)
        print(year)
        print(title)


app = QtWidgets.QApplication(sys.argv)
Dialog=QtWidgets.QDialog()
ui = Ui_Dialog()
ui.show()
#sys.exit(app.exec_())
app.exec_()
