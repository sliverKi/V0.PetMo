from django.contrib import admin
from .models import History

@admin.register(History)
class HistoryAdmin(admin.ModelAdmin):
    list_display=("id","user","query","searched_at",)
    list_display_links=("id","user","query","searched_at",)
    search_fields=("user","query", "searched_at",)