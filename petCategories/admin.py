from django.contrib import admin
from .models import Pet

@admin.register(Pet)
class PetAdmin(admin.ModelAdmin):
    list_display=("id", "animalTypes",)
    list_display_links=("id","animalTypes",)