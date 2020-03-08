from .models import *

import math
from datetime import datetime

from bs4 import BeautifulSoup
import time
import pandas as pd

import urllib
import urllib.request
import urllib.parse
import requests
import json
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse

# Create your views here.

def search_engine(user_input) :  ## 네이버 쇼핑 크롤링 
    query_txt = urllib.parse.quote(user_input)

    url = requests.get('https://search.shopping.naver.com/search/all.nhn?&pagingIndex=1&pagingSize=40&productSet=model&viewType=list&sort=rel&frm=NVSHMDL&query=%s' %query_txt)
    time.sleep(0.5)
    
    full_html = url.text
    
    mask_num = 0
    prod_name = []
    prod_price = []
    prod_img = []
    prod_url=[]

    soup = BeautifulSoup(full_html, 'lxml')
    content_list = soup.find('ul',class_='goods_list').find_all('li',class_='_model_list _itemSection')

    for i in content_list :

        name = i.find('div', class_='tit').get_text().strip()
        prod_name.append(name)
                    
        price_str = i.find('span',class_='num _price_reload').get_text()
        price_int = int(price_str.split("원")[0].replace(",","")) 
        prod_price.append(price_int)

        image = i.find('img',class_='_productLazyImg')['data-original']
        prod_img.append(image)

        url = i.find('div', class_="tit").find("a")['href']
        prod_url.append(url)

    
        mask_num += 1
        
        if mask_num >= 10  : 
            mask_danawa = pd.DataFrame()  # 데이터프레임으로 변환
            mask_danawa["제품명"] = prod_name
            mask_danawa["가격"] = prod_price
            mask_danawa["이미지"] = prod_img
            mask_danawa["URL"] = prod_url
            mask_danawa = mask_danawa.sort_values(["가격"])  ## 가격 순으로 정렬한다
            mask_danawa = mask_danawa.reset_index()   ## 행 번호를 리셋시킨다
            return mask_danawa

def build_url(city) :  ## 미세먼지 API 요청 
    TOKEN = '사용자의 API KEY '  ## 보안 문제 상 쓰지 않았습니다
    return f'http://openapi.airkorea.or.kr/openapi/services/rest/ArpltnInforInqireSvc/getMsrstnAcctoRltmMesureDnsty?stationName={city}&dataTerm=month&pageNo=1&numOfRows=10&ServiceKey={TOKEN}&ver=1.3&_returnType=json'

def request_data(url) :
    response = requests.get(url)
    text_data = response.text
    return text_data

def search_news() :  ## 네이버 뉴스 
    news_url = requests.get('https://search.naver.com/search.naver?where=news&sm=tab_jum&query=KF94+%2B%ED%8C%90%EB%A7%A4+-%EC%83%81%EC%88%A0+-%EA%B8%B0%EB%B6%80+-%EC%A4%91%EA%B5%AD+-%EC%88%98%ED%98%88')
    time.sleep(0.5)

    full_html = news_url.text

    soup = BeautifulSoup(full_html, 'lxml')

    news_num = 0
    news_name = []
    news_img = []
    news_url=[]
    news_date=[]

    content_list = soup.find('ul',class_='type01').find_all('li')

    for i in content_list :

        try :
            name = i.find('a',class_='_sp_each_title').get_text()
            news_name.append(name)
        except AttributeError :
            continue
        
        try :
            url = i.find('a',class_=' _sp_each_title')['href']
            news_url.append(url)
        except :
            url = i.find('a')['href']
            news_url.append(url)

        try :
            image = i.find('img')['src']
            news_img.append(image)
        except :
            news_img.append("https://4game.co.kr/images/banner_left_blank.png")

        raw_date = i.find("dd", class_="txt_inline").get_text()
        list_date = raw_date.split(" ")
        date = list_date[2] + " " + list_date[3]
        news_date.append(date)
        
        news_num += 1
        
        if news_num >= 5  : 
            news_DB = pd.DataFrame()  # 데이터프레임으로 변환
            news_DB["제목"] = news_name
            news_DB["이미지"] = news_img
            news_DB["URL"] = news_url
            news_DB["날짜"] = news_date
            return news_DB


        
@csrf_exempt
def start_engine(request) :                                           # POST 형식이었을 때의 반환
    if request.method == "POST" :
        json_str = ((request.body).decode('utf-8'))
        received_json_data = json.loads(json_str)
        datacontent = received_json_data['userRequest']['utterance'].split()[0]
        print(received_json_data['action']['params'])
        parameter = received_json_data['action']['params']
        parameter_list = list(parameter.keys())
        new_DB = mask_DB(content = received_json_data['action']['params'])
        new_DB.save()
        new_DB_time = mask_DB(content = datetime.now())
        new_DB_time.save()
        
        if parameter_list[0] == "mask_category" :
            par = received_json_data['action']['params']['mask_category']
            sorted_mask_danawa = search_engine(par) ## 함수 실행
            url = "http://www.enuri.com/search.jsp?keyword=%s" %par
                
            return JsonResponse({  ## 카카오 챗봇 json 응답포맷에 맞게 반환
          "version": "2.0",
          "template": {
            "outputs": [
              {
                "listCard": {
                  "header": {
                    "title": par,
                    "imageUrl": "https://postfiles.pstatic.net/MjAyMDAyMjRfNTAg/MDAxNTgyNTQ0NTYwNDgy.aq5sHEZxPsqkrF2tZ_Hqmbg60fk9rOP7RTxGibZOB0og.ClT2TUcxqtiFco_1W3lycojEIc57TB2-p-Q3r-lXlf8g.JPEG.samlee0605/watercolour-1325656_1920.jpg?type=w773"
                  },
                  "items": [
                    {
                      "title": sorted_mask_danawa["제품명"][0],
                      "description": str(sorted_mask_danawa["가격"][0]) + "원",
                      "imageUrl": sorted_mask_danawa["이미지"][0],
                      "link": {
                        "web": sorted_mask_danawa["URL"][0]
                      }
                    },
                    {
                      "title": sorted_mask_danawa["제품명"][1],
                      "description": str(sorted_mask_danawa["가격"][1]) + "원",
                      "imageUrl": sorted_mask_danawa["이미지"][1],
                      "link": {
                        "web": sorted_mask_danawa["URL"][1]
                      }
                    },
                    {
                      "title": sorted_mask_danawa["제품명"][2],
                      "description": str(sorted_mask_danawa["가격"][2]) + "원",
                      "imageUrl": sorted_mask_danawa["이미지"][2],
                      "link": {
                        "web": sorted_mask_danawa["URL"][2]
                      }
                    },
                    {
                      "title": sorted_mask_danawa["제품명"][3],
                      "description": str(sorted_mask_danawa["가격"][3]) + "원",
                      "imageUrl": sorted_mask_danawa["이미지"][3],
                      "link": {
                        "web": sorted_mask_danawa["URL"][3]
                      }
                    },
                    {
                      "title": sorted_mask_danawa["제품명"][4],
                      "description": str(sorted_mask_danawa["가격"][4]) + "원",
                      "imageUrl": sorted_mask_danawa["이미지"][4],
                      "link": {
                        "web": sorted_mask_danawa["URL"][4]
                      }
                    }
                  ],
                  "buttons": [
                    {
                      "label": "메뉴로 돌아가기",
                      "action": "block",
                      "blockId": "5e4e20748192ac0001371dfd"
                    },
                    {
                      "label": "더 알아보기",
                      "action": "webLink",
                      "webLinkUrl": url
                    }
                  ]
                }
              }
            ]
          }
        }
)

        elif parameter_list[0] == "news_category" :
            par = received_json_data['action']['params']['news_category'].split()[0]
            news_DB = search_news()
            return JsonResponse({
      "version": "2.0",
      "template": {
        "outputs": [
          {
            "listCard": {
              "header": {
                "title": par,
                "imageUrl": "https://postfiles.pstatic.net/MjAyMDAyMjRfNTAg/MDAxNTgyNTQ0NTYwNDgy.aq5sHEZxPsqkrF2tZ_Hqmbg60fk9rOP7RTxGibZOB0og.ClT2TUcxqtiFco_1W3lycojEIc57TB2-p-Q3r-lXlf8g.JPEG.samlee0605/watercolour-1325656_1920.jpg?type=w773"
              },
              "items": [
                {
                  "title": news_DB["제목"][0],
                  "description": news_DB["날짜"][0],
                  "imageUrl": news_DB["이미지"][0],
                  "link": {
                    "web": news_DB["URL"][0]
                  }
                },
                {
                  "title": news_DB["제목"][1],
                  "description": news_DB["날짜"][1],
                  "imageUrl": news_DB["이미지"][1],
                  "link": {
                    "web": news_DB["URL"][1]
                  }
                },
                {
                  "title": news_DB["제목"][2],
                  "description": news_DB["날짜"][2], 
                  "imageUrl": news_DB["이미지"][2],
                  "link": {
                    "web": news_DB["URL"][2]
                  }
                },
                {
                  "title": news_DB["제목"][3],
                  "description": news_DB["날짜"][3],
                  "imageUrl": news_DB["이미지"][3],
                  "link": {
                    "web": news_DB["URL"][3]
                  }
                },
                {
                  "title": news_DB["제목"][4],
                  "description": news_DB["날짜"][4],
                  "imageUrl": news_DB["이미지"][4],
                  "link": {
                    "web": news_DB["URL"][4]
                  }
                }
              ],
              "buttons": [
                {
                  "label": "메뉴 창으로 돌아가기",
                  "action": "block",
                  "blockId": "5e4e20748192ac0001371dfd"
                }
              ]
            }
          }
        ]
      }
    }
) 
        elif parameter_list[0] == "syslocation" :
            city_name = received_json_data['action']['params']['syslocation'].split()[0]      
            dust_time = json.loads(request_data(build_url(city_name)))['list'][0]['dataTime']                      # 측정시간
            dust_PM10 = json.loads(request_data(build_url(city_name)))['list'][0]['pm10Value']                     # 미세먼지 농도
            dust_PM25 = json.loads(request_data(build_url(city_name)))['list'][0]['pm25Value']                     # 초미세먼지 농도
            dust_PM10_grade = json.loads(request_data(build_url(city_name)))['list'][0]['pm10Grade1h']             # 미세먼지 1시간 등급
            dust_PM25_grade = json.loads(request_data(build_url(city_name)))['list'][0]['pm25Grade1h']             # 초미세먼지 1시간 등급
            
            return JsonResponse({
        "version": "2.0",
        "template": {
            "outputs": [
                {
                    "simpleText": {
                        "text": city_name + "의 미세먼지 농도는 " + dust_time + " 기준 " + str(dust_PM10) + " 입니다! 초미세먼지는 " + str(dust_PM25) + " 입니다!"
                    }
                }
            ],
        "quickReplies": [
        {
        "label": "메뉴 창",
        "action": "block",
        "blockId": "5e4e20748192ac0001371dfd"
                }
            ]
        }
    }
)
        
                
    else : return HttpResponse("Success")                      # GET 형식이었을 때의 반환         
