from flask import Flask  # 간단히 플라스크 서버를 만든다
import json
import requests
import time

app = Flask(__name__)
data = {}

@app.route("/send_json")
def send_json():

    url = "http://ec2-3-35-100-8.ap-northeast-2.compute.amazonaws.com:8080/warn/eqk"

    # JSON 형태로 데이터를 전송
    while(1):
        response = requests.post(url, json=data)
        time.sleep(2)

    # Spring 서버의 응답을 반환
    return response.text


if __name__ == '__main__':
    app.run(debug=False, host="127.0.0.1", port=5001)