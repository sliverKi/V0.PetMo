from django.contrib import admin
from .models import Post, Comment

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display=("id","user","post","content",)
    list_display_links=("id","user","post","content",)
    search_fields=("user",)


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display=("id","categoryType", "author","address", "content","createdDate")
    list_display_links=("id","author", "content")
    search_fields=("categoryType","boardAnimalTypes", "author",)
