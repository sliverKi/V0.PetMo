import requests
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.hashers import check_password 
from django.conf import settings
from config.settings import KAKAO_API_KEY, GOOGLE_MAPS_API_KEY

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import ParseError, NotFound, PermissionDenied, ValidationError
from rest_framework.permissions import IsAuthenticated

from .models import User, Address
from .serializers import (
    TinyUserSerializers, PrivateUserSerializers, 
    AddressSerializer, AddressSerializers, UserSerializers,
    EnrollPetSerailzer
    )
from pets.models import Pet
from posts.models import Post, Comment
from posts.serializers import PostListSerializers, CommentSerializers, ReplySerializers

#start images: docker run -p 8000:8000 petmo-back
class StaticInfo(APIView):

    def get(self, request):
        user=request.user
        if not user.is_active:
            return Response({"error":"세션이 만료되었거나 올바르지 않은 값입니다."})
        serializer=UserSerializers(user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class MyPost(APIView):  

    def get(self, request):
        user = request.user

        user_posts=Post.objects.filter(user=user)#user가 작성한 게시글
        user_post_serialized = PostListSerializers(user_posts, many=True).data
        
        response_data = {
            "user": TinyUserSerializers(user).data,
            "user_posts": user_post_serialized,
        }
        return Response(response_data, status=status.HTTP_200_OK)
class MyComment(APIView):
    def get(self, request):
        user=request.user
        user_comments=Comment.objects.filter(user=user).select_related('post')#user가 작성한 댓글 
        user_comments_serialized=[]
        for comment in user_comments:
            serialized_comment=CommentSerializers(comment).data
            serialized_comment['post_content']=comment.post.content   
            user_comments_serialized.append(serialized_comment)
        response_data = {
            "user_comments": user_comments_serialized,
        }
        return Response(response_data, status=status.HTTP_200_OK)
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
            return Response({"error":"사용자가 아직 내동네 설정을 하지 않았습니다. "}, status=status.HTTP_404_NOT_FOUND)
    
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
                serializer=AddressSerializers(address)
                
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": "Failed to Save Address Data"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    def put(self, request):
        user=request.user
        
        if not user.user_address:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        serializer=AddressSerializer(
            user.user_address,
            data=request.data,
            partial=True,
        )
        if serializer.is_valid():
            updated_address=serializer.save()
            serializer=AddressSerializer(updated_address)
            return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    def delete(self, request):
        user=request.user
        print("user", user)
        address_id = user.user_address.id
        print(user.user_address.id)
        try:
            address=Address.objects.get(id=address_id)
        except Address.DoesNotExist:
            return Response({"error":"해당 주소가 존재하지 않습니다."},status=status.HTTP_404_NOT_FOUND)    
        
        if request.user!=address.user:
            raise PermissionDenied("내 동네 삭제 권한이 없습니다.")
        user.user_address.delete()
        user.user_address=None
        user.save()
        return Response(status=status.HTTP_200_OK)
       

class getIP(APIView):#ip기반 현위치 탐색
    permission_classes=[IsAuthenticated]#인가된 사용자만 허용

    def get(self, request):
        try:
            client_ip_address  = request.META.get('HTTP_X_FORWARDED_FOR') or request.META.get('REMOTE_ADDR')#현재 접속 ip
            print("client IP address: ", client_ip_address)

            if not client_ip_address:
                return Response({"error": "could not get Client IP address"}, status=status.HTTP_400_BAD_REQUEST)
            geolocation_url =  f'https://www.googleapis.com/geolocation/v1/geolocate?key={GOOGLE_MAPS_API_KEY}'
            data = {
                'considerIp':'true',#IP참조 
            }
            result=requests.post(geolocation_url, json=data)
            # print("result", result)
        
            if result.status_code==200: #get KAKAO_API url-start
                # print("api 요청 접속 성공 ")
                location = result.json().get('location')
                Ylatitude = location.get('lat')#위도
                print("위도:",Ylatitude )
                Xlongitude = location.get('lng')#경도
                print("경도:, ",Xlongitude )
                region_url= f'https://dapi.kakao.com/v2/local/geo/coord2regioncode.json?x={Xlongitude}&y={Ylatitude}'
                headers={'Authorization': f'KakaoAK {KAKAO_API_KEY}' }
                response=requests.get(region_url, headers=headers)
            
                datas=response.json().get('documents')
                print("datas: ", datas)
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
                    return Response({"error":"Failed to get region data for IP address"}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({"error": "Failed to get geolocation data for IP address"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": "Failed to Load open API data."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
   
class getQuery(APIView):#검색어 입력 기반 동네 검색
    permission_classes=[IsAuthenticated]#인가된 사용자만 허용

    def get(self, request):
        
        # 1. 검색어 예외 처리 할 것 
        # 1-1. 검색어의 길이가 2 미만 인 경우 예외 발생 
        # 1-2. 검색어가 공백인 경우 에러 발생  
        # 1-3. 검색한 주소가 없는 경우 예외 발생 
           
        search_query=request.GET.get('q')
        # print(search_query)
        if len(search_query)<2:
            raise ParseError("2자 미만.error")
        if not search_query:
            raise ParseError("검색할 키워드를 입력해 주세요.")
        
        search_url='https://dapi.kakao.com/v2/local/search/address.json'
        headers={'Authorization': f'KakaoAK {KAKAO_API_KEY}'}
        params={'query': search_query}
       
        response=requests.get(search_url, headers=headers, params=params)
        print("res", response)
        datas=response.json()
        if not datas['documents']:
            raise ParseError("입력하신 주소가 없습니다. ")
        
        return Response(datas, status=status.HTTP_200_OK)

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
            serializer=EnrollPetSerailzer(animal)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class Quit(APIView):
    def get(self, request):
        user=request.user
        try:
            serializer=UserSerializers(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except:
            return Response(serializer.errors, status=status.HTTP_404_NOT_FOUND)
    
   
    def post(self, request):
        #input data {"password":"xxx"}
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
        return Response(status=status.HTTP_204_NO_CONTENT)
        





