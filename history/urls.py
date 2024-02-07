from django.urls import path
from . import views

urlpatterns=[
    path("", views.userSearchHistory.as_view(), name="userSearchHistory"),
]