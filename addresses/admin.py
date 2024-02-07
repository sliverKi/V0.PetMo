from django.contrib import admin
from .models import Address

@admin.register(Address)
class PostLikeAdmin(admin.ModelAdmin):
    list_display=("id",  "user", "addressName", "regionDepth1", "regionDepth2", "regionDepth3")