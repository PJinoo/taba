from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.select import Select
import time
import datetime as dt
from bs4 import BeautifulSoup
import event
import json
import requests
import base_Flask
from collections import OrderedDict
driver = webdriver.Chrome()
file_data = OrderedDict()

driver.get("https://www.safekorea.go.kr/idsiSFK/neo/sfk/cs/sfc/dis/disasterMsgList.jsp?menuSeq=679")
title = []
new_title = []

item = []
new_item = []

while(True):
   # select = Select(driver.find_element(By.CLASS_NAME, value= "boardSearch_select"))
   # select.select_by_index(3)
   # selectt = Select(driver.find_element(By.CSS_SELECTOR, value="#search_dsstr"))
   # selectt.select_by_index(5)
    driver.find_element(By.CLASS_NAME, value= "search_btn").click()

    time.sleep(1)
    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")
    if (title.__len__() == 0):
        title = soup.select(".ellipsis") 
    else:
        new_title = soup.select(".ellipsis")

    if(title.__len__() != 0 and new_title.__len__() != 0):
        if (title[0].get("title") != new_title[0].get("title")):
            #새 데이터 감지 > 배열의 0번째 요소(가장 최신 요소)가 변경되었을 때
            file_data["contents"] = new_title[0].get("title")
            url = 'http://ec2-3-35-100-8.ap-northeast-2.compute.amazonaws.com:8080/warn/eqk'

            response = requests.post(url, data=file_data, headers={'Content-Type': 'application/json'})

            event.start("북한")        
        title = new_title
        new_title = []
    time.sleep(9)