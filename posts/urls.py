from django.urls import path
from . import views

urlpatterns=[
    path("", views.v1Posts.as_view(), name="v1Posts"),
    path("post2/", views.v2_Posts.as_view(), name="optimized_postList"),#GET[Done], #POST[]
    path("post3/", views.v3_Posts.as_view(), name="use subQuery, annotate"),
    path("write/", views.makePost.as_view(), name="make_new_post"),#[GET,POST, pagination]
    
    
    path("<int:pk>", views.PostDetail.as_view()),#[GET, PUT(게시글 수정), DELETE]
    
    path("<int:pk>/comments", views.PostComments.as_view()),#[GET, POST(댓글,대댓글 등록가능), pagination]
    path("<int:pk>/comments/<int:comment_pk>", views.PostCommentsDetail.as_view()), #[GET, PUT(댓글 대댓글 수정, DELETE]
    
     
    path("comments/", views.Comments.as_view()), #[GET, POST, pagination]
    path("comments/<int:pk>", views.CommentDetail.as_view()),#[GET,PUT(댓글만 수정 가능),DELETE]

    path("trigger_error",views.trigger_error),
]
