from django.db import models
from users.models import User

class Address(models.Model):
   
    user=models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        related_name="user_address"
    )
    addressName=models.CharField(max_length=255,)

    regionDepth1=models.CharField(max_length=255,default="")
    regionDepth2=models.CharField(max_length=255,default="",  db_index=True)
    regionDepth3=models.CharField(max_length=255,default="", blank=True, null=True)
    
    def __str__(self) -> str:
        return self.addressName 
    
