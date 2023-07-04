from django.shortcuts import render
from django.http import JsonResponse
from django.utils import timezone
from django.shortcuts import redirect
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect
from config.settings import KAKAO_API_KEY
from rest_framework.response import Response
from rest_framework.views import APIView 
from rest_framework.permissions import AllowAny
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
# from rest_framework_simplejwt.tokens import AccessToken
# from rest_framework_simplejwt.token_blacklist.models import OutstandingToken
from rest_framework.exceptions import NotFound, ParseError
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from .serializers import RegisterSerializers
from users.models import User
from users.serializers import UserSerializers

import requests

# {"email":"momo@gmail.com", "password":"momo"}
class LogIn(APIView):

    def post(self, request, format=None):
        email=request.data.get('email')
        password=request.data.get('password')
        res=Response()
        try:
            user = User.objects.get(email=email)
            
        except User.DoesNotExist:
            return Response({"error":"존재하지 않는 사용자 입니다. 회원가입을 먼저 해주세요."}, status=status.HTTP_401_UNAUTHORIZED)
        
        if not email or not password:
           return Response({"error":"이메일과 비밀번호를 입력해주세요."}, status=status.HTTP_400_BAD_REQUEST)
        
        if user.check_password(password):
            login(request, user)
            user.last_login = timezone.now()
            serializer=UserSerializers(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({"error":"이메일 또는 비밀번호를 확인해주세요."}, status=status.HTTP_400_BAD_REQUEST)
            
class LogOut(APIView):
    permission_classes=[IsAuthenticated]#전부 다 인증된 사용자에게만 권한 허용

    def post(self, request):
        res=Response()
        res.delete_cookie("sessionid")
        logout(request)        
        return Response({"success":"Success logout! :) See you!"}, status=status.HTTP_200_OK)
    
      
class Register(APIView):
    
    #input data {"email":"moomoo@gmail.com", "username":"eungimoo", "password":"eungi"}
    def post(self, request, format=None):#privateUserSerializers
        password=request.data.get("password")
        username=request.data.get("username")
        email=request.data.get("email")

        if not password or not username or not email :
            raise ParseError
        serializer=RegisterSerializers(data=request.data)
        if serializer.is_valid():
            user=serializer.save()
            user.set_password(password)
            user.is_first=True
            user.save()
            serializer=RegisterSerializers(user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class KakaoException(Exception):
    pass

class KakaoLogin(APIView):
    def get(self, request):
        kakao_api="https://kauth.kakao.com/oauth/authorize?response_type=code"
        redirect_uri="http://127.0.0.1:8000/api/v1/auths/kakao/callback"
        client_id=KAKAO_API_KEY
        return redirect(f"{kakao_api}&client_id={client_id}&redirect_uri={redirect_uri}")

class KakaoCallBack(APIView):
    def get(self, request):
        try:
            code = request.GET.get("code")
            client_id = KAKAO_API_KEY
            redirect_uri = "http://127.0.0.1:8000/api/v1/auths/kakao/callback"
            token_request = requests.post(
                "https://kauth.kakao.com/oauth/token",
                data={
                    "grant_type": "authorization_code",
                    "client_id": client_id,
                    "redirect_uri": redirect_uri,
                    "code": code,
               },
            )
            token_json = token_request.json()
            print(token_json)
            
            error = token_json.get("error", None)
            
            if error is not None:
                return Response({"message": error}, status=status.HTTP_400_BAD_REQUEST)
            
            access_token = token_json.get("access_token")
            profile_request = requests.get(
                "https://kapi.kakao.com/v2/user/me",
                headers={
                    "Authorization": f"Bearer {access_token}",
                    # "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
                },
            )
            profile_json = profile_request.json()
            
            kakao_account =profile_json.get("kakao_account")
            
            
            if email is None:
                raise KakaoException()
            email = kakao_account.get("email", None)#왜 None?
            nickname = kakao_account.get("profile", None).get("nickname", None)
            
        except KeyError:
            return Response({"message": "INVALID_TOKEN"}, status=status.HTTP_400_BAD_REQUEST)
        
        if User.objects.filter(email=email).exists():
            kakao_user = User.objects.get(email=email)
            refresh=RefreshToken.for_user(kakao_user)
            response=HttpResponseRedirect(
                # front 주소 
                # f"http://127.0.0.1:8000/KakaoLogin?refresh={str(refresh)}&access={str(refresh.access_token)}"

            )
            print("success")
            return Response(response, status=status.HTTP_200_OK)
            
        else:
            if email:
                user=User.objects.create(
                    email=email, username=nickname,
                )
                refresh = RefreshToken.for_user(user)
                response=HttpResponseRedirect(
                    # f"http://127.0.0.1:8000/KakaoLogin?refresh={str(refresh)}&access={str(refresh.access_token)}"
                    
                )
                return Response(response, status=status.HTTP_200_OK)
            else:
                return Response(
                    {"error":"MISSING ACCOUNT"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

class NaverLogin(APIView):    
    def post(self, request):
        code = request.data.get("code")
        state = request.data.get("state")
        
        access_token = (
            requests.post(
                "https://nid.naver.com/oauth2.0/token",
                headers={
                    "Content-Type": "application/x-www-form-urlencoded",
                },
                data={
                    "grant_type": "authorization_code",
                    "client_id": "kq20IeckeIhaC1BsAKuF",
                    "client_secret": "4FTGMSzqCd",
                    "code": code,
                    "state": state,
                },
            )
            .json()
            .get("access_token")
        )
        user_data = requests.get(
            "https://openapi.naver.com/v1/nid/me",
            headers={"Authorization": f"Bearer {access_token}"},
        ).json()
        if (
            user_data.get("resultcode") == "00"
            and user_data.get("message") == "success"
        ):
            response = user_data.get("response")
            try:
                user = User.objects.get(email=response.get("email"))
                login(request, user)
                return Response(status=200)
            except User.DoesNotExist:
                user = User.objects.create(
                    username=response.get("id")[:10],
                    name=response.get("name"),
                    phone_number=response.get("mobile").replace("-", ""),
                    email=response.get("email"),
                    gender="male" if response.get("gender") == "M" else "female",
                    avatar=response.get("profile_image"),
                    is_naver=True,
                )
                user.set_unusable_password()
                user.save()
                login(request, user)
                refresh = RefreshToken.for_user(user)
                return Response(
                    {"access": str(refresh.access_token), "refresh": str(refresh)},
                    status=201,
                )

        return Response(status=400)

