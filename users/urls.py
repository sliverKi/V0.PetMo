from django.contrib import admin
from django.urls import path
from . import views 

urlpatterns=[
    path("static-info", views.StaticInfo.as_view()),#사용자 정적 정보 조회
    
    path("MY/Post", views.MyPost.as_view()), #user작성한 게시글 조회[GET]
    path("MY/Post/<int:pk>", views.MyPostDetail.as_view()), #[get, put, delete]   
    
    path("MY/Comment", views.MyComment.as_view()),#user작성한 댓글 조회[GET]
    path("MY/Comment/<int:pk>", views.MyCommentDetail.as_view()), #댓글 조회 하면 게시글을 보여줄 수 있게 변경해야 함 [수정 필요]
    
    path("my-info", views.MyInfo.as_view()), #user profile 수정 [GET, PUT](ok) 
    path('upload-profile/', views.UserProfileUploadView.as_view(), name='upload-profile-S3'),

    path("animals", views.getPets.as_view()),#[GET, POST]
    path("withdrawal", views.Quit.as_view()),#[DELETE]
]

#처리된 url 손봐야 함.