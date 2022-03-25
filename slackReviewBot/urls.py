"""slackReviewBot URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
# ~/untitled4/urls.py
# untitled4는 프로젝트명 입니다.

from django.contrib import admin
from django.urls import path
from slackbot import views
import dailyPM.views as dailyPM
import api.views as api
import mobileTeam.views as mobile
# 새로만든 앱 'slackbot'에서 views.py를 import합니다.

urlpatterns = [
    path('admin/', admin.site.urls),    # 이건 원래 있던거
    path('', api.Api.as_view()),        # slack Event Subscriptions 전용
   # path('api', views.Api.as_view()),
    path('review', views.reviewPost.as_view()),
    path('dailyPm', dailyPM.dailyPost.as_view()),
    path('mobileTeam', mobile.mobileTeamList.as_view()),
    path('secretaryManagerList', mobile.secretaryManagerList.as_view()),
    path('drawUpWeekly', dailyPM.drawUpWeekly.as_view()),
]