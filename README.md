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
   ( 현재 추가된 것은 app_mentions:read, channels:join, users:read, chat:write )
8. Install to Workspace
9. Bot User OAuth Token 복사
10. Event Subscriptions 탭 이동 Request URL 입력
( http://ip:port/slack ) ip는 공인IP, port는 0번에서 진행한 값으로 설정

** 코드의 아래 주석부분 해제하고 URL 인증받아야 함 **

if "challenge" in slack_event:
    return make_response(slack_event["challenge"], 200, {"content_type": "application/json"})

11. 코드의 8번에서 복사한 token에 입력
12. 코드의 ip와 port 세팅 (사설 IP, 0번에서 진행한 포트로 설정)
13. 실행

### To - Do

1. consider the introduction of slash commends
2. unexpected bug detection and response
3. code refactoring
4. consider introducing new functions