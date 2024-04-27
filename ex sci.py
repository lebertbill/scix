import sys
from PyQt5.QtCore import QThread, pyqtSignal
from bs4 import BeautifulSoup
import requests
from win32com.shell import shell, shellcon
from urllib.request import urljoin, urlopen, Request
import re
from hurry.filesize import size, si
class Externalthread(QThread):
    """
    Runs a counter thread.
    """
    countChanged = pyqtSignal(int)
    statusChanged=pyqtSignal(str)
    senddoi=pyqtSignal(str)
    sendfile=pyqtSignal(str)
    def __init__(self,link,path):
        self.link=link
        self.path=path
        super(Externalthread, self).__init__()
        sys.excepthook = self.show_exception_and_exits
        global docpath
        docpath = shell.SHGetFolderPath(0, shellcon.CSIDL_PERSONAL, None, 0)
        docpath = docpath + '\SciX'
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
       # downloadstatus.setText("ERROR:"+str(exc_value))
      #  window.errorstatus(error=str(exc_value))

    def run(self):

       sys.excepthook = self.show_exception_and_exits
       self.statusChanged.emit('Searching the web')
       count = 0
       self.countChanged.emit(count)
       URL = 'https://sci-hub.tw/'
       sreq = requests.Session()
       count = 20
       self.countChanged.emit(count)
       soup = BeautifulSoup(sreq.get(URL).content, features="html5lib")
       form = soup.find('form')
       print(form)
       fields = form.findAll('input')
       print(fields)
       self.statusChanged.emit('Searching the web...')
       count = 30
       self.countChanged.emit(count)
       formdata = dict((field.get('name'), field.get('value')) for field in fields)
       formdata['request'] = self.link
       posturl = urljoin(URL, form['action'])
       print(posturl)
       self.statusChanged.emit('Fetching the url...')
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
       self.statusChanged.emit('Please wait...')
       try:
           req = Request(src, method='HEAD')
           f = urlopen(req)
           print('f')
           byte = f.headers['Content-Length']
           print('siz')
           siz = size(int(byte), system=si)
       except:
           siz = ''
       self.statusChanged.emit('Downloading pdf (size:%s)'%siz)
       r = requests.get(src, allow_redirects=True)
       pdfl = self.path + '/test.pdf'
       print(pdfl)
       open(pdfl, 'wb').write(r.content)
       self.statusChanged.emit('Download successful')
       doi=None
       count = 60
       self.countChanged.emit(count)
       pattern = re.compile(r"var doi = '(.*?)';$", re.MULTILINE | re.DOTALL)
       script = soups.find("script", text=pattern)
       self.statusChanged.emit('Fetching DOI...')
       doi = pattern.search(script.text).group(1)
       count = 65
       self.countChanged.emit(count)
       print(doi)
       self.statusChanged.emit('DOI:%s'%doi)
       self.senddoi.emit(doi)
       self.sendfile.emit(pdfl)

