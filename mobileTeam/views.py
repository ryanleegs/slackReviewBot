import json

from bs4 import BeautifulSoup
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from rest_framework.views import APIView
from rest_framework.response import Response
from slack_sdk import WebClient

import re
import datetime
from datetime import date, timedelta

import templates.Consts as const
from django.db import connection

# 슬랙 세팅
from slackReviewBot import settings

slack = WebClient(token=const.slackToken)


class mobileTeamList(APIView):
    def post(self, request):
        # try:
        #     cursor = connection.cursor()
        #
        #     today = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        #
        #     strSql = "SELECT * FROM gsitmmobile.employee_info WHERE start_dt <= %s AND end_dt >= %s"
        #     teamlist = slack.team_profile_get()
        #     print("teamlist ====>",teamlist)
        #     result = cursor.execute(strSql, (today, today))  # 실행 여부 성공 1 실패 0 ?
        #     nlist = cursor.fetchall()
        #
        #     connection.commit()
        #     connection.close()
        #
        # except:
        #     connection.rollback()
        #     print("Failed !!!!!!!!!!!!!!!!!!!!!!!")
        # return nlist

        challenge = request.data.get('challenge')

        usr = slack.users_list()

        # for index, memList in enumerate(usr):
        #     mem_list = list(memList["members"])
        #     print(mem_list[index])

        return Response(status=200, data=dict(challenge=challenge))


class secretaryManagerList(APIView):
    def post(self, request):
        challenge = request.data.get('challenge')
        today = date.today()
        # C02TN889Q6N 간사매니저 채널 아이디 / C02HD2Q7DE2 - 챗봇테스트 채널 아이디
        # channel = "C02TN889Q6N"
        # 1월 U01JZDEFMRQ - 박다솜 / U027QTQQS75 - 김우영
        # 2월 U020C787MC1 - 최윤서 / U02S0572ULA - 장대현
        # 3월 U027QMQD0R0 - 이승준 / U01HSRSB0BY - 권형조
        # 4월 U027MN9MDPX - 강명묵 / U02CR9LGB6F - 최문식
        # 5월 U02QWHYUXC7 - 김대연 /  - 차승욱
        # 6월 U02RB6EM5RQ - 이승찬 / U02GG41PHPG - 차수연
        # 7월 U015KNW3CKZ - 김희진 / U01HSRSB0BY - TBD
        # 8월 U01JZDEFMRQ - 박다솜 / U027QTQQS75 - 김우영
        # 9월 U02S0572ULA - 장대현 / U020C787MC1 - 최윤서
        # 10월 U027QMQD0R0 - 이승준 / U01HSRSB0BY - 권형조
        # 11월 U027MN9MDPX - 강명묵 / U02CR9LGB6F - 최문식
        # 12월 U02QWHYUXC7 - 김대연 /  - 차승욱

        # test U031YS3HYFP - 박민규 / U02QWHYUXC7 - 김대연

        with open('templates/member_config.json', 'r', encoding='utf-8') as f:
            member_data = json.load(f)

        month = date.today().month
        month_ago = (today.replace(day=1) - timedelta(days=1)).month

        for mem_data in member_data["member"]:
            mem_mth = mem_data["secretary_month"]

            if mem_mth == month:
                invite_member = [mem_data["member_id"]]
                for mem_list in invite_member:
                    slack.conversations_invite(token=const.slackToken, channel="C02HD2Q7DE2", users=mem_list)
            if mem_mth == month_ago:
                kick_member = [mem_data["member_id"]]
                for mem_list in kick_member:
                    slack.conversations_kick(token=const.slackToken, channel="C02HD2Q7DE2", user=mem_list)

        return Response(status=200, data=dict(challenge=challenge))
