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

import templates.Constants as const
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


class lunch_menu(APIView):

    def post(self, request):
        challenge = request.data.get('challenge')

        return Response(status=200, data=dict(challenge=challenge))


class greeat(APIView):
    def get_content(self):
        # get_content() #현재 선택된 항목을 읽어온다.
        # return [URL, 게시글, 올린 날짜, 좋아요 개수, 지정 위치, 해쉬태그] ################################################
        # 1. 현재 페이지의 HTML 정보 가져오기
        html = self.driver.page_source
        soup = BeautifulSoup(html, 'lxml')
        ################################################
        ### 2. 본문 내용 가져오기
        try:  # 여러 태그중 첫번째([0]) 태그를 선택
            strInstaId = soup.select('div.e1e1d')[0].text
        except:
            strInstaId = ' '
            contentTmp = str()

            # 여러 태그중 첫번째([0]) 태그를 선택
            try:
                content2 = soup.select('div.C4VMK > span')[0]
                for contentDetail in content2.contents:
                    # 공백, 스페이스 1번을 없애주기위해서.. len을 넣은 이유는 공백과 스페이스바를 추가해도 분기 무시를 안하는 경우가 있어서!
                    if (type(contentDetail).__name__ is "NavigableString"):
                        if contentDetail is not "" and contentDetail is not " " and len(contentDetail) is not 1 and len(
                                contentDetail) is not 0:
                            contentTmp += contentDetail + "\t"
                        elif (type(contentDetail).__name__ is "Tag"):
                            # 첫 게시글 본문 내용이 <div class="C4VMK"> 임을 알 수 있다. #태그명이 div, class명이 C4VMK인 태그 아래에 있는 span 태그를 모두 선택.
                            if contentDetail.text is not "" and contentDetail.text is not " ":
                                contentTmp += contentDetail.text + "\t"
            except:
                content2 = ' '
            ################################################ # 3. 본문 내용에서 해시태그 가져오기(정규표현식 활용)

            # content 변수의 본문 내용 중 #으로 시작하며, #뒤에 연속된 문자(공백이나 #, \ 기호가 아닌 경우)를 모두 찾아 tags 변수에 저장 # 4. 작성 일자 가져오기
            tags = re.findall(r'#[^\s#,\\]+', contentTmp)
            # 앞에서부터 10자리 글자

            try:
                date = str(soup.select('time._1o9PC.Nzb55')[0]['datetime'])
            except:
                date = ''

            TIdx = date.find('T')
            dateValue = date[0:TIdx] + " " + date[TIdx + 1:TIdx + 9]  # 5. 좋아요 수 가져오기

            try:
                strTemp = str(soup.select('div.Nm9Fw > button')[0].text)
                strTemp = strTemp.replace(",", "");
                strTemp = strTemp.replace("외", "");
                strTemp = strTemp.replace("명", "");
                strTemp = strTemp.replace(" ", "");
                like = strTemp
            except:
                like = 0
            # 6. 위치 정보 가져오기
            try:
                place = str(soup.select('div.JF9hh')[0].text)
            except:
                place = ''
                data = [self.driver.current_url, strInstaId, contentTmp, dateValue, like, place, tags]
        return data
