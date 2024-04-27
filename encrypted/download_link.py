from PyQt5.QtCore import QThread, pyqtSignal
import requests
from hurry.filesize import size, si
from pdfrw import PdfReader
from pdftitle import get_title_from_file
from crossref.restful import Works,Etiquette
from habanero import Crossref
from difflib import SequenceMatcher
import sys
import re
from win32com.shell import shell, shellcon

class Externalthread(QThread):
    """
    Runs a counter thread.
    """
    countChanged = pyqtSignal(int)
    statusChanged=pyqtSignal(str)
    senddoi=pyqtSignal(str)
    sendfile=pyqtSignal(str)
    def __init__(self,link,path):
        super(Externalthread, self).__init__()
        self.link=link
        self.path=path
        docpath = shell.SHGetFolderPath(0, shellcon.CSIDL_PERSONAL, None, 0)
        self.docpath = docpath + '\SciX'
    def show_exception_and_exits(self,exc_type, exc_value, tb):
        import traceback
        print(self.docpath)
        a = traceback.format_tb(tb)
        print(''.join(a))
        f = open(self.docpath + '\ERROR LOG.txt', 'a')
        f.write(str(exc_value))
        f.write("\n")
        f.write("Details:")
        f.write(''.join(a))
        f.write("\n")
        f.write("\n")
        f.close()
        count = 0
        self.countChanged.emit(count)
        self.statusChanged.emit('Error occured!')
    def run(self):
        sys.excepthook = self.show_exception_and_exits
        self.statusChanged.emit('Initializing...')
        flagtitle=True
        print(self.link)
        count = 10
        self.countChanged.emit(count)
        self.statusChanged.emit('Downloading your file...')
        try:
            req = requests.get(self.link, allow_redirects=True)
            downloadable = 'attachment' in req.headers.get(
                    'Content-Disposition') or 'application/pdf' in req.headers.get(
                    'Content-Type') or 'application/pdf;charset=UTF-8' in req.headers.get('Content-Type')
            count = 15
            self.countChanged.emit(count)
            self.statusChanged.emit('Please wait...')
        except:
            try:
                if self.link.endswith('.pdf') or self.link.endswith('.PDF'):
                    downloadable = True
                    count = 15
                    self.countChanged.emit(count)
                    self.statusChanged.emit('Please wait...')
                else:
                    count = 15
                    self.countChanged.emit(count)
                    self.statusChanged.emit('Please wait...')
                    downloadable = False
            except:
                downloadable=False
        if downloadable==True:
            req = requests.get(self.link, allow_redirects=True)
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
            try:
                if 'Content-Disposition' in req.headers.keys():
                    filname = re.findall("filename=(.+)", req.headers["Content-Disposition"])[0]
                else:
                    filname = self.link.split('/')[-1]
            except:
                filname='test.pdf'
            filname=filname.strip('""')
            if filname.endswith('.pdf') or filname.endswith('.PDF'):
                print('if')
                pass
            else:
                filname=filname+".pdf"
            pdfl = self.path + '/'+filname
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
                print(doi)
                count = 50
                self.countChanged.emit(count)
                self.senddoi.emit(doi)
                self.sendfile.emit(pdfl)
            else:
                try:
                    count = 45
                    self.countChanged.emit(count)
                    self.statusChanged.emit("Fetching DOI...")
                    Title = read.Info.Title
                    if Title != None:
                        Title = Title.strip('()')
                        if Title[:4] == 'doi:' and len(Title) > 8:
                            doi=Title[4:]
                        elif len(Title) > 6:
                            title_temp = Title
                            print(title_temp)
                            cr = Crossref()
                            x = cr.works(query=title_temp)
                            doi = x['message']['items'][0]['DOI']
                            works = Works()
                            meta = works.doi(doi)
                            title = meta['title']
                            title = title[0]
                            title = title.replace('/', '')
                            print(title)
                            if title_temp == title:
                                print('st')
                                doi=doi
                                count = 50
                                self.countChanged.emit(count)
                                self.senddoi.emit(doi)
                                self.sendfile.emit(pdfl)
                            else:
                                match = SequenceMatcher(None, title_temp, title)
                                matchper = match.ratio() * 100
                                if matchper >= 90:
                                    doi=doi
                                    count = 50
                                    self.countChanged.emit(count)
                                    self.senddoi.emit(doi)
                                    self.sendfile.emit(pdfl)
                                else:
                                    flagtitle = False
                        else:
                            flagtitle = False
                    else:
                        flagtitle = False
                except:
                    flagtitle = False

            if flagtitle == False:
                try:
                    title_temp = get_title_from_file(pdfl)
                    print(title_temp)
                    cr = Crossref()
                    x = cr.works(query=title_temp)
                    doi = x['message']['items'][0]['DOI']
                    my_etiquette = Etiquette('SciX', '1.02b', 'www.scix.in', 'service@scix.in')
                    works = Works(my_etiquette)
                    meta = works.doi(doi)
                    title = meta['title']
                    title = title[0]
                    title = title.replace('/', '')
                    print(title)
                    if title_temp == title:
                        print('st')
                        doi = doi
                        count = 50
                        self.countChanged.emit(count)
                        self.senddoi.emit(doi)
                        self.sendfile.emit(pdfl)
                    else:
                        print('nt')
                        match = SequenceMatcher(None, title_temp, title)
                        matchper = match.ratio() * 100
                        if matchper >= 90:
                            print('matched')
                            doi = doi
                            count = 50
                            self.countChanged.emit(count)
                            self.senddoi.emit(doi)
                            self.sendfile.emit(pdfl)
                        else:
                            count = 100
                            self.countChanged.emit(count)
                            self.statusChanged.emit("Update DOI manually.(File:%s)"%filname)
                except:
                    count = 100
                    self.countChanged.emit(count)
                    self.statusChanged.emit("Update DOI manually.(File:%s)"%filname)
        else:
            count = 0
            self.countChanged.emit(count)
            self.statusChanged.emit('Error. Link not downloadable')