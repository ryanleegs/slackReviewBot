# ~/slackbot/views.py
import dateutil
from rest_framework.views import APIView
from rest_framework.response import Response
from slack_sdk import WebClient

import datetime
from google_play_scraper import app, Sort, reviews, reviews_all

import requests
import templates.Consts as const
from dateutil import parser

# 슬랙 세팅
slack = WebClient(token=const.slackToken)


def android_review(review_id, review_code):
    result = reviews_all(
        review_id,
        lang='ko',  # defaults to 'en'
        country='kr',  # defaults to 'us'
        sort=Sort.NEWEST,  # defaults to Sort.MOST_RELEVANT
        count=30,  # defaults to 100
        # filter_score_with=3  # defaults to None(means all score)
    )
    today = datetime.datetime.now()
    _yesterday = (today - datetime.timedelta(days=1)).strftime("%Y-%m-%d")
    yesterday = datetime.datetime.strptime(_yesterday, "%Y-%m-%d")
    for index, googleList in enumerate(result):
        reg_dtime = googleList["at"]
        googleList["app_title"] = review_code
        # 어제기준 리뷰 노출
        if reg_dtime > yesterday:
            reviewList = []
            reviewList.append(googleList)
            sendSlack.send(reviewList, "ANDROID")


def iOS_review(review_id, review_code):
    ios_rank_url = sendIosMessage.getUrl(review_id)
    response = requests.get(ios_rank_url)

    response_data = response.json()
    ios_app_list = response_data["feed"]["entry"]

    today = datetime.datetime.now()
    _yesterday = (today - datetime.timedelta(days=1)).strftime("%Y-%m-%d")
    yesterday = datetime.datetime.strptime(_yesterday, "%Y-%m-%d")

    for index, iosList in enumerate(ios_app_list):
        _reg_dtime = iosList["updated"]["label"]
        _reg_dtime_str = dateutil.parser.isoparse(_reg_dtime).strftime("%Y-%m-%d %H:%M:%S")
        reg_dtime = datetime.datetime.strptime(_reg_dtime_str, "%Y-%m-%d %H:%M:%S")

        if reg_dtime > yesterday:
            iosList["title"] = {"label": review_code}
            reviewList = [iosList]

            sendSlack.send(iosList, "IOS")


class reviewPost(APIView):

    def post(self, request):
        challenge = request.data.get('challenge')
        review_code = request.GET.get('review_code', '')

        phone_type = request.GET.get('phone_type', 'ALL')

        if review_code == "EV":
            review_text = "com.gscaltex.energyplusev"

        elif review_code == "EP":
            review_text = "com.gscaltex.energyplus"

        elif review_code == "GSNPT":
            review_text = "kr.co.gscaltex.gsnpoint"

        # Android
        android_review(review_text, review_code)
        # iOS
        iOS_review(review_code, review_code)

        return Response(status=200, data=dict(challenge=challenge))


#
# class Api(APIView):
#
#     def post(self, request):
#         """
#         슬랙에서 채팅 이벤트가 있을 때 호출하는 API
#         :param request:
#         :return:
#         """
#         print(request.body)
#         # body에서 challenge 필드만 빼오기
#
#         # 슬랙 이벤트 requestUrl post호출시 반드시 넘겨줘야 하는 챌리지 값
#         challenge = request.data.get('challenge')
#
#         # 봇인지 팀원인지 구분
#         user = request.data.get('event').get('user')
#         # 입력되는 텍스트
#         text = request.data.get('event').get('text')
#
#         # 텍스트 입력이 들어올 때 체크
#         if text is not None:
#
#             if user == 'U02HGPVMZ7F':
#                 print("봇이 전달하는 메세지")
#                 # slack.chat_postMessage(
#                 #     channel="#chatbot_test"
#                 #     , blocks=[
#                 #         {
#                 #             "type": "section",
#                 #             "text": {
#                 #                 "type": "mrkdwn",
#                 #                 "text": "나에요 나 : "
#                 #             }
#                 #         }
#                 #     ]
#                 # )
#                 # if text == "명령어":
#             else:
#                 print("사용자가 입력한 메세지", text)
#                 try:
#                     #   reviewPost.google(self, request)
#                     try:
#                         reviewPost.ios(self, request)
#                     finally:
#                         print("dd")
#                 finally:
#                     print("dd")
#
#         return Response(status=200, data=dict(challenge=challenge))
#

class sendIosMessage():
    def getUrl(text):
        urlData = {
            "EP": const.energyplusIosUrl,
            "EV": const.energyplusEvIosUrl,
            "GSNPT": const.gsnpointIosUrl,
        }
        return urlData.get(text)

    def getImgUrl(text):
        imgUrlData = {
            "EP": "https://play-lh.googleusercontent.com/brnsmY_M7QjBj_hYYAJv8yxE8zTtiNUyQd_f8xtmMVpR85Ppwvbgi6bZ-vD2FzH4TQ",
            "EV": "https://play-lh.googleusercontent.com/9ciBq2zI6py_VxAYsGNvKKKygRyxFXbg8gb21i-ToYkQ-Yj38R3XMCvQifZZLnZbuQ",
            "GSNPT": "https://play-lh.googleusercontent.com/1xpLr9sOnAKLT7279VkX-5y_f9Y1P8cvgGu9Pfr84hwGjawy-h58DPDb2K8YiQc1LVA",
        }
        return imgUrlData.get(text)


class sendSlack:

    def send(rlist, text):

        if text in "IOS":
            title = "iOS 앱 리뷰"
            content = rlist["content"]["label"]
            avg = rlist["im:rating"]["label"]
            avg_star = ":star:" * int(avg)
            if int(avg) < 3:
                color = "#ff0000"
            elif int(avg) == 3:
                color = "#f2c744"
            elif int(avg) > 3:
                color = "#00ff80"
            review_name = rlist["author"]["name"]["label"]
            review_uri = rlist["author"]["uri"]["label"]
            img_url = sendIosMessage.getImgUrl(rlist["title"]["label"])
            reg_date = dateutil.parser.isoparse(rlist["updated"]["label"]).strftime("%Y-%m-%d %H:%M:%S")

        elif text in "ANDROID":
            title = "안드로이드 앱 리뷰"
            content = rlist[0]["content"]
            avg = rlist[0]["score"]
            avg_star = ":star:" * avg
            if int(avg) < 3:
                color = "#ff0000"
            elif int(avg) == 3:
                color = "#f2c744"
            elif int(avg) > 3:
                color = "#00ff80"
            review_name = rlist[0]["userName"]
            review_uri = rlist[0]["userImage"]
            img_url = sendIosMessage.getImgUrl(rlist[0]["app_title"])
            reg_date = datetime.datetime.strftime(rlist[0]["at"], "%Y-%m-%d %H:%M:%S")

        return slack.chat_postMessage(
            channel="C034SUVQCS1"
            , attachments=[
                {
                    "color": color,
                    "blocks": [
                        {
                            "type": "header",
                            "text": {
                                "type": "plain_text",
                                "text": title,
                            }
                        },
                        {
                            "type": "section",
                            "fields": [
                                {
                                    "type": "mrkdwn",
                                    "text": "*등록자:*\n" + review_name + "\n"
                                },
                                {
                                    "type": "mrkdwn",
                                    "text": "*Date:*\n" + reg_date + "\n"
                                },
                                {
                                    "type": "mrkdwn",
                                    "text": "*내용:*\n" + content
                                },
                                {
                                    "type": "mrkdwn",
                                    "text": "*평점:*\n" + avg_star
                                }
                            ],
                            "accessory": {
                                "type": "image",
                                "image_url": img_url,
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
