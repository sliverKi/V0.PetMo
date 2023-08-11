from django.db import models
import datetime
class CommonModel(models.Model):
    print("Common Model")
    createdDate = models.DateTimeField(
        auto_now_add=True,
    ) 
    updatedDate = models.DateTimeField(
        auto_now=True,
    )  
    
    class Meta: 
        abstract = True

   
    
   
    
   
