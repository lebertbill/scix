from PyQt5.QtCore import QThread, pyqtSignal
import requests
from hurry.filesize import size, si
from pdfrw import PdfReader

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

    def run(self):
        print(self.link)
        self.statusChanged.emit('Downloading your file...')
        try:
            req = requests.get(self.link, allow_redirects=True)
            downloadable = 'attachment' in req.headers.get(
                'Content-Disposition') or 'application/pdf' in req.headers.get(
                'Content-Type') or 'application/pdf;charset=UTF-8' in req.headers.get('Content-Type')
        except:
            downloadable=False
        if downloadable==True:
            count = 20
            self.countChanged.emit(count)
            self.statusChanged.emit('Downloading your file...')
            try:
                byte = req.headers['Content-Length']
                print('siz')
                siz = size(int(byte), system=si)
            except:
                siz = ''
            self.statusChanged.emit('Downloading pdf (size:%s)' % siz)
            count = 40
            self.countChanged.emit(count)
            pdfl = self.path + '/test.pdf'
            open(pdfl, 'wb').write(req.content)
            read = PdfReader(pdfl)
            doi = ''
            try:
                doi = read.Info.doi.strip('()')
            except:
                try:
                    string = read.Info.Subject.strip('()')
                    keyword = 'doi:'
                    before_keyword, keyword, after_keyword = string.partition(keyword)
                    doi = after_keyword
                except:
                    pass

            if doi!='':
                count = 50
                self.countChanged.emit(count)
                self.senddoi.emit(doi)
                self.sendfile.emit(pdfl)
            else:
                count = 0
                self.countChanged.emit(count)
                self.statusChanged.emit('Could not parse pdf')
        else:
            count = 0
            self.countChanged.emit(count)
            self.statusChanged.emit('Error. Link not downloadable')