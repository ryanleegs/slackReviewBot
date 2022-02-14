# ~/slackbot/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from slack_sdk import WebClient

import datetime
from google_play_scraper import app, Sort, reviews, reviews_all

import requests
import templates.Constants as const
import json

from django.core.serializers.json import DjangoJSONEncoder

# 슬랙 세팅
slack = WebClient(token=const.slackToken)


class reviewPost(APIView):

    def post(self, request, idx=0):
        challenge = request.data.get('challenge')
        result = reviews_all(
            'com.gscaltex.energyplus',
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
            # 어제기준 리뷰 노출
            if reg_dtime > yesterday:
                reviewList = []
                reviewList.append(googleList)
                sendSlack.send(reviewList, "ANDROID")

        return Response(status=200, data=dict(challenge=challenge))
        # If you pass `continuation_token` as an argument to the reviews function at this point,
        # it will crawl the items after 3 review items.

    def ios(self, request, idx=0):
        challenge = request.data.get('challenge')
        ios_rank_url = sendIosMessage.getUrl("에너지플러스")
        print("ios_rank_url ===>", ios_rank_url)
        response = requests.get(ios_rank_url)
        print("response ===>", response)

        response_data = response.json()
        ios_app_list = response_data["feed"]["entry"]

        for index, reviewList in enumerate(ios_app_list):
            rank = index + 1
            title = reviewList["title"]["label"]
            content = reviewList["content"]["label"]
            avg = reviewList["im:rating"]["label"]
            avg_star = ":star:" * int(avg)
            if int(avg) < 3:
                color = "#ff0000"
            elif int(avg) == 3:
                color = "#f2c744"
            elif int(avg) > 3:
                color = "#00ff80"
            review_name = reviewList["author"]["name"]["label"]
            review_uri = reviewList["author"]["uri"]["label"]
            review_id = str.replace(review_uri, "https://itunes.apple.com/kr/reviews/", "")
            reg_dtime = reviewList["updated"]["label"]
            # reg_date = datetime.fromisoformat(reg_dtime).strftime("%Y-%m-%d %H:%M:%S")

            sendSlack.send(reviewList, "IOS")

        return Response(status=200, data=dict(challenge=challenge))
        # If you pass `continuation_token` as an argument to the reviews function at this point,
        # it will crawl the items after 3 review items.


class Api(APIView):

    def post(self, request):
        """
        슬랙에서 채팅 이벤트가 있을 때 호출하는 API
        :param request:
        :return:
        """
        print(request.body)
        # body에서 challenge 필드만 빼오기

        # 슬랙 이벤트 requestUrl post호출시 반드시 넘겨줘야 하는 챌리지 값
        challenge = request.data.get('challenge')

        # 봇인지 팀원인지 구분
        user = request.data.get('event').get('user')
        # 입력되는 텍스트
        text = request.data.get('event').get('text')

        # 텍스트 입력이 들어올 때 체크
        if text is not None:

            if user == 'U02HGPVMZ7F':
                print("봇이 전달하는 메세지")
                # slack.chat_postMessage(
                #     channel="#chatbot_test"
                #     , blocks=[
                #         {
                #             "type": "section",
                #             "text": {
                #                 "type": "mrkdwn",
                #                 "text": "나에요 나 : "
                #             }
                #         }
                #     ]
                # )
                # if text == "명령어":
            else:
                print("사용자가 입력한 메세지", text)
                try:
                    #   reviewPost.google(self, request)
                    try:
                        reviewPost.ios(self, request)
                    finally:
                        print("dd")
                finally:
                    print("dd")

        return Response(status=200, data=dict(challenge=challenge))


class sendIosMessage():
    def getUrl(text):
        urlData = {
            "에너지플러스": const.energyplusIosUrl,
            "EV": const.energyplusEvIosUrl,
            "GSPOINT": const.gsnpointIosUrl,
        }
        return urlData.get(text)

    def send(text):

        ios_rank_url = sendIosMessage.getUrl(text)

        response = requests.get(ios_rank_url)

        response_data = response.json()
        ios_app_list = response_data["feed"]["entry"]

        for index, ios_app in enumerate(ios_app_list):
            rank = index + 1
            title = ios_app["title"]["label"]
            content = ios_app["content"]["label"]
            avg = ios_app["im:rating"]["label"]
            avg_star = ":star:" * int(avg)
            if int(avg) < 3:
                color = "#ff0000"
            elif int(avg) == 3:
                color = "#f2c744"
            elif int(avg) > 3:
                color = "#00ff80"
            review_name = ios_app["author"]["name"]["label"]
            review_uri = ios_app["author"]["uri"]["label"]
            review_id = str.replace(review_uri, "https://itunes.apple.com/kr/reviews/", "")
            reg_dtime = ios_app["updated"]["label"]
            reg_date = datetime.fromisoformat(reg_dtime).strftime("%Y-%m-%d %H:%M:%S")

            ## TODO 추후 1시간 씩 배치돌면서 시간 내 항목 존재 시 post_message
            sendSlack(ios_app, "IOS")
            slack.chat_postMessage(
                channel="#chatbot_test"
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
                                        "text": "*평점:*\n" + avg_star + "(" + avg + ")"
                                    }
                                ],
                                "accessory": {
                                    "type": "image",
                                    "image_url": "https://www.gscaltex.com/images/common/future/ci_signature_ve.png",
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
            if index == 9:
                break


class getReview():
    """
        iOS
        ios는 리뷰 목록을 json으로 제공
    """

    def getIos(self, txt):
        print("ios")

    """
        Android    
        android는 리뷰 제공해주는 api가 없기 때문에 별도 크롤링 작업 진행
    """

    def getAndroid(self, txt):
        print("android")


class sendSlack():

    def send(rlist, text):

        if text in "IOS":
            title = rlist["title"]["label"]
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
            review_id = str.replace(review_uri, "https://itunes.apple.com/kr/reviews/", "")
            reg_dtime = rlist["updated"]["label"]
            print("reg_dtime ==>", type(reg_dtime))
            reg_date = "22222222"
        # reg_date = datetime.datetime.strftime(reg_dtime, "%Y-%m-%d %H:%M:%S")

        elif text in "ANDROID":
            title = rlist[0]["userName"]
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
            review_id = str.replace(review_uri, "https://itunes.apple.com/kr/reviews/", "")
            reg_date = datetime.datetime.strftime(rlist[0]["at"], "%Y-%m-%d %H:%M:%S")
            # reg_date = datetime.fromisoformat(reg_dtime).strftime("%Y-%m-%d %H:%M:%S")

        return slack.chat_postMessage(
            channel="#chatbot_test"
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
                                "image_url": "https://www.gscaltex.com/images/common/future/ci_signature_ve.png",
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
