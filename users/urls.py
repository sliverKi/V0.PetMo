from django.contrib import admin
from django.urls import path
from . import views 

urlpatterns=[
    path("static-info", views.StaticInfo.as_view()),#사용자 정적 정보 조회
    
    path("MY/Post", views.MyPost.as_view()), #user작성한 게시글 조회[GET]
    path("MY/Post/<int:pk>", views.MyPostDetail.as_view()), #[get, put, delete] put : boardanimaltype : 필수  
    
    path("MY/Comment", views.MyComment.as_view()),#user작성한 댓글 조회[GET]
    path("MY/Comment/<int:pk>", views.MyCommentDetail.as_view()), #댓글 수정 삭제 해야함
    
    path("my-info", views.MyInfo.as_view()), #user profile 수정 [GET, PUT](ok) 
    
    path("address/", views.getAddress.as_view()),#[POST, PUT, DELETE] 사용자가 등록한 동네 조회, 삭제, POST] +)+)동네 재설정 추가, 동네 삭제[PUT]
    path("address/get/ip", views.getIP.as_view()), #user 현 위치의 동네 조회[GET]
    path("address/get/query", views.getQuery.as_view()), #검색어 기반 동네 조회 [GET]

    path("animals", views.getPets.as_view()),#[GET, POST]
    path("withdrawal", views.Quit.as_view()),#[DELETE]
]

#처리된 url 손봐야 함.
#3,5번 만들어야 해 