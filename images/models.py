from django.db import models
from common.models import CommonModel

class Image(CommonModel):
    post=models.ForeignKey(
        "posts.Post",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="images"
    )
    img_path=models.URLField()
