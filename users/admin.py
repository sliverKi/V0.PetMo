from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User, Address

@admin.register(User)

class MyUserAdmin(UserAdmin):
    fieldsets = (
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
                "classes": ("collapse",),
            },
        ),
        (
            None,
            {
                "fields": (
                    
                    "email",
                    "username",
                    "password",
                    "hasPet",
                    "pets",
                    "first",
                    # "address",
                    "profile",
                )
            },
        ),
        (
            _("Important dates"),
            {
                "fields": (
                    "last_login",
                    "dated_joined",
                ),
                "classes": ("collapse",),
            },
        ),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "password1", "password2",),
            },
        ),
    )
    list_display = (
        "pk",
        "username",
        "email",
        "hasPet",
        # "address",
        "is_staff",
    )
    list_display_links=('pk', 'username')
    list_filter = ("username",)
    search_fields = ("email", "username")
    ordering = ("username",)


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display=('pk', 'user', 'addressName', 'regionDepth1', 'regionDepth2', 'regionDepth3')
    list_display_links=('pk', 'user', 'addressName', 'regionDepth1', 'regionDepth2', 'regionDepth3')



    


