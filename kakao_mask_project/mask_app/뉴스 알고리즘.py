import json
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse

from bs4 import BeautifulSoup
from selenium import webdriver
import time
import pandas as pd
from pandas import DataFrame, Series

import urllib
import urllib.request
import urllib.parse
import requests



# Create your views here.



def search_news() :
    news_url = requests.get('https://search.naver.com/search.naver?where=news&sm=tab_jum&query=kf94+-%EB%8C%80%EA%B5%AC+-%EA%B8%B0%EB%B6%80+-%EB%A7%A4%EC%A7%84+-%EC%82%AC%EC%9E%AC%EA%B8%B0+-%EB%B6%80%EC%82%B0+-%EC%8B%A0%EC%B2%9C%EC%A7%80+-%EA%B5%90%ED%9A%8C+-%ED%9B%84%EC%9B%90+-%EC%82%AC%EB%A7%9D')
    time.sleep(0.5)

    full_html = news_url.text

    soup = BeautifulSoup(full_html, 'lxml')

    news_num = 0
    news_name = []
    news_img = []
    news_url=[]

    content_list = soup.find('ul',class_='type01').find_all('li')

    for i in content_list :

        try :
            name = i.find('a',class_='_sp_each_title').get_text()
            news_name.append(name)
        except AttributeError :
            continue

        url = i.find('a',class_='sp_thmb thmb80')['href']
        news_url.append(url)

        image = i.find('img')['src']
        news_img.append(image)

        news_num += 1
        
        if news_num >= 5  : 
            news_DF = pd.DataFrame()  # 데이터프레임으로 변환
            news_DF["제목"] = news_name
            news_DF["이미지"] = news_img
            news_DF["URL"] = news_url
            return news_DF

print(search_news())