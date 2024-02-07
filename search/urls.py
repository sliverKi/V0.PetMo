from django.urls import path
from . import views

urlpatterns=[
    path("<str:query>", views.SearchPost.as_view())    
]
