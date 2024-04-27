import requests
from bs4 import BeautifulSoup as bs
from fake_useragent import UserAgent
from habanero import Crossref
from difflib import SequenceMatcher
from crossref.restful import Works, Etiquette

def urltotitle(link):
    ua = UserAgent()
#link=['https://www.nejm.org/doi/full/10.1056/nejme2002387','https://www.ncbi.nlm.nih.gov/pmc/articles/PMC7169770/','https://www.nature.com/articles/s41577-020-0308-3','https://www.ncbi.nlm.nih.gov/pmc/articles/PMC7262788/','https://mpgjournal.mpg.es/index.php/journal/article/view/457','https://ccforum.biomedcentral.com/articles/10.1186/s13054-020-03077-0','https://jlb.onlinelibrary.wiley.com/doi/full/10.1189/jlb.0205074','https://www.nature.com/articles/nbt1003-1137','https://www.tandfonline.com/doi/abs/10.1517/14712598.3.4.655','https://www.nature.com/articles/nrc1566','https://onlinelibrary.wiley.com/doi/abs/10.1002/9783527623327','https://link.springer.com/article/10.1007/s11051-010-0192-z','https://www.sciencedirect.com/science/article/pii/S0167779900015365?casa_token=_pYMaj-ze2wAAAAA:S2nsyA5tY4S7F9TOtD3E6Su16PdDq6BKeKPI1p9IMmq5-ulkMHh-9tAsn9iJJRHOsDAQRDfvDi8','https://www.osti.gov/etdeweb/biblio/7150331','https://www.sciencedirect.com/science/article/pii/S0167779907000881?casa_token=4IED0A3115QAAAAA:96vODivlh_Gaxwyz47yOh9QGxl0H52XO5kuX3S87s3Jv2eFZ6h8XyX-qwwN_9Uq0WlGfPhj9zSI','https://heinonline.org/hol-cgi-bin/get_pdf.cgi?handle=hein.journals/adelrev2&section=8']
    header = {'User-Agent':str(ua.random)}
    r=requests.get(link,headers=header)
    soup = bs(r.content, 'lxml')
    #print(i)
    print(soup.select_one('title').text)
    title_temp=soup.select_one('title').text
    if title_temp.find('|')!=-1:
        k=title_temp.find('|')
        title_temp=title_temp[:k]
    title_temp=title_temp.strip('- ScienceDirect')
    title_temp=title_temp.strip('- Wiley Online Library')
    doi,title=titletodoi(title_temp)
    return doi,title

def titletodoi(title_temp):
        print('titletodoi')
        title_temp1=title_temp
        cr = Crossref()
        x = cr.works(query=title_temp)
        my_etiquette = Etiquette('SciX', '1.0', 'www.scix.in', 'service@scix.in')
        works = Works(my_etiquette)

        doi=None
        flag=True
        for i in range(len(x['message']['items'])):
            if flag==True:
                doi_temp = x['message']['items'][i]['DOI']
                meta = works.doi(doi_temp)
                try:
                    journal = meta['container-title']
                    journal = journal[0]
                    journal = journal.replace('/', '')
                except:
                    journal = None
                try:
                    yr = meta['created']
                    yrs = yr['date-time']
                    year = yrs[:4]
                    year = year.replace('/', '')
                except:
                    year = None
                try:
                    title_temp = title_temp.replace(journal, '')
                    title_temp = title_temp.replace(year, '')
                except:
                    pass
                try:
                    title = x['message']['items'][i]['reference'][0]['article-title']
                except:
                    try:
                        title = x['message']['items'][i]['title']
                    except:
                        title = x['message']['items'][i]['container-title']
                if type(title) is list:
                    title = title[0]
                print(title)
                print(title_temp)
                match = SequenceMatcher(None, title_temp, title)
                matchper = match.ratio() * 100
                if matchper >= 80:
                    print('matched')
                    flag=False
                    doi=doi_temp
        if doi!=None:
            return doi,title
        else:
            return doi,title_temp1
        print(doi)




        
def doitotitle(doi):
    my_etiquette = Etiquette('SciX', '1.0', 'www.scix.in', 'service@scix.in')
    works = Works(my_etiquette)
    meta = works.doi(doi)
    title = meta['title']
    try:
        title = title[0]
        title = title.replace('/', '')
    except:
        pass
    print(title)
    return title
    
    
  





    
        
    
    
