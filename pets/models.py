from django.db import models

class Pet(models.Model):
    
    class AnimalSpeciesChoices(models.TextChoices):
        강아지="강아지", "강아지"
        고양이="고양이","고양이"
        물고기="물고기","물고기"
        햄스터="햄스터","햄스터"
        파충류="파충류","파충류"
        토끼="토끼","토끼"
        새="새", "새"
        other="기타","기타",
        전체="전체", "전체"
    
    animalTypes=models.CharField(
        max_length=255,
        choices=AnimalSpeciesChoices.choices,
    )
    def __str__(self) -> str:
        return self.animalTypes