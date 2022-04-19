import json
import logging
import this

from rest_framework.views import APIView
from rest_framework.response import Response
from slack_sdk import WebClient

import datetime

from slack_sdk.errors import SlackApiError

import templates.Consts as const

from django.db import connection

# 슬랙 세팅
slack = WebClient(token=const.slackToken)

class employeeList():
    def readDBPost(self):
        pm_member = []
        try:
            cursor = connection.cursor()

            today = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # 오늘 날짜

            strSql = "SELECT " \
                     "  M.USER_ID,M.USER_NAME " \
                     "FROM " \
                     "   gsmobile.T_MEMBER M LEFT JOIN T_DAILY_PM TDP on M.USER_ID = TDP.USER_ID " \
                     "WHERE " \
                     "  TDP.START_DTIME <= %s AND TDP.END_DTIME >= %s"

            result = cursor.execute(strSql, (today, today))  # 결과 카운트 == count()

            pm_member = cursor.fetchall()

        except SlackApiError as e:
            logging.Logger.log(e)
            connection.rollback()
            print("Failed !!!!!!!!!!!!!!!!!!!!!!!")
        return pm_member

    def readFilePost(self):
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
        # json 파일 읽어서 보낼 때
        """
        name = employeeList.readFilePost(self)
        sendSlack.postReadFile(name)
        """
        # DB 연결하여 읽을 때
        name = employeeList.readDBPost(self)
        sendSlack.postReadDB(name)
        return Response(status=200, data=dict(challenge=challenge))


class sendSlack():

    """
        postReadDB - DB에서 담당자 확인
        postReadFile - dailyPM_config.json 파일 read 후 확인
    """

    def postReadDB(lst):
        user_token = lst[0][0]
        user_name = lst[0][1]
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        return slack.chat_postMessage(
            channel="C016DHDF0G1"
            # C034YUUS3H6 : chatbot_test2
            # C02HD2Q7DE2 : chatbot_test
            # C016DHDF0G1 : 자사-온라인
            , attachments=[
                {
                    "color": "#3F58FF",
                    "blocks": [
                        {
                            "type": "header",
                            "text": {
                                "type": "plain_text",
                                "text": "일일점검 시간",
                            }
                        },
                        {
                            "type": "section",
                            "fields": [
                                {
                                    "type": "mrkdwn",
                                    "text": "*점검자:*\n" + "<@" + user_token + "> " + user_name + "매니저님"
                                },
                                {
                                    "type": "mrkdwn",
                                    "text": "*점검일:*\n" + today + "\n"
                                },
                                {
                                    "type": "mrkdwn",
                                    "text": "*내용:*\n B2C대량메일 \n KIXX \n 웹쉘솔루션 \n 설문솔루션"
                                },
                                {
                                    "type": "mrkdwn",
                                    "text": "*비고:*\n 빠르게 하고 여유로운 크픠흔즌 \n " + user_name + " 매니저 부재 시 다른 분이 해주세요"
                                }
                            ],
                            "accessory": {
                                "type": "image",
                                "image_url": "https://search.pstatic.net/common?type=ofullfill&size=138x138&fillColor=ffffff&quality=75&direct=true&src=https%3A%2F%2Fboard.jinhak.com%2FBoardV1%2FUpload%2FJob%2FCompany%2FCI%2F243139.jpg",
                                "alt_text": "아이콘"
                            }
                        },
                        {
                            "type": "divider"
                        }
                    ]
                }
            ]
        )

    def postReadFile(lst):
        user_name = lst[0]["name"]
        user_token = lst[0]["member_id"]
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        return slack.chat_postMessage(
            channel="C016DHDF0G1"
            # C034YUUS3H6 : chatbot_test2
            # C02HD2Q7DE2 : chatbot_test
            # C016DHDF0G1 : 자사-온라인
            , attachments=[
                {
                    "color": "#D2B48C",
                    "blocks": [
                        {
                            "type": "header",
                            "text": {
                                "type": "plain_text",
                                "text": "일일점검 시간",
                            }
                        },
                        {
                            "type": "section",
                            "fields": [
                                {
                                    "type": "mrkdwn",
                                    "text": "*점검자:*\n" + "<@" + user_token + "> " + user_name + "매니저님"
                                },
                                {
                                    "type": "mrkdwn",
                                    "text": "*점검일:*\n" + today + "\n"
                                },
                                {
                                    "type": "mrkdwn",
                                    "text": "*내용:*\n B2C대량메일 \n KIXX \n 웹쉘솔루션 \n 설문솔루션"
                                },
                                {
                                    "type": "mrkdwn",
                                    "text": "*비고:*\n 후딱 하고 커피 커피 \n " + user_name + " 매니저 부재 시 다른 분이 해주세요"
                                }
                            ],
                            "accessory": {
                                "type": "image",
                                "image_url": "https://search.pstatic.net/common?type=ofullfill&size=138x138&fillColor=ffffff&quality=75&direct=true&src=https%3A%2F%2Fboard.jinhak.com%2FBoardV1%2FUpload%2FJob%2FCompany%2FCI%2F243139.jpg",
                                "alt_text": "아이콘"
                            }
                        },
                        {
                            "type": "divider"
                        }
                    ]
                }
            ]
        )
