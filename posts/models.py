from django.db import models
from common.models import CommonModel

class Post(CommonModel):
    author=models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        related_name="posts"
    )
    address=models.ForeignKey(
        "addresses.Address",
        on_delete=models.SET_NULL,
        null=True,
        unique=False,
        related_name="post_address"
    )
    content=models.TextField(
        max_length=550,
        blank=True,
        null=True,
    )
    boardAnimalTypes=models.ManyToManyField(
        "petCategories.Pet",
        related_name="posts",
    )
    categoryType=models.ForeignKey(
        "boardCategories.Board",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="posts",
    )
    viewCount=models.PositiveIntegerField( # 조회수
        default=0,
        editable=False,
    )
    postImage=models.URLField(
        blank=True, 
        null=True, 
    )

    @property
    def likeCount(self):
        return self.postLike.count()
    
    @property
    def commentCount(self):
        return self.post_comments.filter(parent_comment=None).count()
    
    @property
    def bookmarkCount(self):
        return self.bookmarks.count()
    
    def __str__(self):
        return f"{self.author} - {self.content}"
    


class Comment(CommonModel):
    user=models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        help_text="댓글 작성자의 pk"
    )    
    post=models.ForeignKey(
        "posts.Post",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="post_comments",
        help_text="댓글이 달릴 게시글의 pk"
    )
    content=models.CharField(#댓글 작성
        max_length=150,
        blank=True,
        null=True,
        help_text="댓글 내용"
    )
    parent_comment=models.ForeignKey(#parent_comment에 값이 있으면 대댓글, 값이 없으면 댓글 
        "self",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="replies",
        help_text="댓글 인지 대댓글인지 구분 토글, if parent_comment==null: 댓글, else: 대댓글"
    )
   
    def __str__(self):
        return f"{self.user} - {self.content}"
    