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
    address = models.ForeignKey(
        'addresses.Address',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='user_address'
    )
    hasPet=models.BooleanField(default=False)
    pets=models.ManyToManyField(
        "petCategories.Pet",
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

