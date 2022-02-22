import json

from rest_framework.views import APIView
from rest_framework.response import Response
from slack_sdk import WebClient

import datetime
import templates.Consts as const

# 슬랙 세팅
slack = WebClient(token=const.slackToken)


class employeeList():
    def post(self):
        # try:
        """
                TODO 
                1. mariaDB에 각 담당자 데이터 관리
                2. 노션에 각 담당자 데이터 관리
            """

        # 1번
        # nlist = ""
        # cursor = connection.cursor()
        # today = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # strSql = "SELECT * FROM gsitmmobile.employee_info WHERE start_dt <= %s AND end_dt >= %s"
        # result = cursor.execute(strSql, (today, today))  # 실행 여부 성공 1 실패 0 ?
        # nlist = cursor.fetchall()
        # connection.commit()
        # connection.close()
        # except:
        #     # 1번
        #     #connection.rollback()
        #     print("Failed !!!!!!!!!!!!!!!!!!!!!!!")

        with open('templates/dailyPM_config.json', 'r', encoding='utf-8') as f:
            member_data = json.load(f)

        today = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        pm_member = []
        for part_data in member_data["part"]:
            for today_member in part_data["market-online"]:
                start_dt = today_member["start_dt"]
                end_dt = today_member["end_dt"]
                if start_dt <= today <= end_dt:
                    pm_member.append(today_member)

        return pm_member


class dailyPost(APIView):
    def post(self, request):
        challenge = request.data.get('challenge')
        # name = list(employeeList.post(self))
        # sendSlack.send(name)
        name = employeeList.post(self)
        sendSlack.send_pm(name)
        return Response(status=200, data=dict(challenge=challenge))


class sendSlack():

    def send_pm(lst):
        user_name = lst[0]["name"]
        user_token = lst[0]["member_id"]
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
