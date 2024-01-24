import redis 
from django.conf import settings
from django.http import HttpResponse

class searchRateLimiterMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.redis_client = redis.Redis(
            host = settings.REDIS_HOST,
            port = settings.REDIS_PORT,
        )
        self.rate_limit_key = "search_rate_limit:{}" #redis key
    
    def __call__(self, request):
        # 검색어 관리 로직
        user_name = request.user.username
        rate_limit_key = self.rate_limit_key.format(user_name)
        
        if not self.redis_client.exists(rate_limit_key):
            self.redis_client.set(rate_limit_key, 1, ex=20) #해당 키가 존재하지 않으면, 새로 생성하고 만료 시간 설정(20초)
        else:
            request_count = self.redis_client.incr(rate_limit_key) #이미 키가 존재하는 경우, 요청 카운트를 증가
            request_limit = 5
            
            if request_count > request_limit:
                ttl = self.redis_client.ttl(rate_limit_key)
                print("ttl: ", ttl)#ttl: 키가 만료되고 자동으로 삭제될때까지 남은 시간
                response = HttpResponse(
                    f"검색 요청 횟수가 초과되었습니다. {ttl}초 후에 다시 시도하세요.",
                    content_type="text/plain",
                    status=429,  # HTTP 상태 코드 429 (너무 많은 요청)
                )
                response["Retry-After"] = str(ttl)
                return response
            
        response = self.get_response(request)
        return response