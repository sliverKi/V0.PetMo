from .models import History
from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
class HistoryListSerializer(ModelSerializer):
    user = serializers.CharField(source="user.username")
    class Meta:
        model=History
        fields=("user", "query", "searched_at",)
