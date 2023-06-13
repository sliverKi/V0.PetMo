from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from .manager import UserManager
from django.core.validators import MinLengthValidator
class User(AbstractUser):

    # username_validator = UnicodeUsernameValidator()

    username = models.CharField(#닉네임
        _("username"),
        max_length=255,
        blank=True,
        unique=True,
        validators=[MinLengthValidator(2, "닉네임은 2자 이상이어야 합니다.")],
        error_messages={"unique":"이미 사용중인 닉네임 입니다."}
    )
    email = models.EmailField(
        _("email_address"),
        max_length=255,
        unique=True,
        error_messages={"unique":"이미 사용중인 이메일 입니다."},
    )
    profile=models.URLField(
        blank=True,
        null=True,
    )
    # address=models.ForeignKey(
    #     "users.Address",
    #     max_length=255,
    #     null=True,
    #     blank=True, 
    #     on_delete=models.SET_NULL,
    #     related_name="users"
    # )
    hasPet=models.BooleanField(default=False)
    pets=models.ManyToManyField(
        "pets.Pet",
        blank=True,
        related_name="user_pets"
    )

    first=models.BooleanField(default=True)

    is_staff = models.BooleanField(
        _("staff status"),
        default=False,
    )
    is_active = models.BooleanField(
        _("active"),
        default=True,
    )
    dated_joined = models.DateTimeField(
        _("dated_joined"),
        default=timezone.now,
    )
    
    objects = UserManager()

    USERNAME_FIELD = "email"
    EMAIL_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def __str__(self) -> str:
        return self.username

class Address(models.Model):
   
    user=models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="user_address"
    )
    addressName=models.CharField(max_length=255,)

    regionDepth1=models.CharField(max_length=255,default="")
    regionDepth2=models.CharField(max_length=255,default="")
    regionDepth3=models.CharField(max_length=255,default="")
    
    def __str__(self) -> str:
        return self.addressName 