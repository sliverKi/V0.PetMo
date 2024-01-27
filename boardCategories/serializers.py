from rest_framework.serializers import ModelSerializer
from rest_framework import status
from .models import Board


class BoardCategorySerializer(ModelSerializer):
    class Meta:
        model = Board
        fields = ("boardCategoryType",)
        read_only=False