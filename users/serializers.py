import re
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from rest_framework.exceptions import ParseError,ValidationError
from .models import User
from addresses.models import Address
from pets.serializers import PetsSerializers
from pets.models import Pet
class TinyUserSerializers(ModelSerializer):#내동네 설정에서 이용
    #user 정보 : username, profile, pets, region,/ 작성 글(게시글, [댓글, 대댓글]이 있는 게시글)
    pets= PetsSerializers(many=True)
    regionDepth2=serializers.CharField(source="user_address.regionDepth2", read_only=True)
    regionDepth3=serializers.CharField(source="user_address.regionDepth3", read_only=True)

    class Meta:
        model=User
        fields=(
            "username",
            "profile",
            "pets",
            "regionDepth2",
            "regionDepth3",
        )
class SimpleUserSerializer(ModelSerializer):#MY/Post에서 이용
    #user 정보 : username, profile, pets, region,/ 작성 글(게시글, [댓글, 대댓글]이 있는 게시글)
    regionDepth2=serializers.CharField(source="user_address.regionDepth2", read_only=True)
    regionDepth3=serializers.CharField(source="user_address.regionDepth3", read_only=True)

    class Meta:
        model=User
        fields=(
            "username",
            "profile",
            "regionDepth2",
            "regionDepth3",
        )
class AddressSerializers(serializers.ModelSerializer):#내동네 설정시 이용
    user=TinyUserSerializers(read_only=True)
    class Meta:
        model = Address
        fields = (
            "id",
            "user",#context={'user':user}
            "addressName",
            "regionDepth1", 
            "regionDepth2",
            "regionDepth3",
        )
        extra_kwargs = {"regionDepth3":{"required":False}}
        #필수 필드가 아닌 선택적 필드로 변경 ex)경기도 시흥시 (xx구)
    
    
    def validate(self, attrs):
        
        addressName=attrs.get("addressName")
        regionDepth1=attrs.get("regionDepth1")
        regionDepth2=attrs.get("regionDepth2")

        if not addressName:
           raise ValidationError("전체 주소를 입력해 주세요.")    
        elif not regionDepth1:
            raise ValidationError("시도 단위 주소를 입력해 주세요.")
        elif not regionDepth2:
                raise ValidationError("군,구 단위 주소를 입력해 주세요.")
        else: 
            return attrs     

class AddressSerializer(ModelSerializer):#유저 정적 정보 조회시, 내 동네 조회시 이용
    class Meta:
        model=Address
        fields=(
            "addressName",
            "regionDepth1", 
            "regionDepth2",
            "regionDepth3",
        )
class UserSerializers(ModelSerializer):#정적 정보 조회시 이용
    user_address=AddressSerializer()
    pets=PetsSerializers(many=True)
    class Meta:
        model=User
        fields=(
            "pk", 
            "username", 
            "email",
            "password", 
            "profile", 
            "user_address", #역참조
            "hasPet",
            "pets",
            "first",
        )



class PublicUserSerializer(ModelSerializer):
    class Meta:
        model=User
        fields=(
            "")
class PrivateUserSerializers(ModelSerializer):
    pets=PetsSerializers(many=True)
    regionDepth2=serializers.CharField(source="user_address.regionDepth2", read_only=True)
    regionDepth3=serializers.CharField(source="user_address.regionDepth3", read_only=True)
    class Meta:
        model=User
        fields=(
            "username",
            "profile",
            "pets",
            "regionDepth2",
            "regionDepth3"
            )
        
    def update(self, instance, validated_data):
        #input data
        """ {"username":"eungi",
            "profile":"https://www.lifewithcats.tv/wp-content/uploads/2011/04/Jumping-Cat.jpg",
            "pets":[{"animalTypes":"고양이"}, {"animalTypes":"물고기"}]}
        """
        pets_data = validated_data.pop("pets", None)
        if pets_data is not None:
            if not isinstance(pets_data, list):
                raise serializers.ValidationError(
                    "Pets should be provided as a list of objects"
                )
            if len(pets_data) > 3:
                raise serializers.ValidationError(
                    "A maximum of 3 pets can be selected."
                )
            instance.pets.clear()
            for pet in pets_data:
                animalTypes = pet.get("animalTypes")
                if not animalTypes:
                    raise serializers.ValidationError(
                        "Pet species should be provided."
                    )
                try:
                    pet_obj = Pet.objects.get(animalTypes=animalTypes)
                    instance.pets.add(pet_obj)
                except Pet.DoesNotExist:
                    raise serializers.ValidationError(
                        f"{animalTypes} is not a valid pet species."
                    )
        return super().update(instance, validated_data)
    


class EnrollPetSerailzer(ModelSerializer):
    pets=PetsSerializers(many=True)
    class Meta:
        model=User
        fields=("pets",)
    
    
    
    def create(self, validated_data):
        pets_data=validated_data.pop("pets", None) 
        user = self.context["request"].user
        
        user.pets.clear()
        if len(pets_data)>3:
            raise ValidationError("최대 3마리까지 등록이 가능합니다.")
        
        if isinstance(pets_data, list):
            for pet_data in pets_data:
                pet=get_object_or_404(Pet, animalTypes=pet_data["animalTypes"])
                user.pets.add(pet)
        else:
            raise ValidationError()       
        user.hasPet=True
        user.save()
        return user




class UserProfileUploadSerializer(ModelSerializer):
    class Meta:
        model=User
        fields=("profile",)
    def update(self, instance, validated_data):
        instance.profile = validated_data["profile"]
        instance.save()
        return instance