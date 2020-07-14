# -*- coding: utf-8 -*-
"""isolezwelesixhosa_scrap_links.ipynb
Code for scrapping news text from https://www.isolezwelesixhosa.co.za

Author: Jesujoba Alabi
"""

import requests
from bs4 import BeautifulSoup
from urllib import request
from urllib.request import Request, urlopen
agent = {"User-Agent":'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36'}

#define new category aside from the home page
category = ['iindaba','ezemidlalo','ezoyolo','izimvo']
#get the number of `featured` pages each of the categories have
def get_no_featuredpages(catgory):
  url = "https://www.isolezwelesixhosa.co.za/"+catgory+"?filter_by=featured"
  reqs = requests.get(url, headers=agent)
  soup = BeautifulSoup(reqs.content, 'lxml')
  res = soup.find('span',{'class':'pages'})
  return int(res.text.split()[-1])

#scrap links from the different categories 
def scrap_link(catgory, catgory_size):
  urls = []
  print("Getting the URL from the category : ", catgory, " (featured) with ", catgory_size, " pages . " )
  for p in range(catgory_size):
    url = 'https://www.isolezwelesixhosa.co.za/'+catgory+'/page/'+str(p+1)+'?filter_by=featured'
    #print(url)
    reqs = requests.get(url, headers=agent)
    soup = BeautifulSoup(reqs.content, 'lxml')
    res = soup.find_all('div',{'class':'td-module-thumb'})#.find_all("a", href=True)
    #print(res)
    urls.extend([t.a['href'] for t in res])
  #return all the news article links from the category
  return urls

#scrap the articles with links in the `urls` variable
def getSoup(links):
  print("getting soup objects for all the links ... ")
  soupx = []
  cnt=0
  for url in links: 
    page_request = request.Request(url, headers=agent)
    page = request.urlopen(page_request)
    #response = requests.get(page_url)
    #print(page.getcode())
    soup = BeautifulSoup(page, 'html.parser')
    soupx.append(soup)
    cnt = cnt + 1
    progresse = (cnt/len(links) * 100) 
    if progresse  % 10 == 0:
      print ("Got ", progresse, "% of soup objects")
  print("got the soup object for all the links ... ")
  return soupx

def getcontent(soupx):
  print("scrapping the articles ... ")
  cnt=0;
  title=[];time=[]; texts=[]
  for soups in soupx:
    cnt=cnt+1
    if soups.find("h1", {"class":"entry-title"})!= None:
      title.append(soups.find("h1", {"class":"entry-title"}).text.replace("\t","").replace("\n",""))
    else:
      title.append("")
    if soups.find("time", {"class":"entry-date updated td-module-date"})!= None:
      time.append(soups.find("time", {"class":"entry-date updated td-module-date"}).text.replace("\t","").replace("\n",""))
    else:
      time.append("")
  
    if soups.find("div", {"class":"td-post-content"})!=None:
      result = soups.find("div", {"class":"td-post-content"}).findAll('p')
      txtstring=""
      for x in result:
      #print (x.text)
        txtstring+=x.text.replace(u'\xa0', u' ').replace('\n'," ")+" \n"
      texts.append(txtstring.strip())
    else:
      texts.append("") 

    progresse = (cnt/len(soupx) * 100) 
    if progresse  % 10 == 0:
      print ("Scrapped ", progresse, "% of the articles")

  return title,time,texts

cat_len = [get_no_featuredpages(cat) for cat in category]
print("Got the following size for each category = ", cat_len)
urls = set([scrap_link(category[i], cat_len[i]) for i in range(len(category))][0])

soups = getSoup(list(urls))
title,time,texts = getcontent(soups)
#create a dictionarty
import pandas as pd
d = {'Date':time,'Title':title,'Text':texts}
df = pd.DataFrame(d)

print(df)

#write the dataframe to file
df.to_csv(r'xhosa_news.csv')

