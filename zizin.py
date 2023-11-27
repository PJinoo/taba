from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.select import Select
import time
import re
import event
import json
import datetime as dt
from collections import OrderedDict
import urllib.request
from bs4 import BeautifulSoup
file_data = OrderedDict()
driver = webdriver.Chrome()
import base_Flask
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

        file_data["latitude"] = script_tags[0].text[17792:17796]
        file_data["longitude"] = script_tags[0].text[17815:17822]
        file_data["magnitude"] = magnitude
        print(json.dumps(file_data,ensure_ascii=False, indent="\t"))
        if item == '':
            item = script_tags[0]
        else:
            new_item = script_tags[0]
            if item != new_item:
                text = iframe_soup.select(".est_mag")
                print(script_tags[0].text[17776:17822])
                print(formatted_output)
                file_data["latitude"] = script_tags[0].text[17792:17822]
                file_data["longitude"] = script_tags[0].text[17817:17822]
                file_data["magnitude"] = magnitude

                base_Flask.data = file_data
                #지진 났으니깐 서버에 지진 났다고 전달, text값도 같이 전달(flask)
                event.start("지진")
        time.sleep(3)    
        driver.refresh()

    # print(script_tags[0].text[17776:17822])
    # time.sleep(3)
start()