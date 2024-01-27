from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import PetCategorySerializer
from .models import Pet
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
class Pets(APIView):
    @swagger_auto_schema(
        operation_summary="List all available pets",
        operation_description="Returns a list of all available pets.",
        responses={
            200: "OK",
            401: "Unauthorized",
            403: "Forbidden",
            404: "Not Found",
            500: "Internal Server Error"
        },
    )
    def get(self, request):
        all_pets=Pet.objects.all()
        serializer=PetCategorySerializer(all_pets, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

