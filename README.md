# NeubilityDJ
automatic music player made with slack api + selenium

### Prerequisites

What things you need to install the software and how to install them

```
python version 3.8.13

pip install -r requirements.txt
```

1. 포트포워딩 설정
2. https://api.slack.com/ 접속
3. Create an app 선택
4. From scratch 선택
5. App Name 설정, 워크스페이스 선택
6. OAuth & Permissions 탭 이동
7. Scopes 필요한 scope 추가 
   ( 현재 추가된 것은 app_mentions:read, channels:join, users:read, chat:write, incoming-webhook, commands )
8. slash commends 추가 (neubilityDJ.py에서 @self.app.route("/reset", methods=["POST"]) 에 해당하는 slash 명령어 추가)
9. Interactivity & Shortcuts RequestURL 설정  공인IP/process_button
10. Install to Workspace
11. Bot User OAuth Token 복사
12. Event Subscriptions 탭 이동 Request URL 입력
( http://ip:port/slack ) ip는 공인IP, port는 1번에서 진행한 값으로 설정
13. 코드의 8번에서 복사한 token에 입력
14. 코드의 ip와 port 세팅 (사설 IP, 0번에서 진행한 포트로 설정)
15. 실행
16. 해당 채널에 봇 초대 @

### To - Do

1. 예상하지 못한 버그 발견 및 대응
2. 여러 명이 있는 환경에서 테스트 필요
3. manual 업데이트
4. 기본곡 수정 혹은 추천곡으로 바꿀지?
