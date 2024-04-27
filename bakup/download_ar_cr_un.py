from PyQt5.QtCore import QThread, pyqtSignal
import requests
from pdfrw import PdfReader
from crossref.restful import Works,Etiquette
from habanero import Crossref
import sys
import re
import arxiv
from bs4 import BeautifulSoup
import os
import urllib.request, json
from urllib.parse import urljoin
from win32com.shell import shell, shellcon
import doiextractor
from unpywall import Unpywall
from unpywall.utils import UnpywallCredentials
import arxivtobib
import textwrap

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
        link=self.link.lstrip()
        self.countChanged.emit(5)
        self.statusChanged.emit('Starting..')
        if link.startswith('https://arxiv.org'):
            self.countChanged.emit(15)
            self.statusChanged.emit('Query:arxiv id')
            print('toarxiv1')
            for i in range(len(link)-1):
                if link[i]=='/':
                    j=i
                else:
                    pass
            link=link[j+1:]
            print(link)
            self.arxiv_download(link)
        elif link.startswith('arxiv'):
            self.countChanged.emit(15)
            self.statusChanged.emit('Query:arxiv id')
            print('toarxiv2')
            link=link[6:]
            self.arxiv_download(link)
        elif link.startswith('https://dx.doi.org') or link.startswith('https://doi.org'):
            self.countChanged.emit(15)
            self.statusChanged.emit('Query:DOI')
            print('doi')
            self.unpywall(link,None)
        elif link[:5]!='https':
            if link[:3]=='10.':
                self.countChanged.emit(15)
                self.statusChanged.emit('Query:DOI')
                print('doi1')
                self.unpywall(link,None)
            elif link[:4]=='Doi:' or link[:4]=='doi:':
                self.countChanged.emit(15)
                self.statusChanged.emit('Query:DOI')
                print(link[4:])
                self.unpywall(link,None)
            elif link[:5]=='doi :' or link[:5]=='Doi :':
                self.countChanged.emit(15)
                self.statusChanged.emit('Query:DOI')
                print(link[5:])
                self.unpywall(link,None)
            else:
                print('check for title')
                self.countChanged.emit(15)
                self.statusChanged.emit('Query:Title')
                doi,title=doiextractor.titletodoi(link)
                print(doi)
                if doi!=None:
                    self.unpywall(doi,title)
                else:
                    self.core(link)
        else:
            print('urltodoi')
            self.countChanged.emit(15)
            self.statusChanged.emit('Query:URL')
            doi,title=doiextractor.urltotitle(link)
            print(doi)
            if doi!=None:
                self.unpywall(doi,None)


    def arxiv_download(self,ids):
        self.countChanged.emit(50)
        self.statusChanged.emit('Searching in arxiv..')
        paper = arxiv.query(id_list=[ids])[0]
        pdfurl=paper['pdf_url']
        title=paper['title']
        self.atitle=title
        doi=paper['doi']
        paper2 = {"pdf_url": pdfurl,"title":title}
        if doi!=None and doi!='':
            self.countChanged.emit(55)
            self.statusChanged.emit('Downloading..')
            arxiv.download(paper,dirpath=self.path,slugify=self.customslug)
            self.senddoi.emit(doi)
            self.sendfile.emit(self.path+'/test.pdf')
        else:
            self.countChanged.emit(55)
            self.statusChanged.emit('Downloading..')
            arxiv.download(paper,dirpath=self.path,slugify=self.customslug1)
            self.countChanged.emit(85)
            self.statusChanged.emit('Getting bibtex file..')
            arxivtobib.main(ids,paths=self.path)
            self.countChanged.emit(100)
            self.statusChanged.emit('Completed')

    def customslug(self,obj):
        a='test'
        return a
    def customslug1(self,obj):
        self.atitle=textwrap.shorten(self.atitle, width=100, placeholder='..')
        return self.atitle

    def unpywall(self,doi,title):
        self.countChanged.emit(25)
        self.statusChanged.emit('Searching Unpaywall database..')
        print('unpywall')
        UnpywallCredentials('nick.haupka@gmail.com')
        try:
            pdf=Unpywall.get_pdf_link(doi=doi)
            req = requests.get(pdf, allow_redirects=True)
            downloadable = 'application/pdf' in req.headers.get(
                'Content-Type') or 'application/pdf;charset=UTF-8' in req.headers.get('Content-Type')
            print(downloadable)
            if downloadable==True:
                self.countChanged.emit(30)
                self.statusChanged.emit('Downloading from Unpaywall..')
                open(self.path+'/test.pdf', 'wb').write(req.content)
                self.senddoi.emit(doi)
                self.sendfile.emit(self.path + '/test.pdf')
            else:
                self.countChanged.emit(30)
                self.statusChanged.emit('Redirecting..')
                if title != None:
                    self.core(title,doi)
                else:
                    title = doiextractor.doitotitle(doi)
                    if title != None or title != '':
                        self.core(title,doi)
                    else:
                        self.countChanged.emit(0)
                        self.statusChanged.emit('Article unavailable!')
                        print('none found')
            #Unpywall.download_pdf_file(doi=doi,filename='test.pdf',filepath=self.path)
        except:
            self.countChanged.emit(30)
            self.statusChanged.emit('Redirecting..')
            if title!=None:
                self.core(title,doi)
            else:
                title=doiextractor.doitotitle(doi)
                if title!=None or title!='':
                    self.core(title,doi)
                else:
                    self.countChanged.emit(0)
                    self.statusChanged.emit('Article unavailable!')
                    print('not available')
    def core(self,title,doi):
        self.countChanged.emit(40)
        self.statusChanged.emit('Searching in Core..')
        print('core')
        urls='https://core.ac.uk:443/api-v2/search/'+urllib.parse.quote(title)+'?page=1&pageSize=10&apiKey=dNpYIhQOiU1BnKsFHLAz73e6CWcDo2lS'
        with urllib.request.urlopen(urls) as url:
            data = json.loads(url.read().decode())
        flag=True
        sent=False
        for i in range(len(data['data'])):
            if flag==True:
                title_t = data['data'][i]['_source']['title']
                if title == title_t:
                    flag=False
                    download = data['data'][i]['_source']['downloadUrl']
                    id_ = data['data'][i]['_source']['id']
                    print(download)
                    print(id_)
                    if download == '' or download == None:
                        download = 'https://core.ac.uk:443/api-v2/articles/get/' + id_ + '/download/pdf?apiKey=dNpYIhQOiU1BnKsFHLAz73e6CWcDo2lS'
                    req = requests.get(download, allow_redirects=True)
                    downloadable = 'application/pdf' in req.headers.get(
                        'Content-Type') or 'application/pdf;charset=UTF-8' in req.headers.get('Content-Type')
                    print(downloadable)
                    if downloadable == True:
                        self.countChanged.emit(45)
                        self.statusChanged.emit('Downloading..')
                        open(self.path + '/test.pdf', 'wb').write(req.content)
                        # doi=doiextractor.titletodoi(title)
                        sent=True
                        self.senddoi.emit(doi)
                        self.sendfile.emit(self.path + '/test.pdf')
                    elif download[:17] == 'https://arxiv.org' or download[:16] == 'http://arxiv.org':
                        for i in range(len(download) - 1):
                            if download[i] == '/':
                                j = i
                            else:
                                pass
                        download = download[j + 1:]
                        print(download)
                        self.countChanged.emit(50)
                        self.statusChanged.emit('Redirecting to arxiv..')
                        sent=True
                        self.arxiv_download(download)

        if sent==False:
            self.countChanged.emit(0)
            self.statusChanged.emit('Article not available..')

