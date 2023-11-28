# 크롤링시 필요한 라이브러리 불러오기
from bs4 import BeautifulSoup
import requests
import re
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import news_sum
import ai_base
import paramiko
# 웹드라이버 설정
options = webdriver.ChromeOptions()
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option("useAutomationExtension", False)
options.add_argument("--headless")
options.add_argument("window-size=1400,1500")
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("start-maximized")
options.add_argument("enable-automation")
options.add_argument("--disable-infobars")
options.add_argument("--disable-dev-shm-usage")
driver = webdriver.Chrome(options=options)


# 페이지 url 형식에 맞게 바꾸어 주는 함수 만들기 
# 입력된 수를 1, 11, 21, 31 ...만들어 주는 함수
def makePgNum(num):
    if num == 1:
        return num
    elif num == 0:
        return num + 1
    else:
        return num + 9 * (num - 1)


# 크롤링할 url 생성하는 함수 만들기(검색어, 크롤링 시작 페이지, 크롤링 종료 페이지)
def makeUrl(search, start_pg, end_pg):
    if start_pg == end_pg:
        start_page = makePgNum(start_pg)
        url = "https://search.naver.com/search.naver?where=news&sm=tab_pge&query=" + search + "&start=" + str(
            start_page)
        print("생성url: ", url)
        return url
    else:
        urls = []
        for i in range(start_pg, end_pg + 1):
            page = makePgNum(i)
            url = "https://search.naver.com/search.naver?where=news&sm=tab_pge&query=" + search + "&start=" + str(page)
            urls.append(url)
        print("생성url: ", urls)
        return urls


##########뉴스크롤링 시작###################
def start(search):
    print("뉴스 크롤링 시작")
    # naver url 생성
    search_urls = makeUrl(search, 1, 3)

    ## selenium으로 navernews만 뽑아오기##

    # 버전에 상관 없이 os에 설치된 크롬 브라우저 사용
    driver = webdriver.Chrome()
    driver.implicitly_wait(3)

    # selenium으로 검색 페이지 불러오기 #

    naver_urls = []
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/98.0.4758.102"}
    for i in search_urls:
        driver.get(i)
        time.sleep(1)  # 대기시간 변경 가능

        # 네이버 기사 눌러서 제목 및 본문 가져오기#
        # 네이버 기사가 있는 기사 css selector 모아오기
        a = driver.find_elements(By.CSS_SELECTOR, 'a.info')
        b = driver.find_elements(By.CSS_SELECTOR, 'a.info.press')
        c = []
        for j in a:
            if j not in b:
                c.append(j)
    
        # 위에서 생성한 css selector list 하나씩 클릭하여 본문 url얻기
        for i in c:
            i.click()

            # 현재탭에 접근
            driver.switch_to.window(driver.window_handles[1])
            time.sleep(3)  # 대기시간 변경 가능

            # 네이버 뉴스 url만 가져오기

            url = driver.current_url
            print(url)

            if "news.naver.com" in url:
                original_html = requests.get(url, headers=headers)
                html = BeautifulSoup(original_html.text, "html.parser")
                  # 뉴스 제목 가져오기
                title = html.select("div#ct > div.media_end_head.go_trans > div.media_end_head_title > h2")
                # list합치기
                title = ''.join(str(title))
                # html태그제거
                pattern1 = '<[^>]*>'
                title_test = re.sub(pattern=pattern1, repl='', string=title)
                if search == '북한':
                    if ai_base.is_emergency(title_test,'war_model') == 1:
                        naver_urls.append(url)
                elif search == '지진':
                    if ai_base.is_emergency(title_test) == 1:
                        naver_urls.append(url)
            else:
                pass
            # 현재 탭 닫기
            driver.close()
            # 다시처음 탭으로 돌아가기(매우 중요!!!)
            driver.switch_to.window(driver.window_handles[0])

    print(naver_urls)

    ###naver 기사 본문 및 제목 가져오기###

    # ConnectionError방지
    

    titles = []
    contents = []
    for i in naver_urls:
        original_html = requests.get(i, headers=headers)
        html = BeautifulSoup(original_html.text, "html.parser")
        # 검색결과확인시
        # print(html)

        # 뉴스 제목 가져오기
        title = html.select("div#ct > div.media_end_head.go_trans > div.media_end_head_title > h2")
        # list합치기
        title = ''.join(str(title))
        # html태그제거
        pattern1 = '<[^>]*>'
        title = re.sub(pattern=pattern1, repl='', string=title)
        titles.append(title)
        
        # 뉴스 본문 가져오기

        content = html.select("div#ct > div.newsct_body > div.newsct_article.newsct_article._article_body > article")

        # 기사 텍스트만 가져오기
        # list합치기
        content = ''.join(str(content))

        # html태그제거 및 텍스트 다듬기
        content = re.sub(pattern=pattern1, repl='', string=content)
        pattern2 = """[\n\n\n\n\n// flash 오류를 우회하기 위한 함수 추가\nfunction _flash_removeCallback() {}"""
        content = content.replace(pattern2, '')

        contents.append(content)
        print(content)

    print(titles)
    print(contents)
    sum = []
    for i in range(len(contents)):
        news_sum.news_content.append(contents[i]) 
        if len(contents[i]) >= 300:
            sum.append(news_sum.summarize(3))
        else:
            sum.append(contents[i])
        

    # 데이터프레임으로 정리(titles,url,contents,summary)
    import pandas as pd

    news_df = pd.DataFrame({'title': titles, 'link': naver_urls, 'content': contents, 'summary': sum})

    news_df.to_csv('NaverNews_%s.csv' % search, index=False, encoding='utf-8-sig')
    # 서버 정보 설정
    hostname = '3.36.101.246'
    username = 'ec2-user'
    port = 22  # SSH 포트, 기본값은 22

    # 파일 정보 설정
    local_file = 'NaverNews_' + search +'.csv'
    remote_path = '/home/ec2-user/data/NaverNews_' + search + '.csv'

    # SFTP 세션 시작
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    mykey = paramiko.RSAKey.from_private_key_file('C:/Users/ParkJinoh/Desktop/Crowlling/tibero.pem')
    ssh_client.connect(hostname, port, username, pkey=mykey)

    sftp = ssh_client.open_sftp()
    sftp.put(local_file, remote_path)  # 파일 전송
    sftp.close()

    ssh_client.close()
    