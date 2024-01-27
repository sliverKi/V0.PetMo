from .models import Address
from rest_framework.serializers import ModelSerializer

class AddressSerializer(ModelSerializer):
    class Meta:
        model = Address
        fields = ['regionDepth2']
