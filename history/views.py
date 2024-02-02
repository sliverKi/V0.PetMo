from django.shortcuts import render
from rest_framework.views import APIView
from .models import History
from .serializers import HistoryListSerializer
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK

class userSearchHistory(APIView):
    def get(self, request):
        user=request.user
        user_search_history = History.objects.filter(user=user).order_by('searched_at')
        serializer=HistoryListSerializer(user_search_history, many=True)
        return Response(serializer.data, status=HTTP_200_OK)
