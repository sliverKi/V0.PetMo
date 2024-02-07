from django.db import models
from common.models import CommonModel


class PostLike(CommonModel):
    user=models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE
    )
    post=models.ForeignKey(
        "posts.Post",
        on_delete=models.CASCADE,
        related_name="postLike"
    )
    unique_together=("user", "post")


    
