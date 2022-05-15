#-*- coding: utf-8 -*-
import json
from flask import Flask, request, make_response
import requests
import threading
import time
from collections import deque

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
import re
from oclock import Event
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities 
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from urllib.parse import quote

class WebApp():
    def __init__(self, ip, port): 
        self.ip = ip
        self.port = port
        self.app = Flask(__name__)
        self.token = YOUR_TOKEN
        self.play_list = deque()
        self.play_list.clear()
        self.e = Event()
        self.m = re.compile('[<]?http[s]?://www.youtube.com/(?:[a-zA-Z]|[0-9]|[$\-@\.&+:/?=]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+[>]?')
        self.current_song = ''
        self.current_singer = ''
        self.current_user = ''
        self.playing = False
        self.birthday_video = 'https://www.youtube.com/watch?v=uoNK5xq2MhA&ab_channel=TJKARAOKETJ%EB%85%B8%EB%9E%98%EB%B0%A9%EA%B3%B5%EC%8B%9D%EC%9C%A0%ED%8A%9C%EB%B8%8C%EC%B1%84%EB%84%90'
        self.path_to_extension = YOUR_EXTENSION_PATH
        self.chrome_options = webdriver.ChromeOptions()
        self.caps = DesiredCapabilities().CHROME 
        self.caps["pageLoadStrategy"] = "none"
        self.default_video = 'https://www.youtube.com/watch?v=CMPydTGGYJw&t=484s&ab_channel=Programmers'
        self.channel = None
        self.is_stop = False

    def print_list(self, mode=0):
        li = list(self.play_list)
        print(li)
        text = '노래 대기 목록\n\n'
        for i in range(len(li)):
            text += str(i + 1) + '. ' + li[i]['music'] + '\n'
        if text == '':
            if mode == 0:
                text = '대기 중인 노래가 없습니다.'
        return text

    def member_name(self, user_id):
        response = requests.get("https://slack.com/api/users.list",
            headers={"Authorization": "Bearer "+ self.token}
        )
        users = response.json()['members']
        for user in users:
            if user['id'] == user_id:
                return user['real_name']
    
    def post_message(self, text):
        response = requests.post("https://slack.com/api/chat.postMessage",
            headers={"Authorization": "Bearer "+ self.token},
            data={"channel": self.channel,"text": text}
        )
        print(response)
    
    def is_youtube_link(self, link):
        if self.m.match(link) is not None:
            return True
        return False
    
    def is_birthdaysong(self, message):
        if message.lower() == 'birthday':
            return True
        return False

    
    def add_birthdaysong(self, user_name):
        data = {}
        data['music'] = self.birthday_video
        data['user'] = user_name
        if self.playing == False:
            self.e.set()
        self.play_list.appendleft(data)
        text = '생일 축하합니다\n' + self.print_list(1)
        self.post_message(text)
        return make_response("success", 200, {"X-Slack-No-Retry": 1})

    def add_link(self, message, user_name):
        data = {}
        if message[0] == '<':
            message = message[1:]
            print(message)
        if message[-1] == '>':
            message = message[:-1]
            print(message)
        data['music'] = message
        data['user'] = user_name
        if self.playing == False:
            self.e.set()
        self.play_list.append(data)
        text = self.print_list(1)

        self.post_message(text)
        return make_response("success", 200, {"X-Slack-No-Retry": 1})

    def is_highest_priority(self, message):
        if message[0] == '!':
            return True
        return False

    def extract_info(self, message):
        msgs = message.split('-')
        if len(msgs) < 2:
            text = '형식 어긋남 가수 - 제목 형식으로 입력해주세요.'
            self.post_message(text)
            return make_response("success", 200, {"X-Slack-No-Retry": 1})

        singer = message.split('-')[0].strip()
        song = message.split('-')[1].strip()
        return singer, song

    def left_add_song(self, singer, song, user_name):
        data = {}
        data['music'] = singer + ' - ' + song
        data['user'] = user_name
        if self.playing == False:
            self.e.set()
        self.play_list.appendleft(data)
        text = self.print_list(1)

        self.post_message(text)
        return make_response("success", 200, {"X-Slack-No-Retry": 1})

    def add_song(self, singer, song, user_name):
        data = {}
        data['music'] = singer + ' - ' + song
        data['user'] = user_name
        if self.playing == False:
            self.e.set()
        self.play_list.append(data)
        text = self.print_list(1)

        self.post_message(text)
        return make_response("success", 200, {"X-Slack-No-Retry": 1})
    
    def how_to_use_DJ(self):
        text = " *사용법* \n\n1. 재생 리스트에 추가하는 법 : \n  a. *@neubieDJ 가수명 - 제목* 형식으로 검색 ( ex) *태연 - weekend* )\n  b. *@neubieDJ 유튜브 링크* 로 검색\n2. 재생 리스트 보는 법 : \n  a. *@neubieDJ list*\n3. 노래 추가한 사람 확인 : \n  a. *@neubieDJ whom*\n4. 현재 노래 건너뛰기 : \n  a. *@neubieDJ skip*\n5. 노래를 리스트의 최상단으로 넣기 : \n  a. *노래를 추가할 때 앞에 !붙이기*\n6. 생일 축하 노래 넣기 : \n  a. *@neubieDJ birthday*\n  b. 5번의 우선 집어넣기도 적용됨\n6. 노래 재생봇 중단 : \n  a. *@neubieDJ stop*\n7. 노래 재생봇 시작 : \n  a. *@neubieDJ start*"
        self.post_message(text)
        return make_response("success", 200, {"X-Slack-No-Retry": 1})


    def message_process(self, message, user_name):
        if self.is_highest_priority(message.lower()):
            message = message[1:]
            if self.is_birthdaysong(message.lower()) == True:
                return self.add_birthdaysong(self, user_name)
            
            elif self.is_youtube_link(message):
                return self.add_link(message, user_name)
            
            singer = ''
            song = ''
            try:
                singer, song = self.extract_info(message)
            except:
                return make_response("success", 200, {"X-Slack-No-Retry": 1})

            return self.left_add_song(singer, song, user_name)

        elif message.lower() == 'stop':
            self.is_stop = True
            self.play_list.clear()
            self.e.set()
            return make_response("success", 200, {"X-Slack-No-Retry": 1})
        
        elif message.lower() == 'start':
            self.is_stop = False
            return make_response("success", 200, {"X-Slack-No-Retry": 1})

        elif message.lower() == 'list':
            text = self.print_list()
            self.post_message(text)
            return make_response("success", 200, {"X-Slack-No-Retry": 1})  

        elif message.lower() == 'instructions':
            return self.how_to_use_DJ()

        elif message.lower() == 'skip':
            self.e.set()
            text = 'skip\n' + self.current_singer + ' - ' + self.current_song
            self.post_message(text)
            return make_response("success", 200, {"X-Slack-No-Retry": 1})

        elif message.lower() == 'whom':
            text = self.current_user
            if text == '':
                text = '재생 중인 노래가 없습니다.'
            self.post_message(text)
            return make_response("success", 200, {"X-Slack-No-Retry": 1})

        elif message.lower() == 'current':
            text = self.current_singer + ' - ' + self.current_song
            if text == '':
                text = '재생 중인 노래가 없습니다.'
            self.post_message(text)
            return make_response("success", 200, {"X-Slack-No-Retry": 1})

        elif self.is_birthdaysong(message.lower()) == True:
            return self.add_birthdaysong(self, user_name)
            
        elif self.is_youtube_link(message):
            return self.add_link(message, user_name)

        print(message)
        singer = ''
        song = ''
        try:
            singer, song = self.extract_info(message)
        except:
            return make_response("success", 200, {"X-Slack-No-Retry": 1})
        return self.add_song(singer, song, user_name)


    def run(self):
        @self.app.route("/slack", methods=["POST"])            
        def test():
            slack_event = json.loads(request.data)
            # if "challenge" in slack_event:
            #     return make_response(slack_event["challenge"], 200, {"content_type": "application/json"})
            print(slack_event)
            if not "event" in slack_event:
                return make_response("슬랙 요청에 이벤트가 없습니다.", 404, {"X-Slack-No-Retry": 1})
            else:
                if slack_event['event']['type'].strip() == 'app_mention':
                    self.channel = slack_event["event"]["channel"]
                    print(slack_event['event']['text'])
                    message = slack_event['event']['text'].strip().split('>')[1]
                    message = message.strip()
                    user_name = self.member_name(slack_event['event']['user'])
                    return self.message_process(message, user_name) 

        t = threading.Thread(target=self.app.run, args=(self.ip,self.port,False))
        t.start()

    def check_ads(self, driver):
        is_ads = False
        try:
            ads = driver.find_element(by=By.XPATH, value='//div[contains(@class, "ytp-ad-text ytp-ad-preview-text")]')
            is_ads = True
        except:
            is_ads = False
        return is_ads

    def cal_duration(self, driver, mode='normal'):
        duration = driver.find_element(by=By.XPATH, value='//span[contains(@class, "ytp-time-duration")]')
        times = duration.text.split(':')
        print('time : ', times)
        sleep_time = 0
        if mode == 'default':
            if len(times) == 3:
                hour = int(times[0]) 
                min = int(times[1])
                sec = int(times[2])
                sleep_time = sec + min * 60 + hour * 3600
            elif len(times) == 2:
                hour = 0 
                min = int(times[0])
                sec = int(times[1])
                if min == 0:
                    is_ads = self.check_ads(driver)

                    if is_ads == True:
                        time.sleep(sec + 1)
                    element = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.CLASS_NAME, "ytp-time-duration")))
                    times = driver.find_element_by_xpath('//span[contains(@class, "ytp-time-duration")]').text.split(':')
                    print(times)
                    if len(times) == 3:
                        hour = int(times[0])
                        min = int(times[1])
                        sec = int(times[2])
                    elif len(times) == 2:
                        hour = 0
                        min = int(times[0])
                        sec = int(times[1])
                sleep_time = sec + min * 60 + hour * 3600
            else:
                return -1
        else:
            if len(times) > 2 or len(times) <= 0:
                return -1
            else:
                min = int(times[0])
                sec = int(times[1])
                if min > 10:
                    return -1
                elif min == 0:
                    is_ads = self.check_ads(driver)

                    if is_ads == True:
                        time.sleep(sec + 1)
                    element = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.CLASS_NAME, "ytp-time-duration")))
                    times = driver.find_element_by_xpath('//span[contains(@class, "ytp-time-duration")]').text.split(':')
                    print(times)
                    if len(times) > 2 or len(times) <= 0:
                        return -1
                    else:
                        min = int(times[0])
                        sec = int(times[1])
            sleep_time = sec + min * 60
        return sleep_time

    def move_tab(self, driver):
        driver.implicitly_wait(2)
        driver.switch_to.window(driver.window_handles[-1])

    def accelerate_selenium(self):
        self.chrome_options.add_argument('load-extension=' + self.path_to_extension)

        self.chrome_options.add_argument("window-size=1920x1080") # 화면크기(전체화면)
        self.chrome_options.add_argument("disable-gpu") 
        self.chrome_options.add_argument("disable-infobars")

        prefs = {'profile.default_content_setting_values': {'cookies' : 2, 'images': 2, 'plugins' : 2, 'popups': 2, 'geolocation': 2, 'notifications' : 2, 'auto_select_certificate': 2, 'fullscreen' : 2, 'mouselock' : 2, 'mixed_script': 2, 'media_stream' : 2, 'media_stream_mic' : 2, 'media_stream_camera': 2, 'protocol_handlers' : 2, 'ppapi_broker' : 2, 'automatic_downloads': 2, 'midi_sysex' : 2, 'push_messaging' : 2, 'ssl_cert_decisions': 2, 'metro_switch_to_desktop' : 2, 'protected_media_identifier': 2, 'app_banner': 2, 'site_engagement' : 2, 'durable_storage' : 2} }   
        self.chrome_options.add_experimental_option('prefs', prefs)
        self.chrome_options.add_experimental_option('excludeSwitches', ['enable-loggin'])
        
        
    

    def play_music(self):
        while(True):
            if self.is_stop == True:
                time.sleep(1)
                continue

            self.accelerate_selenium()
            driver = webdriver.Chrome(YOUR_CHROME_DRIVER_PATH, chrome_options=self.chrome_options)
            driver.create_options()
            
            if len(self.play_list) == 0:
                self.current_song = ''
                self.current_user = ''
                self.current_singer = ''
                
                driver.get(self.default_video)
                self.move_tab(driver)
                element = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.CLASS_NAME, "ytp-time-duration")))
                sleep_time = self.cal_duration(driver, mode='default')
                if sleep_time == -1:
                    text = '기본곡 설정이 올바르지 않습니다.'
                    self.post_message(self.token, self.channel, text)
                else:
                    driver.find_element(by=By.XPATH, value='//button[contains(@class, "ytp-large-play-button ytp-button")]').click()
                    self.playing = False
                    self.e.clear()
                    self.e.wait(timeout=sleep_time)
                driver.quit()
            else:
                res = self.play_list.popleft()
                print('res : ', res['music'])
                
                if self.is_youtube_link(res['music']) == True:
                    self.current_song = res['music']
                    self.current_singer = ''
                    self.current_user = res['user']
                    driver.get(res['music'])
                    self.move_tab(driver)
                    element = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.CLASS_NAME, "ytp-time-duration")))
                    sleep_time = self.cal_duration(driver)
                    if sleep_time == -1:
                        text = self.current_singer + ' - ' + self.current_song + ' 취소되었습니다.\n'
                        text = '10분 미만의 곡만 신청이 가능합니다.'
                        self.post_message(self.token, self.channel, text)
                    else:
                        driver.find_element(by=By.XPATH, value='//button[contains(@class, "ytp-large-play-button ytp-button")]').click()
                        self.playing = True
                        self.e.clear()
                        self.e.wait(timeout=sleep_time)
                    driver.quit()
                else:
                    singer, song = res['music'].split('-')
                    self.current_song = song
                    self.current_singer = singer
                    self.current_user = res['user']
                    query = singer + ' - ' + song + ' 음원'

                    driver.get("https://www.youtube.com/results?search_query=" + quote(query))
                    self.move_tab(driver)
                    element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "video-title")))
                    videos = driver.find_elements(by=By.XPATH, value='//a[contains(@class, "yt-simple-endpoint style-scope ytd-video-renderer")]')
                    for video in videos:                
                        
                        valid = True
                        video.click()
                        element = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.CLASS_NAME, "ytp-time-duration")))
                        sleep_time = self.cal_duration(driver)
                        if sleep_time == -1:
                            valid = False
                        else:
                            self.playing = True               
                            self.e.clear()
                            self.e.wait(timeout=sleep_time)

                        if valid == False:
                            driver.back()
                            continue
                        else:
                            break
                    driver.quit()
        

if __name__ == '__main__':
    webapp = WebApp(YOUR_IP, YOUR_PORT)
    music_t = threading.Thread(target=webapp.play_music, daemon=True)
    music_t.start()
    webapp.run()
