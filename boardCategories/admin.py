from django.contrib import admin
from .models import Board
@admin.register(Board)
class BoardAdmin(admin.ModelAdmin):
    list_display=("id","boardCategoryType",)
    list_display_link=("id","boardCategoryType",)
