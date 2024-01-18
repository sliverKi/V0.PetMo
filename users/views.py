import requests, boto3
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.hashers import check_password 
from django.conf import settings
from django.core.paginator import Paginator

from config.settings import KAKAO_API_KEY, IP_GEOAPI

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import ParseError, NotFound, PermissionDenied, ValidationError
from rest_framework.permissions import IsAuthenticated


from .models import User
from addresses.models import Address
from . import serializers
from .serializers import (
    
    SimpleUserSerializer, PrivateUserSerializers, 
    AddressSerializer, AddressSerializers, UserSerializers,
    EnrollPetSerailzer, TinyUserSerializers,
    UserProfileUploadSerializer
    )
from pets.models import Pet
from posts.models import Post, Comment

from posts.serializers import PostDetailSerializers,PostListSerializers, CommentSerializers, ReplySerializers
from urllib.request import urlopen
import json, uuid
from config.settings import AWS_S3_ACCESS_KEY_ID, AWS_S3_SECRET_ACCESS_KEY, AWS_STORAGE_BUCKET_NAME
from django.core.files import File
from django.core.files.base import ContentFile
#start images: docker run -p 8000:8000 petmo-back
class StaticInfo(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        user=request.user
        serializer=UserSerializers(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

class MyPost(APIView):  
  
    def get(self, request):
        user = request.user

        user_posts=Post.objects.filter(user=user).order_by('-updatedDate')#user가 작성한 게시글
        # Pagination 설정
        paginator = Paginator(user_posts, 10)  # 페이지당 10개의 게시물을 보여줄 경우
        page_number = request.GET.get('page')  # 현재 페이지 번호
        page_obj = paginator.get_page(page_number)
        user_post_serialized = PostListSerializers(page_obj, many=True).data

        response_data = {
            "user_posts": user_post_serialized,
            "total_pages": paginator.num_pages,  # 전체 페이지 수
            "current_page": page_obj.number,  # 현재 페이지 번호
            "has_previous": page_obj.has_previous(),  # 이전 페이지 존재 여부
            "has_next": page_obj.has_next(),  # 다음 페이지 존재 여부
        }
        return Response(response_data, status=status.HTTP_200_OK)
        
    
class MyPostDetail(APIView):
    def get_object(self,pk):
        try:
            return Post.objects.get(pk=pk)
        except Post.DoesNotExist:
            raise NotFound

    def get(self, request, pk):
        post=self.get_object(pk)
        post.viewCount+=1 # 조회수 카운트
        post.save()
        
        serializer = PostDetailSerializers(
            post,
            context={"request":request},
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        post=self.get_object(pk=pk)

        if post.user != request.user:
            raise PermissionDenied
        
        serializer=PostDetailSerializers(
            post, 
            data=request.data,
            partial=True
        )
        if serializer.is_valid():
            try:
                post=serializer.save(
                    category=request.data.get("categoryType"),
                    boardAnimalTypes=request.data.get("boardAnimalTypes"),
                    Image=request.data.get("Image")
                )
            except serializers.ValidationError as e: 
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
                
            post = serializer.save(
                category=request.data.get("categoryType"),
                # boardAnimalTypes=request.data.get("boardAnimalTypes")
                )    
            serializer=PostDetailSerializers(post)
            return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request,pk):#게시글 삭제
        post=self.get_object(pk)    
        if request.user!=post.user:
            raise PermissionDenied("게시글 삭제 권한이 없습니다.")
        post.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class MyComment(APIView): 
    def get(self, request):
        user=request.user
        user_comments=Comment.objects.filter(user=user, parent_comment=None).select_related('post').order_by('-updatedDate')#user가 작성한 댓글 
        # Pagination 설정
        paginator = Paginator(user_comments, 5)  # 페이지당 10개의 댓글을 보여줄 경우
        page_number = request.GET.get('page')  # 현재 페이지 번호
        page_obj = paginator.get_page(page_number)

        user_comments_serialized=[]
        for comment in page_obj:
            serialized_comment=CommentSerializers(comment).data
            serialized_comment['post_content']=comment.post.content   
            user_comments_serialized.append(serialized_comment)
        
        response_data = {
            "user_comments": user_comments_serialized,
            "total_pages": paginator.num_pages,  # 전체 페이지 수
            "current_page": page_obj.number,  # 현재 페이지 번호
            "has_previous": page_obj.has_previous(),  # 이전 페이지 존재 여부
            "has_next": page_obj.has_next(),  # 다음 페이지 존재 여부
        }
        return Response(response_data, status=status.HTTP_200_OK)
    
class MyCommentDetail(APIView):
    def get_object(self, pk):
        try:
            return Comment.objects.get(pk=pk)
        except Comment.DoesNotExist:
            raise NotFound
        
    def get(self, request, pk):#게시글 삭제되면 댓글 자동 삭제 됌
        comment=self.get_object(pk)
        post = comment.post
        if not post:
            return Response({"error":"게시글이 삭제되었습니다."}, status=status.HTTP_404_NOT_FOUND)
        
        post_serializer = PostDetailSerializers(
            post,
            context={"request": request},
        )
    
        comment_serializer = CommentSerializers(
            comment,
            context={"request": request},
        )
        response_data = {
            "post": post_serializer.data,
            "comment": comment_serializer.data,
        }
        return Response(response_data, status=status.HTTP_200_OK)
    
    def put(self, request, pk):
        comment=self.get_object(pk)
        if comment.user !=request.user:
            raise PermissionDenied
        serializer= CommentSerializers(
            comment, 
            data=request.data,
            partial=True
        )
        if serializer.is_valid():
            comment = serializer.save()
            serializer=CommentSerializers(comment)
            return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    def delete(self, request, pk):
        comment=self.get_object(pk)
        if comment.user !=request.user:
            raise PermissionDenied
        comment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

            
class MyInfo(APIView):
    def get(self, request):
        user=request.user
        serializer = PrivateUserSerializers(user)
        return Response(serializer.data, status=status.HTTP_200_OK) 


    def put(self, request):
        user = request.user
        serializer = PrivateUserSerializers(
            user,
            data=request.data,
            partial=True,
        )
        if serializer.is_valid():
            user = serializer.save()
            serializer = PrivateUserSerializers(user)
            return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
   

# class PublicUser(APIView):#다른 누군가의 프로필을 보고 싶은 경우 
#     def get(self, request, username):
#         try:
#             User.objects.get(username=username)
#         except User.DoesNotExist:
#             raise NotFound   
#         serializer=PublicUserSerializer(user)
#         return Response(serializer.data) 


class getPets(APIView): #유저의 동물 등록
    def get(self, request):
        user=request.user
        serializer = UserSerializers(user)
        return Response(serializer.data, status=status.HTTP_200_OK) 
    
    
    #input data
    # {
    # "pets": [
    #    {"animalTypes": "강아지"},
    #    {"animalTypes": "고양이"}
    #   ]
    # }
 
    def post(self, request):
        user=request.user
        
        serializer=EnrollPetSerailzer(
            data=request.data,
            context={'request':request}
        )

        if serializer.is_valid():
            animal=serializer.save(
                user=request.user,
                pets=request.data.get("pets"),
            )            
            serializer=UserSerializers(animal)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class Quit(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        user=request.user
        print(user)
        if user.is_authenticated:
            serializer=UserSerializers(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({"message":"이미 탈퇴한 회원입니다. 회원가입후에 이용해 주세요."}, status=status.HTTP_404_NOT_FOUND)
    
   
    #input data {"password":"xxx"}
    def post(self, request):
        user=request.user
        password=request.data.get("password")
        # 검사사항
        #1. 유저가 입력한 비밀번호가 맞는지 확인 check_password(password, user.password)
        #2. 유저가 작성한 게시글, 댓글, 대댓글 모두 삭제 
        #3. 유저 디비에서 삭제 
        #4. 유저 세션 끊음

        if not check_password(password, user.password):
            raise ValidationError("비밀번호가 일치하지 않습니다.")
        
        posts=Post.objects.filter(user=user)
        posts.delete()

        comments=Comment.objects.filter(user=user)
        comments.delete()

        user.delete()#db에서 user 삭제
        request.session.delete()#session 끊음
        return Response({"Success Quit"}, status=status.HTTP_204_NO_CONTENT)
        


class UserProfileUploadView(APIView):
    def post(self, request):
        s3 = boto3.resource(
            's3',
            aws_access_key_id=AWS_S3_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_S3_SECRET_ACCESS_KEY,
        )
        serializer = UserProfileUploadSerializer(data=request.data)
        if serializer.is_valid():
            profile = serializer.validated_data['profile']
            response = requests.get(profile)
            if response.status_code == 200:# 이미지 파일을 다운로드하여 파일 객체로 변환
                unique_filename = str(uuid.uuid4()) + '.jpg'
                profile_image = File(response.content, name=unique_filename)
                # S3 버킷에 파일 객체 업로드
                s3.Object(AWS_STORAGE_BUCKET_NAME, 'profiles/' + profile_image.name).put(Body=profile)
                
                profile_saved_url = f"https://{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com/profiles/{profile_image.name}"
                
                user=request.user
                user.profile = profile_saved_url
                user.save()
                
                return Response({'message': '이미지가 업로드되었습니다.'}, status=status.HTTP_201_CREATED)
            else:
                return Response({'error': '이미지를 다운로드할 수 없습니다.'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)