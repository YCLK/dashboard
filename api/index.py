from flask import Flask
from flask import render_template
from flask import request            #브라우저의 요청을 처리하기 위한 클래스
from flask import redirect            #인자로 전달된 주소(라우트) 호출
from flask_pymongo import PyMongo
import requests
from bs4 import BeautifulSoup
from datetime import datetime

from bson.objectid import ObjectId


#급식
def getMeal() :
    
    date = datetime.today().strftime("%Y%m%d")
    response = requests.get("https://open.neis.go.kr/hub/mealServiceDietInfo?KEY=417cfd38cd41410091cd4bb11ee814d2&ATPT_OFCDC_SC_CODE=D10&SD_SCHUL_CODE=7240394&MLSV_YMD="+date)
    
    try :
        menuList = BeautifulSoup(response.text, 'html.parser').find("ddish_nm").text.split('<br/>')
        menuList2 = [i.split('(')[0] for i in menuList]
        menuList2.insert(0, date)
    except :
        menuList2 = ['급식 없음']
    
    return menuList2


#날씨
def getWeather() :
    
    html = requests.get('https://search.naver.com/search.naver?query=현풍읍날씨')
    #웹페이지 요청을 하는 코드
    
    soup = BeautifulSoup(html.text, 'html.parser')
    
    loc = soup.find('h2', {'class':'title'} ).text
    temp = soup.find('div', {'class':'temperature_text'} ).text[6:]
    wea = soup.find('span', {'class':'weather before_slash'} ).text
    
    return [loc, temp, wea]


#뉴스
def getNews() :
    
    html = requests.get('https://news.naver.com/section/105')
    #웹페이지 요청을 하는 코드이다. 특정 url을 적으면 웹피이지에 대한 소스코드들을 볼 수 있다.
    
    soup = BeautifulSoup(html.text, 'html.parser')
    
    newsList = []
    
    for i in soup.find('ul', {'class' : 'sa_list'}).find_all('a') :
        if i.find('strong') != None :
            newsList.append([i.text.strip(), i.get('href')])
        
    return newsList

app = Flask(__name__)    #플라스크 객체(서버) 생성

app.config["MONGO_URI"] = "mongodb+srv://admin:1234@cluster0.e1str.mongodb.net/myweb?"
mongo = PyMongo(app)     #mongo 변수를 통해 DB(myweb)에 접근 가능

@app.route("/")    #라우트는 데코레이터(@)와 함수를 활용하여 구현됨, "/"은 루트 경로
def index():
    meal = getMeal()
    weather = getWeather()
    news = getNews()
    
    todo = mongo.db.todo
    todoList = todo.find()
    
    return render_template('index.html', meal=meal, weather=weather, news=news, todoList=todoList)

@app.route("/todo", methods=["POST"])   #POST 요청 처리를 위해 필요한 속성
def todo():    
    contents = request.form.get("contents")      #폼의 name 속성값이 contents인 데이터
    post = { "contents" : contents, }     #데이터베이스에 저장될 자료구조(딕셔너리)
    
    todo = mongo.db.todo     #todo는 컬렉션(테이블)의 이름
    todo.insert_one(post)
    
    return redirect('/')

@app.route("/delete/<idx>")    # 팬시(간편, clean) URL 형식
def delete(idx):
    todo = mongo.db.todo
    todo.delete_one({"_id":ObjectId(idx)}) 
    return redirect('/')
