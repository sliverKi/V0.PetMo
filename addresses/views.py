import requests, json, time, redis
from django.shortcuts import render
from users.models import User
from .models import Address
from config.settings import KAKAO_API_KEY, IP_GEOAPI, REDIS_HOST, REDIS_PORT

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import NotFound, PermissionDenied, ValidationError
from rest_framework.permissions import IsAuthenticated

from users.serializers import AddressSerializer, AddressSerializers
from urllib.request import urlopen
from config.searchlimit import searchRateLimiterMiddleware

# Create your views here.
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
    permission_classes=[IsAuthenticated]#인가된 사용자만 허용
    
    def get_clientIP(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            print("ip주소들 ", x_forwarded_for)
            client_ip_address = x_forwarded_for.split(',')[0].strip()
            print("use XFF, client IP address: ", client_ip_address)
        else:
            client_ip_address  = request.META.get('REMOTE_ADDR')
            print("use REMOTE, client IP address", client_ip_address)
        return client_ip_address

    
    def get(self, request):
        try:
            client_ip_address = self.get_clientIP(request)  # 현재 접속 IP
            print("최종 client IP address:", client_ip_address)
            if not client_ip_address:
                return Response({"error": "Could not get Client IP address."}, status=status.HTTP_400_BAD_REQUEST)
            
            ip_geolocation_url=f'https://geo.ipify.org/api/v2/country,city?apiKey={IP_GEOAPI}&ipAddress={client_ip_address}'
            result=urlopen(ip_geolocation_url).read().decode('utf8')
            # print(urlopen(ip_geolocation_url).read().decode('utf8'))
        
            print("result: ", result)
            res_data=json.loads(result)
            # print("res_data", res_data)
            
            if not res_data:
                return Response({"error":"res_data is empty."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
        
            if res_data: #구글API에서 위도 경도를 추출하고 KAKAO_API에 전달
                print("client_ip_address", client_ip_address)
                location = res_data.get('location')
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
        start_time = time.time()
        search_query=request.GET.get('q')
        #print("ㅂ: ",search_query)
        if not search_query and len(search_query)<2:
            raise ValidationError("error: 검색 키워드를 2자 이상으로 입력해 주세요.")

        search_url='https://dapi.kakao.com/v2/local/search/address.json'
        headers={'Authorization': f'KakaoAK {KAKAO_API_KEY}'}
        params={'query': search_query}
       
        response=requests.get(search_url, headers=headers, params=params)
        #print("res", response)
        datas=response.json()
        
        if 'documents' not in datas or not datas['documents']:
            raise ValidationError("error: 입력하신 주소가 존재하지 않습니다.")
        
        # Redis에 사용자가 입력한 검색어 저장
        user_name = request.user.username
        redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT)
        user_search_key = f"user_search_history:{user_name}"
        redis_client.set(user_search_key, search_query)
        
        search_history = redis_client.get(f'user_search_history:{user_name}')
        decoded_search_history = search_history.decode('utf-8')
        print("decode_search_history: ", decoded_search_history)#redis-cli에서는 encoding된 값으로 확인되어져, terminal에서 decode된 값 확인하기 위함  

        results=[]
        for document in datas['documents']:
            result={
                "region_1depth_name": document['address']['region_1depth_name'],
                "region_2depth_name": document['address']['region_2depth_name'],
                "region_3depth_h_name": document['address']['region_3depth_h_name'],
                "region_3depth_name": document['address']['region_3depth_name'],
            }
            results.append(result)
        
        end_time = time.time()
        elapsed_time = end_time-start_time#0.18초

        results.append(elapsed_time)
        return Response(results, status=status.HTTP_200_OK)
