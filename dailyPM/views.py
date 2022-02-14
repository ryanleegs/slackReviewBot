from rest_framework.views import APIView
from rest_framework.response import Response
from slack_sdk import WebClient

import datetime

import templates.Constants as const
from django.db import connection

# 슬랙 세팅
slack = WebClient(token=const.slackToken)


class employeeList():
    def post(self):
        try:
            """
                TODO 
                1. mariaDB에 각 담당자 데이터 관리
                2. 노션에 각 담당자 데이터 관리
            """

            # 1번
            cursor = connection.cursor()
            today = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            strSql = "SELECT * FROM gsitmmobile.employee_info WHERE start_dt <= %s AND end_dt >= %s"
            result = cursor.execute(strSql, (today, today))  # 실행 여부 성공 1 실패 0 ?
            nlist = cursor.fetchall()
            connection.commit()
            connection.close()

            # 2번
            """
                TODO 
                token = 'a8b1f42ae4c723ba17c34e749b06e38cc7c46b66b7c264533ec98c51469a733e5a7409a65a4db7353a02fb0c41c0682683070ef8e7a86008cf359a9dd50920f6426fd6dd531a69a621e65771fcca'
                
                
            """
        except:
            # 1번
            connection.rollback()
            print("Failed !!!!!!!!!!!!!!!!!!!!!!!")

        return nlist


class dailyPost(APIView):
    def post(self, request):
        challenge = request.data.get('challenge')
        name = list(employeeList.post(self))
        print("name ========>", name)
        sendSlack.send(name)
        return Response(status=200, data=dict(challenge=challenge))


class sendSlack():

    def send(lst):
        user_name = lst[0][1]
        user_token = lst[0][5]

        return slack.chat_postMessage(
            channel="#chatbot_test"
            , attachments=[
                {
                    "color": "#f2c744",
                    "blocks": [
                        {
                            "type": "section",
                            "text": {
                                "type": "mrkdwn",
                                "text": "<@" + user_token + "> " + user_name + "매니저님!!!!!!! 일일점검 하실 시간입니다!"
                            }
                        }
                    ]
                }
            ]
        )
