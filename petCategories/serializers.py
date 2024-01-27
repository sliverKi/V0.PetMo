from rest_framework.serializers import ModelSerializer
from rest_framework import status
from rest_framework.exceptions import ParseError, ValidationError
from .models import Pet

class PetCategorySerializer(ModelSerializer):
    class Meta:
        model=Pet
        fields=("animalTypes",)
        read_only=False

    def validate_animalTypes(self, animalTypes):
        if not isinstance(animalTypes, str):
            raise ValidationError('유효한 동물 종류가 아닙니다.')
        return animalTypes
    