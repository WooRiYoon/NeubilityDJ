from flask import make_response
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from urllib.parse import quote
from selenium.webdriver.support import expected_conditions as EC
from pynput.keyboard import Key,Controller
import requests, re, json, time, os, chromedriver_autoinstaller
from selenium import webdriver

class DJProcess:
    def __init__(self, token):
        self.token = token
        self.keyboard = Controller()
        self.channel = ''
        self.birthday_video = 'https://www.youtube.com/watch?v=uoNK5xq2MhA&ab_channel=TJKARAOKETJ%EB%85%B8%EB%9E%98%EB%B0%A9%EA%B3%B5%EC%8B%9D%EC%9C%A0%ED%8A%9C%EB%B8%8C%EC%B1%84%EB%84%90'

    def birthday(self, request_form, play_list):
        self.channel = request_form.get("channel_id")
        user_id = request_form.get('user_id')
        name = request_form.get('text')

        result = {}
        result['user_id'] = user_id
        result['title'] = '%s님 생일 축하' % name
        result['link'] = self.birthday_video
        play_list.appendleft(result)
        self.post_message('*%s* 님 생일 축하합니다.' % name)

    def move_tab(self, driver):
        driver.switch_to.window(driver.window_handles[0])
        driver.close()
        driver.switch_to.window(driver.window_handles[0])

    def chrome_auto_install(self):
        chrome_ver = chromedriver_autoinstaller.get_chrome_version().split('.')[0]
        
        driver_path = f'./{chrome_ver}/chromedriver.exe'
        if os.path.exists(driver_path):
            print(f"chrom driver is insatlled: {driver_path}")
        else:
            print(f"install the chrome driver(ver: {chrome_ver})")
            chromedriver_autoinstaller.install(True)
        return driver_path

    def setting_driver(self, path_to_extension, driver_path):
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('load-extension=' + path_to_extension)

        chrome_options.add_argument("window-size=1920x1080") # 화면크기(전체화면)
        chrome_options.add_argument("disable-gpu") 
        chrome_options.add_argument("disable-infobars")

        prefs = {'profile.default_content_setting_values': {'cookies' : 2, 'images': 2, 'plugins' : 2, 'popups': 2, 'geolocation': 2, 'notifications' : 2, 'auto_select_certificate': 2, 'fullscreen' : 2, 'mouselock' : 2, 'mixed_script': 2, 'media_stream' : 2, 'media_stream_mic' : 2, 'media_stream_camera': 2, 'protocol_handlers' : 2, 'ppapi_broker' : 2, 'automatic_downloads': 2, 'midi_sysex' : 2, 'push_messaging' : 2, 'ssl_cert_decisions': 2, 'metro_switch_to_desktop' : 2, 'protected_media_identifier': 2, 'app_banner': 2, 'site_engagement' : 2, 'durable_storage' : 2} }   
        chrome_options.add_experimental_option('prefs', prefs)
        chrome_options.add_experimental_option('excludeSwitches', ['enable-loggin'])

        driver = webdriver.Chrome(driver_path, options=chrome_options)
        
        driver.create_options()
        driver.get('https://www.youtube.com/')
        self.move_tab(driver)
        element = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.CLASS_NAME, "style-scope ytd-rich-grid-media")))
        return driver

    def manual(self, request_form):
        text = " *사용법* \n\n*1. volume 조절*\n    ex) /volume down 10\n*2. 노래를 끄고 싶을 때는 stop명령어 사용*\n*3. 그 외의 명령어는 spotify와 동일합니다.*\n"
        self.channel = request_form.get("channel_id")
        self.post_message(text)
        return make_response("manual", 200, {"X-Slack-No-Retry": 1})

    def list(self, request_form, play_list):
        self.channel = request_form.get("channel_id")
        message = '*대기 중인 재생목록*\n\n'
        if len(play_list) == 0:
            message = '* 대기 중인 음악이 없습니다. *'
        else:
            for i in range(len(play_list)):
                message += '%d. %s \n' % (i + 1, play_list[i]['title'])
        self.post_message(message)
        return make_response("list", 200, {"X-Slack-No-Retry": 1})
    
    def add(self, request_form, search_driver, play_list, event, default):
        self.channel = request_form.get("channel_id")
        message = request_form.get('text')
        user_id = request_form.get('user_id')

        result = {}
        result['user_id'] = user_id
        search_driver.get("https://www.youtube.com/results?search_query=" + quote(message + ' 가사'))
        WebDriverWait(search_driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//a[@class="yt-simple-endpoint style-scope ytd-video-renderer"]')))

        videos = search_driver.find_elements(by=By.XPATH, value='//a[contains(@class, "yt-simple-endpoint style-scope ytd-video-renderer")]')
        max_search = 3
        check_success = False
        for i in range(max_search):          
            url = videos[i].get_attribute('href')
            title = videos[i].text
            result['title'] = title
            result['link'] = url
            if default == True:
                default = False
                event.set()
            play_list.append(result)
            check_success = True
            break
        if check_success == True:
            self.post_message('*:tada: New video added to your playlist !*\n %s' % result['title'])
        else:
            self.post_message('*Fail!*\n %s' % result['title'])
        return make_response("add", 200, {"X-Slack-No-Retry": 1}), default
    
    def find(self, request_form, search_driver):
        message = request_form.get('text')
        self.channel = request_form.get("channel_id")

        search_driver.get("https://www.youtube.com/results?search_query=" + quote(message))
        WebDriverWait(search_driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//a[@class="yt-simple-endpoint style-scope ytd-video-renderer"]')))

        videos = search_driver.find_elements(by=By.XPATH, value='//a[contains(@class, "yt-simple-endpoint style-scope ytd-video-renderer")]')
        thumbnails = search_driver.find_elements(by=By.XPATH, value="//div[@id='dismissible']/ytd-thumbnail[@class='style-scope ytd-video-renderer']/a[@id='thumbnail']/yt-img-shadow[@*]/img[@class='style-scope yt-img-shadow']")
        
        length = min(len(videos), len(thumbnails), 3)
        block = self.make_block()
        
        block = self.make_video_list(0, length, videos, thumbnails, block, message)
        slack_data={"channel" : self.channel, "blocks": block, "replace_original": True }
        self.post_message(text='', json=slack_data)
        return make_response("find", 200, {"X-Slack-No-Retry": 1})
    
    def button_click(self, request_form, search_driver, play_list, event, default):
        json_format = request_form.get('payload')
        json_format = json.loads(json_format)
        self.channel = json_format["container"]["channel_id"]
        selected_option = json.loads(json_format['actions'][0]['value'])
        timestamp = json_format['container']['message_ts']
        if selected_option['title'] == "see more videos":
            start = int(json.loads(json_format['message']['blocks'][3]['accessory']['value'])['index'])
            end = int(json.loads(json_format['message']['blocks'][-2]['accessory']['value'])['index'])
            message = selected_option['message']
            search_driver.get("https://www.youtube.com/results?search_query=" + quote(message))
            WebDriverWait(search_driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//a[@class="yt-simple-endpoint style-scope ytd-video-renderer"]')))

            videos = search_driver.find_elements(by=By.XPATH, value='//a[contains(@class, "yt-simple-endpoint style-scope ytd-video-renderer")]')
            thumbnails = search_driver.find_elements(by=By.XPATH, value="//div[@id='dismissible']/ytd-thumbnail[@class='style-scope ytd-video-renderer']/a[@id='thumbnail']/yt-img-shadow[@*]/img[@class='style-scope yt-img-shadow']")
            end = end + 1
            length = min(len(videos), len(thumbnails), end + 3)
            if end >= length:
                end = 0
                length = min(len(videos), len(thumbnails), end + 3)
            block = self.make_block()
        
            block = self.make_video_list(end, length, videos, thumbnails, block, message)
            response = requests.post("https://slack.com/api/chat.update",
                headers={"Authorization": "Bearer "+ self.token},
                json={"channel": self.channel, "ts" : timestamp, "blocks" : block},
            )
        else:
            result = {}
            result['link'] = selected_option['link']
            result['title'] = selected_option['title']
            result['user_id'] = json_format['user']['id']
            if default == True:
                default = False
                event.set()
            play_list.append(result)

            response = requests.post("https://slack.com/api/chat.update",
                headers={"Authorization": "Bearer "+ self.token},
                data={"channel": self.channel, "ts" : timestamp, "blocks" : '[]', "text" : '*:tada:New video added to your playlist !*\n %s' % result['title']},
            )
        
        return make_response("button_click", 200, {"X-Slack-No-Retry": 1}), default

    def whom(self, request_form, current_title, current_user):
        self.channel = request_form.get("channel_id")
        self.post_message(text= ':microphone: This video, *%s* , \nwas last requested by <@%s>' % (current_title, current_user) )
        return make_response("whom", 200, {"X-Slack-No-Retry": 1})
    
    def current(self, request_form, current_title):
        self.channel = request_form.get("channel_id")
        self.post_message(text = ':musical_note: Your current video is \n*%s*' % (current_title))
        return make_response("success_print_whom", 200, {"X-Slack-No-Retry": 1})
    
    def pause(self, request_form):
        self.channel = request_form.get("channel_id")
        # if self.playing == True and self.is_pause == False:
        #     WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//video[@class="video-stream html5-main-video"]'))).click()
        #     self.playing = False
        # self.is_pause = True
        self.post_message(text = '일시 정지는 아직 지원하지 않고 있는 기능입니다.')
        return make_response("success_pause", 200, {"X-Slack-No-Retry": 1})
    
    def play(self, driver, event, playing, is_pause, is_stop):
        if playing == False:
            if is_pause == True and is_stop == False:
                WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//video[@class="video-stream html5-main-video"]'))).click()
            else:
                if is_stop == True:
                    event.clear()
        is_stop = False
        is_pause = False
        playing = True
        return make_response("success_play", 200, {"X-Slack-No-Retry": 1}), is_stop, is_pause, playing

    def stop(self, play_list, event, driver, is_stop, playing):
        play_list.clear()
        if is_stop == False and playing == True:
            event.set()
            WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//video[@class="video-stream html5-main-video"]'))).click()          
        is_stop = True
        playing = False
        return make_response("success_stop", 200, {"X-Slack-No-Retry": 1}), is_stop, playing
    
    def reset(self, play_list):
        play_list.clear()
        return make_response("success_reset", 200, {"X-Slack-No-Retry": 1})

    def skip(self, is_pause, is_stop, playing, event, driver):
        if is_stop == False and playing == True:
            event.set()
            WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//video[@class="video-stream html5-main-video"]'))).click()
            playing = False
        is_pause = False
        return make_response("success_skip", 200, {"X-Slack-No-Retry": 1}), is_pause, playing
    
    def volume(self, request_form):
        self.channel = request_form.get("channel_id")
        message = request_form.get('text')
        
        try:
            method , size = message.split(' ')
            size = int(size)
            if method == 'down':
                for i in range(size):
                    self.keyboard.press(Key.media_volume_down)
                self.keyboard.release(Key.media_volume_down)
                self.post_message('*:speaker:Great! Your video volume has been set down*')
            elif method == 'up':
                for i in range(size):
                    self.keyboard.press(Key.media_volume_up)
                self.keyboard.release(Key.media_volume_up)
                self.post_message('*:speaker:Great! Your video volume has been set up*')
            else:
                self.post_message('*:speaker:Fail! You have to send only up or down *')
        except:
            self.post_message('*잘못된 형식으로 볼륨을 조절하였습니다.*\n올바른 예시) /volume up 10')
        return make_response("success_volume_control", 200, {"X-Slack-No-Retry": 1})        

    def post_message(self, text, json=None):
        if json == None:
            response = requests.post("https://slack.com/api/chat.postMessage",
                headers={"Authorization": "Bearer "+ self.token},
                data={"channel": self.channel,"text": text },
            )
        else:
            response = requests.post("https://slack.com/api/chat.postMessage",
                headers={"Authorization": "Bearer "+ self.token},
                json = json,
            )

    def member_name(self, user_id):
        response = requests.get("https://slack.com/api/users.list",
            headers={"Authorization": "Bearer "+ self.token}
        )
        users = response.json()['members']
        for user in users:
            if user['id'] == user_id:
                return user['real_name']
        return None

    def make_block(self):
        block = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "Are any of theses videos what you were looking for?"
                }
            },
            {
                "type": "divider"
            },
        ]
        return block

    
    def make_video_list(self, start, end, videos, thumbnails, block, message):
        for i in range(start, end):
            info = str(videos[i].get_attribute('aria-label')).split('게시자')
            title = info[0]
            duration = info[1]
            fields = {}
            fields['type'] = 'section'
            fields['text'] = {'type' : 'mrkdwn', 'text' : '*:studio_microphone:' + title + '*' }
            fields['accessory'] = { 'type' : 'image', 'image_url' : str(thumbnails[i].get_attribute('src')).split('?')[0], 'alt_text' : ''}
            block.append(fields)
            
            duration = duration.replace('시간 ', 'h')
            duration = duration.replace('분 ', 'm')
            m = re.search('(([0-9]+)[h]?)?(([0-9]+)[m]?)?([0-9]+)초', duration)
            if m != None:
                duration = m.group().split('h')
                hour = 0
                minute = 0
                if len(duration) >= 2:
                    hour = duration[0]
                    duration = duration[1]
                else:
                    duration = duration[0]
                duration = duration.split('m')
                if len(duration) >= 2:
                    minute = duration[0]
                    duration = duration[1]
                else:
                    duration = duration[0]
                sec = duration.split('초')[0]
                if hour == 0:
                    if minute == 0:
                        duration = '영상 길이 : ' + str(sec) + '초'
                    else:
                        duration = '영상 길이 : ' + str(minute) + '분 ' + str(sec) + '초'
                else:
                    duration = '영상 길이 : ' + str(hour) + '시간 ' + str(minute) + '분 ' + str(sec) + '초'
            else:
                duration = ' '
            
            video_link = str(videos[i].get_attribute('href'))
            context = {}
            context['type'] = 'section'
            context['text'] = {'type' : 'mrkdwn', 'text' : duration }
            context['accessory'] = {'type' : 'button', 'text' : {'type' : 'plain_text', 'emoji' : True, 'text' : 'Add song'}, "style": "primary", 'value' : '{"index" : "%d" , "title" : "%s", "link" : "%s"}' % (i, title.replace('"',''), video_link) }

            block.append(context)
        context = {}
        context['type'] = 'actions'
        context['elements'] = [
            { "type": "button",  
                "text": {
                    "type": "plain_text",
                    "text": "See more videos"
                },
                "value": '{"message" : "%s", "title" : "see more videos" }' % message
            }
        ]
        block.append(context)
        return block

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
