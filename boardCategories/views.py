from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Board
from .serializers import BoardCategorySerializer

class Categories(APIView):
    def get(self, request):
        all_categories=Board.objects.all()
        serializer=BoardCategorySerializer(all_categories, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)