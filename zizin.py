from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.select import Select
from selenium.webdriver.chrome.options import Options
import time
import re
import event
import json
import requests
import datetime as dt
from collections import OrderedDict
import urllib.request
from bs4 import BeautifulSoup
file_data = OrderedDict()
options = Options()
options.add_argument("--headless")
options.add_argument("window-size=1400,1500")
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("start-maximized")
options.add_argument("enable-automation")
options.add_argument("--disable-infobars")
options.add_argument("--disable-dev-shm-usage")
driver = webdriver.Chrome(options = options)
url = "https://www.weather.go.kr/pews/"  # Replace with the URL of the web page
driver.get(url)

def start():
    item = ''
    new_item = ''  
    while(1):
        response = driver.page_source
        html_content = response
        soup = BeautifulSoup(html_content, "html.parser")
        iFrames=[] # qucik bs4 example
        iframexx = soup.find_all('iframe')
        url = "https://www.weather.go.kr/pews/"
        response = urllib.request.urlopen(url + iframexx[0].attrs['src'])
        iframe_soup = BeautifulSoup(response)
        script_tags = iframe_soup.find_all("script")
        print(script_tags[0].text[17776:17822])
        text = iframe_soup.select(".est_mag")
        
        # Parse the HTML
        soup_mag = BeautifulSoup(str(text), 'html.parser')

        # Extracting magnitude and intensity
        magnitude = soup_mag.find('dt', string='추정규모').find_next('dd').get_text(strip=True)
        intensity = soup_mag.find('dt', string='최대예상진도').find_next('dd').get_text(strip=True)

        # Removing unnecessary characters
        magnitude = magnitude.replace('M', '').replace('L', '')
        intensity = intensity.replace('<b class="val" id="estMag">', '').replace('</b>', '')

        # Formatted output
        formatted_output = f"최대예상진도 {intensity}"

        file_data["latitude"] = float(script_tags[0].text[17792:17797])
        file_data["longitude"] = float(script_tags[0].text[17815:17821])
        file_data["magnitude"] = int(magnitude)
        print(json.dumps(file_data,ensure_ascii=False, indent="\t"))
        if item == '':
            item = script_tags[0]
        else:
            new_item = script_tags[0]
            if item != new_item:
                text = iframe_soup.select(".est_mag")
                print(script_tags[0].text[17776:17822])
                print(formatted_output)
                file_data["latitude"] = float(script_tags[0].text[17792:17797])
                file_data["longitude"] = float(script_tags[0].text[17815:17821])
                file_data["magnitude"] = int(magnitude)
                url = 'http://ec2-3-35-100-8.ap-northeast-2.compute.amazonaws.com:8080/warn/eqk'
                #지진 났으니깐 서버에 지진 났다고 전달, text값도 같이 전달
                response = requests.post(url, data=file_data, headers={'Content-Type': 'application/json'})
                #뉴스 크롤링 event 시작
                event.start("지진")
        time.sleep(3)    
        driver.refresh()

    # print(script_tags[0].text[17776:17822])
    # time.sleep(3)
start()