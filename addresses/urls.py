from django.contrib import admin
from django.urls import path
from . import views 
from config.searchlimit import searchRateLimiterMiddleware
urlpatterns=[
    path("", views.getAddress.as_view()),#[POST, PUT, DELETE] 사용자가 등록한 동네 조회, 삭제, POST] +)+)동네 재설정 추가, 동네 삭제[PUT]
    path("get/ip", views.getIP.as_view()), #user 현 위치의 동네 조회[GET]
    path("get/query", searchRateLimiterMiddleware(views.getQuery.as_view())), #검색어 기반 동네 조회 [GET]
]