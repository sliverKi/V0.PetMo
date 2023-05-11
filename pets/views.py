from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import PetsSerializers
from .models import Pet

class Pets(APIView):
    def get(self, request):
        all_pets=Pet.objects.all()
        serializer=PetsSerializers(all_pets, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

