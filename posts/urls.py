from django.urls import path
from . import views

urlpatterns=[
    path("", views.Posts.as_view(), name="get_postlist_by_categories"),
    path("write/", views.makePost.as_view(), name="make_new_post"),#[GET,POST, pagination]
    path("<int:pk>", views.PostDetail.as_view()),#[GET, PUT(게시글 수정), DELETE]
    
    path("<int:pk>/comments", views.PostComments.as_view()),#[GET, POST(댓글,대댓글 등록가능), pagination]
    path("<int:pk>/comments/<int:comment_pk>", views.PostCommentsDetail.as_view()), #[GET, PUT(댓글 대댓글 수정, DELETE]
    
    #[ api문서 작성 x]    
    path("comments/", views.Comments.as_view()), #[GET, POST, pagination]
    path("comments/<int:pk>", views.CommentDetail.as_view()),#[GET,PUT(댓글만 수정 가능),DELETE]

    path("trigger_error",views.trigger_error),
   

]
# pagination 적용 확인해봐야 함. 
# 게시글 : 10개 pagination, 댓글: 5개 pagination