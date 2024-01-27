from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from rest_framework.pagination import CursorPagination
from rest_framework.exceptions import ParseError, ValidationError
from rest_framework.response import Response
from rest_framework import status


from users.serializers import TinyUserSerializers, SimpleUserSerializer, V2_PostAuthorSerializer
from .models import Post,Comment

from boardCategories.models import Board
from boardCategories.serializers import BoardCategorySerializer
from petCategories.models import Pet
from petCategories.serializers import PetCategorySerializer
from likes.models import PostLike
from bookmarks.models import Bookmark
from search.documents import PostDocument
from django_elasticsearch_dsl_drf.serializers import DocumentSerializer
import sys

from django.db import transaction
sys.setrecursionlimit(100000)

# from django_elasticsearch_dsl_drf.serializers import DocumentSerializer


class CommentSerializers(ModelSerializer):
    author=SimpleUserSerializer(read_only=True)
    class Meta:
        model=Comment
        fields=( 
            "pk",
            "parent_comment",
            "post",  
            "author",
            "content",
            "createdDate",
            "updatedDate"
        ) 
class ReplySerializers(ModelSerializer):
    children=serializers.SerializerMethodField()
    author=SimpleUserSerializer(read_only=True)
    
    class Meta:
        model=Comment
        fields=(
            "id",
            "parent_comment",
            "post",  
            "author",
            "content",
            "createdDate",
            "updatedDate",
            "children"
        )

    def get_children(self, obj):
        children=Comment.objects.filter(parent_comment=obj.id).order_by('createdDate')
        if not children.exists():
            return None
        serializer=ReplySerializers(children, many=True,)
        return serializer.data
    
    def get_coments_count(self, obj):
        return obj.coments_count
    


class TinyPostSerializers(ModelSerializer):#좋아요 기능에서 이용
    # Image=ImageSerializers(many=True, read_only=True, required=False)
    class Meta:
        model=Post
        fields=(
            "pk",
            "content",
            "Image",
            "createdDate",
            "likeCount"#게시글 좋아요 수 
            )
class PostSerializers(ModelSerializer):#댓글 없음.
    print("PostSerilaizers")
    categoryType=BoardCategorySerializer(many=True, read_only=True)
    boardAnimalTypes=PetCategorySerializer(many=True, read_only=True)
    author=TinyUserSerializers(read_only=True)
    # Image=ImageSerializers(many=True, read_only=True, required=False)
    # likeCheck=serializers.SerializerMethodField()#현재 사용자가 게시글을 좋아요 했는지를 여부를 나타냄
    
    class Meta:
        model=Post
        fields=(
            "pk",
            "categoryType",
            "boardAnimalTypes",
            "author",
            "content",
            "Image",#ImageModel의 related_name 이용 
            # "likeCount",
            # "likeCheck",
        )

    # def get_likeCheck(self, data):
    #     request=self.context.get("request")
    #     if request and request.user.is_authenticated:
    #         return PostLike.objects.filter(user=request.user, post=data).exists()
    #     return False

    
    def create(self, validated_data):  
        
        category_data=validated_data.pop("categoryType", None)
        print("category_data: ", category_data)
        pet_category_data=validated_data.pop("boardAnimalTypes", None)
        print("pet_: ", pet_category_data)
        image_data = validated_data.pop("Image", None)#값 없으면 None
        try:
            with transaction.atomic():
                post = Post.objects.create(**validated_data)
                if category_data:
                    for i in Board.objects.all():
                        print(i.categoryType)
                    categoryType=Board.objects.filter(categoryType=category_data).first()
                    post.categoryType=categoryType
                    post.save()

                if image_data:
                    if isinstance(image_data, list):
                        if len(image_data)<=5:
                            for img in image_data:
                                Image.objects.create(post=post, img_path=img.get("img_path"))
                        else:
                            raise ParseError("이미지는 최대 5장 까지 업로드 할 수 있습니다.") 
                    else:
                        raise ParseError("image 잘못된 형식 입니다.")               
                
                if pet_category_data:
                    if len(pet_category_data) > 3:
                        raise ParseError("boardAnimalTypes는 최대 3개까지 선택할 수 있습니다.")
                    if isinstance(pet_category_data, list):
                        for pet_category in pet_category_data:
                            pet_category = get_object_or_404(Pet,animalTypes=pet_category)
                            post.boardAnimalTypes.add(pet_category)
                    else:
                        pet_category = get_object_or_404(Pet, animalTypes=pet_category_data)
                        post.boardAnimalTypes.add(pet_category)
                else:
                    raise ParseError({"error": "잘못된 형식입니다."})
        
        except Exception as e:
            raise ValidationError({"error":str(e)})
        return post
        
    def validate(self, data):
        content = data.get('content', None)
        images = data.get('Image', None)
        if content is None and images is None:
            raise ParseError({"error": "내용을 입력해주세요."})
        if images and len(images)>5:
            raise ParseError({"error":"이미지는 최대 5개까지 등록이 가능합니다."})
        return data
    
    

class PostListSerializers(ModelSerializer):#간략한 정보만을 보여줌
    author=SimpleUserSerializer(read_only=True)
    boardAnimalTypes=PetCategorySerializer(many=True)
    categoryType=BoardCategorySerializer()
    #images=ImageSerializers(many=True, read_only=True, required=False)
    # images = serializers.SerializerMethodField()
    #commentCount=serializers.SerializerMethodField()
    commentCount = serializers.IntegerField(read_only=True)
    likeCount = serializers.IntegerField(read_only=True)
    bookmarkCount = serializers.IntegerField(read_only=True)

    createdDate = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%S")
    updatedDate = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%S")

    class Meta:
        model=Post
        fields=(
            "pk",
            "categoryType",
            "boardAnimalTypes",
            "author",
            "content",
            "postImage",
            "createdDate", 
            "updatedDate",
            "viewCount",#조회수
            "likeCount",#좋아요수 
            "commentCount",#댓글수 (대댓글 미포함)
            "bookmarkCount",#북마크수
        )
    # def get_images(self, post):
    #     images = post.images.all()
    #     if images.exists():
    #         return ImageSerializers(images.first(), context=self.context).data   
    #     return [] 
    # def get_images(self, post):
    # # 이미 로드된 이미지 데이터를 사용
    #     images = getattr(post, 'images', None)
    #     if images:
    #         return ImageSerializers(images, many=True, context=self.context).data
    #     return []

    def get_commentCount(self, obj):
        return obj.commentCount
    
    # def to_representation(self, instance):
    #     ret = super().to_representation(instance)
    #     ret['createdDate'] = instance.createdDate.strftime("%Y-%m-%dT%H:%M:%S")
    #     ret['updatedDate'] = instance.updatedDate.strftime("%Y-%m-%dT%H:%M:%S")
    #     return ret
    
class PostListSerializer(ModelSerializer):#MY/Post에서 이용(일단 보류.)
    author=TinyUserSerializers(read_only=True)
    boardAnimalTypes=PetCategorySerializer(many=True)
    categoryType=BoardCategorySerializer()
    # Image=ImageSerializers(many=True, read_only=True, required=False)
    commentCount=serializers.SerializerMethodField()
    class Meta:
        model=Post
        fields=(
            "pk",
            "categoryType",
            "boardAnimalTypes",
            "author",
            "content",
            "Image",
            "createdDate", 
            "updatedDate",
            "viewCount",#조회수
            "likeCount",#좋아요 수 
            "commentCount",#댓글 수 (대댓글 미포함)
            "bookmarkCount",#북마크 수
        )
    # def get_images(self, post):
    #     images = post.images.all()
    #     if images.exists():
    #         return ImageSerializers(images.first(), context=self.context).data   
    #     return [] 
    def get_commentCount(self, obj):
        return obj.commentCount    
    
    
        
        return self.updatedDate.strftime("%Y-%m-%dT%H:%M:%S") 
class PostDetailSerializers(ModelSerializer):#image 나열
    author=SimpleUserSerializer()
    boardAnimalTypes=PetCategorySerializer(many=True)
    categoryType=BoardCategorySerializer()
    # Image=ImageSerializers(many=True, read_only=True, required=False)
    likeCheck=serializers.SerializerMethodField()
    commentCount=serializers.SerializerMethodField()
    bookmarkCheck=serializers.SerializerMethodField()
    class Meta:
        model=Post
        fields=(
            "id",
            "categoryType",
            "boardAnimalTypes",
            "author", 
            "content",
            "Image",
            "createdDate",
            "updatedDate",    
            "viewCount",# 조회수 
            "likeCount",# 좋아요 수
            "likeCheck",#좋아요 토글
            "commentCount",#댓글 수 
            "bookmarkCheck",#북마크 토글
            "bookmarkCount",#북마크 수
        )

    def get_likeCheck(self, data):
        request = self.context.get("request")
        if request:
            if request.user.is_authenticated:
                return PostLike.objects.filter(author=request.user,post__pk=data.pk).exists()
        return False
    
    def get_commentCount(self, obj):
        return obj.commentCount
    
    def get_bookmarkCheck(self, data):
        request=self.context.get("request")
        if request and request.user.is_authenticated:
            return Bookmark.objects.filter(author=request.user, post=data).exists()
        return False
    
# {
    # "content": "test",
    # "categoryType": {"categoryType": "반려고수"},
    # "Image": [
    # {
    #        "img_path": "https://res.cloudinary.com/dk-find-out/image/upload/q_80,w_960,f_auto/DCTM_Penguin_UK_DK_AL526630_wkmzns.jpg"
    # }
    # ],
    # "boardAnimalTypes": [{"animalTypes": "새"}]
# }
    
    def update(self, instance, validated_data):
        
        # instance.boardAnimalTypes.clear()
        pet_category_data = validated_data.pop("boardAnimalTypes", None)
        category_data = validated_data.pop("categoryType", None)
        image_data = validated_data.pop("Image", None)
        existing_image_count = instance.Image.count()
        
        if image_data:
            if isinstance(image_data, list):
                total_image_count = existing_image_count + len(image_data)
                if total_image_count > 5:
                    raise ParseError("이미지는 최대 5장 까지 업로드 할 수 있습니다.")
                
                instance.Image.clear()
                
                for img in image_data:
                    Image.objects.create(post=instance, img_path=img.get("img_path"))
            else:
                raise ValidationError("image 잘못된 형식 입니다.")
                   
        if category_data:
            category_instance = Board.objects.filter(categoryType=category_data.get("categoryType")).first()
            if not category_instance:
                raise ParseError({"category": "Invalid category"})
            instance.categoryType = category_instance

        # Update the remaining fields
        instance = super().update(instance, validated_data)

        # Update the many-to-many fields
        if pet_category_data and len(pet_category_data) > 3:
            raise ParseError("boardAnimalTypes는 최대 3개까지 선택할 수 있습니다.")
        if pet_category_data is not None:
            instance.boardAnimalTypes.clear()
            for pet_category in pet_category_data:
                print("aa: ", pet_category)
                animalTypes = pet_category.get("animalTypes")
                print("9:", animalTypes)
                if animalTypes:
                    pet_category, _ = Pet.objects.get_or_create(animalTypes=animalTypes)
                    instance.boardAnimalTypes.add(pet_category)

        instance.save()
        return instance
  



class v2_PostListSerializer(ModelSerializer):
    author=V2_PostAuthorSerializer()
    # author = serializers.CharField(source='author.username')#FK에서 필요한 column가져오는 경우 source를 사용함
    categoryType = serializers.CharField(source='categoryType.boardCategoryType')
    animal_types = serializers.SerializerMethodField()
    regionDepth2 = serializers.CharField(source='address.regionDepth2', read_only=True)
    
    def get_animal_types(self, obj):
        return [animalType.animalTypes for animalType in obj.boardAnimalTypes.all()]

    class Meta:
        model = Post
        fields = [
            'id',
            'author',
            'regionDepth2',
            'categoryType', 
            'animal_types', 
            'content', 
            'postImage', 
            'viewCount', 
            'createdDate', 
            'updatedDate'
        ]


#<use elasticsearh>
class PostSearchSerializer(DocumentSerializer):
    author=SimpleUserSerializer(read_only=True)
    boardAnimalTypes=PetCategorySerializer(many=True)
    categoryType=BoardCategorySerializer()
    # Image=ImageSerializers(many=True, read_only=True, required=False)

    class Meta:
        model=Post
        document=PostDocument
        fields=(
            "id",
            "categoryType",
            "boardAnimalTypes",
            "author",
            "content",
            "Image",
            "createdDate", 
            "updatedDate",
            "viewCount",
            "likeCount",
            "commentCount",
            "bookmarkCount",
        )