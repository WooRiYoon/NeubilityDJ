#-*- coding: utf-8 -*-
from flask import Flask, request, make_response
import json, time, threading
from collections import deque
from selenium.webdriver.common.by import By
from oclock import Event
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


from process import DJProcess

class WebApp():
    def __init__(self, ip, port): 
        self.ip = ip
        self.port = port
        self.app = Flask(__name__)
        self.token = YOUR_TOKEN
        self.play_list = deque()
    
        self.e = Event()
        self.current_title = ''
        self.current_user = ''
        
        self.default_video = 'https://www.youtube.com/watch?v=CMPydTGGYJw&t=484s&ab_channel=Programmers'

        self.playing = False
        self.default = True
        self.is_stop = False
        self.is_pause = False
        self.process = DJProcess(self.token)

        path_to_extension = r'YOUR_EXTENSION_PATH'
        driver_path = self.process.chrome_auto_install()
        self.driver = self.process.setting_driver(path_to_extension, driver_path)
        self.search_driver = self.process.setting_driver(path_to_extension, driver_path)

    def run(self):
        @self.app.route("/birthday", methods=["POST"])
        def birthday():
            self.process.birthday(request.form, self.play_list)
            result, self.is_pause, self.playing = self.process.skip(self.is_pause, self.is_stop, self.playing, self.e, self.driver)
            return result

        @self.app.route("/manual", methods=["POST"])
        def manual():
            return self.process.manual(request.form)
            
        @self.app.route("/list", methods=["POST"])    
        def list():
            return self.process.list(request.form, play_list=self.play_list)
            
        @self.app.route("/add", methods=["POST"])            
        def add():
            result, self.default = self.process.add(request.form, self.search_driver, self.play_list, self.e, self.default)
            return result
        
        @self.app.route("/find", methods=["POST"])
        def find_song():
            return self.process.find(request.form , self.search_driver)

        @self.app.route("/whom", methods=["POST"])            
        def whom():
            return self.process.whom(request.form, self.current_title, self.current_user)
            
        @self.app.route("/process_button", methods=["POST"])            
        def process_button():
            result, self.default = self.process.button_click(request.form, self.search_driver, self.play_list, self.e, self.default)
            return result

        @self.app.route("/current", methods=["POST"])            
        def current():
            return self.process.current(request.form, self.current_title)

        @self.app.route("/pause", methods=["POST"])            
        def pause():
            return self.process.pause(request.form)
        
        @self.app.route("/play", methods=["POST"])            
        def play():
            result, self.is_stop, self.is_pause, self.playing = self.process.play(self.driver, self.e, self.playing, self.is_pause, self.is_stop)
            return result

        @self.app.route("/stop", methods=["POST"])            
        def stop():
            result, self.is_stop, self.playing = self.process.stop(self.play_list, self.e, self.driver, self.is_stop, self.playing)
            return result
        
        @self.app.route("/reset", methods=["POST"])            
        def reset():
            return self.process.reset(self.play_list)
        
        @self.app.route("/skip", methods=["POST"])            
        def skip():
            result, self.is_pause, self.playing = self.process.skip(self.is_pause, self.is_stop, self.playing, self.e, self.driver)
            return result

        @self.app.route("/volume", methods=["POST"])            
        def volume():
            return self.process.volume(request.form)

        @self.app.route("/slack", methods=["POST"])            
        def test():
            slack_event = json.loads(request.data)
            if "challenge" in slack_event:
                return make_response(slack_event["challenge"], 200, {"content_type": "application/json"})

        t = threading.Thread(target=self.app.run, args=(self.ip,self.port,False))
        t.start()

    def play_music(self):
        while(True):
            if self.is_stop == True:
                time.sleep(1)
                continue
            time.sleep(0.5)
            if len(self.play_list) == 0 and self.is_stop == False and self.is_pause == False:
                self.driver.get(self.default_video)
                WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located((By.CLASS_NAME, "ytp-time-duration")))
                WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//button[@class="ytp-button"]'))).click()
                sleep_time = self.process.cal_duration(self.driver, 'default')
                print('sleep time : ', sleep_time)
                self.current_title = 'default music'
                self.current_user = ''
                self.default = True
                self.playing = True
                self.e.clear()
                self.e.wait(timeout=sleep_time)
                while self.is_pause == True:
                    continue
                self.playing = False
                
                continue
            elif len(self.play_list) != 0 and self.is_stop == False and self.is_pause == False:
                res = self.play_list.popleft()
                print('len : ', len(self.play_list))
                print('res : ', res['link'])
                print('res : ', res['title'])
                
                self.driver.get(res['link'])
                WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located((By.CLASS_NAME, "ytp-time-duration")))
                WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//button[@class="ytp-button"]'))).click()
                sleep_time = self.process.cal_duration(self.driver)
                print('sleep time : ', sleep_time)
                if sleep_time == -1:
                    text = 'bug'
                    self.process.post_message(text)
                else:
                    self.current_title = res['title']
                    self.current_user = res['user_id']
                    self.playing = True
                    self.default = False
                    self.e.clear()
                    self.e.wait(timeout=sleep_time)
                    while self.is_pause == True:
                        continue
                self.playing = False
        

if __name__ == '__main__':
    webapp = WebApp(YOUR_IP, YOUR_PORT)
    music_t = threading.Thread(target=webapp.play_music, daemon=True)
    music_t.start()
    webapp.run()
