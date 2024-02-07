from django.db import models

class Board(models.Model):
    class BoardKindChoices(models.TextChoices):
        
        자유="자유","자유"
        반려질문="반려질문", "반려질문"
        반려고수="반려고수","반려고수"
        장소후기="장소후기","장소후기"
        축하해요="축하해요","축하해요"
        반려구조대="반려구조대","반려구조대"
        
    boardCategoryType = models.CharField(
        max_length=255,
        choices=BoardKindChoices.choices,
    )
    def __str__(self) -> str:
        return self.boardCategoryType

    
