import requests
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.hashers import check_password 
from django.conf import settings
from django.core.paginator import Paginator

from config.settings import KAKAO_API_KEY, GOOGLE_MAPS_API_KEY

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import ParseError, NotFound, PermissionDenied, ValidationError
from rest_framework.permissions import IsAuthenticated


from .models import User, Address
from . import serializers
from .serializers import (
    
    SimpleUserSerializer, PrivateUserSerializers, 
    AddressSerializer, AddressSerializers, UserSerializers,
    EnrollPetSerailzer, TinyUserSerializers
    )
from pets.models import Pet
from posts.models import Post, Comment

from posts.serializers import PostDetailSerializers,PostListSerializers, CommentSerializers, ReplySerializers


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

class getAddress(APIView):
    # permission_classes=[IsAuthenticated]#인가된 사용자만 허용
    def get_object(self, pk):
        try:
            return User.objects.get(pk=pk)
        except User.DoesNotExist:
            raise NotFound     
    
    def get(self, request):#현재 로그인한 user의 주소를 조회 
        user=request.user
        print(user)
        user_address=Address.objects.filter(user=user).first()
        print(user_address)
        if user_address:
            serializer = AddressSerializer(user_address)
            return Response(serializer.data, status=status.HTTP_200_OK) 
        else:
            return Response({"message":"사용자가 아직 내동네 설정을 하지 않았습니다."}, status=status.HTTP_404_NOT_FOUND)
    

    def post(self, request):#주소 등록 
        print("post Start")
        try:
            user=request.user
            serializer = AddressSerializers(
                data=request.data, 
                context={'user':user}#user 객체를 참조하기 위함. ~> serializer에서 사용자 정보가 필요하기 때문
            )
            if serializer.is_valid():
                address=serializer.save(user=request.user)
                address.addressName=request.data.get('addressName')
                user.user_address=address
                user.save()
                serializer=AddressSerializer(address)
                
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": "Failed to Save Address Data."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
  
    def put(self, request):
        user=request.user
        
        if not user.user_address:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        serializer=AddressSerializers(
            user.user_address,
            data=request.data,
            partial=True,
        )
        if serializer.is_valid():
            updated_address=serializer.save()
            serializer=AddressSerializers(updated_address)
            return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
   
    def delete(self, request):
        user=request.user
        address_id = user.user_address.id
        address=Address.objects.get(id=address_id)
        if request.user!=address.user:
            raise PermissionDenied("내 동네 삭제 권한이 없습니다.")
        user.user_address.delete()
        user.user_address=None
        user.save()
        return Response({"Success address delete."},status=status.HTTP_204_NO_CONTENT)
       

class getIP(APIView):#ip기반 현위치 탐색
    # permission_classes=[IsAuthenticated]#인가된 사용자만 허용
    def get(self, request):
        try:
            client_ip_address  = request.META.get('HTTP_X_FORWARDED_FOR') or request.META.get('REMOTE_ADDR')#현재 접속 ip
            print("client IP address: ", client_ip_address)

            if not client_ip_address:
                return Response({"error": "Could not get Client IP address."}, status=status.HTTP_400_BAD_REQUEST)
            geolocation_url =  f'https://www.googleapis.com/geolocation/v1/geolocate?key={GOOGLE_MAPS_API_KEY}'
            data = {
                'considerIp':'true',#IP참조 
            }
            result=requests.post(geolocation_url, json=data)
            if not result:
                return Response({"error":"result is empty."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            # print("result", result)
        
            if result.status_code==200: #get KAKAO_API url-start
                # print("api 요청 접속 성공 ")
                location = result.json().get('location')
                Ylatitude = location.get('lat')#위도
                print("위도:",Ylatitude )
                Xlongitude = location.get('lng')#경도
                print("경도:, ",Xlongitude )
                region_url= f'https://dapi.kakao.com/v2/local/geo/coord2regioncode.json?x={Xlongitude}&y={Ylatitude}'
                print("2:", region_url)#kakao url
                headers={'Authorization': f'KakaoAK {KAKAO_API_KEY}' }
                response=requests.get(region_url, headers=headers)
                
                datas=response.json().get('documents')
                print("datas: ", datas)
                if not datas:#추가
                    return Response({"error":"datas is empty."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                response.json().get('error')#추가
                if response.status_code==200:
                    address=[]
                    for data in datas:
                        address.append({
                            'address_name': data['address_name'], 
                            'region_1depth_name': data['region_1depth_name'], 
                            'region_2depth_name': data['region_2depth_name'], 
                            'region_3depth_name': data['region_3depth_name'],
                        })
                    return Response(address, status=status.HTTP_200_OK)
                else:
                    return Response({"error":"Failed to get region data for IP address."}, status=status.HTTP_400_BAD_REQUEST)#error
            else:
                return Response({"error": "Failed to get geolocation data for IP address."}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": "Failed to Load open API data."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
   
class getQuery(APIView):#검색어 입력 기반 동네 검색
    # permission_classes=[IsAuthenticated]#인가된 사용자만 허용
 
    def get(self, request):
        
        # 1. 검색어 예외 처리 할 것 
        # 1-1. 검색어의 길이가 2 미만 인 경우 예외 발생 
        # 1-2. 검색어가 공백인 경우 에러 발생  
        # 1-3. 검색한 주소가 없는 경우 예외 발생 
           
        search_query=request.GET.get('q')
        # print(search_query)
        if not search_query and len(search_query)<2:
            raise ValidationError("error: 검색 키워드를 2자 이상으로 입력해 주세요.")
        # if :
        #     raise ValidationError("error: 검색할 키워드를 입력해 주세요.")
        
        search_url='https://dapi.kakao.com/v2/local/search/address.json'
        headers={'Authorization': f'KakaoAK {KAKAO_API_KEY}'}
        params={'query': search_query}
       
        response=requests.get(search_url, headers=headers, params=params)
        print("res", response)
        datas=response.json()
        
        if 'documents' not in datas or not datas['documents']:
            raise ValidationError("error: 입력하신 주소가 존재하지 않습니다.")
        results=[]
        for document in datas['documents']:
            result={
                "region_1depth_name": document['address']['region_1depth_name'],
                "region_2depth_name": document['address']['region_2depth_name'],
                "region_3depth_h_name": document['address']['region_3depth_h_name'],
                "region_3depth_name": document['address']['region_3depth_name'],
            }
            results.append(result)
        return Response(results, status=status.HTTP_200_OK)

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
        






