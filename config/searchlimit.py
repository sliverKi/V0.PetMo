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
        self.rate_limit_key = "search_rate_limit:user:{}" #redis key
    
    def __call__(self, request):
        # 검색어 관리 로직
        user_name = request.user.username
        if not self.redis_client.exists(self.rate_limit_key.format(user_name)):
            # 해당 키가 존재하지 않으면, 새로 생성하고 만료 시간을 설정
            self.redis_client.set(self.rate_limit_key.format(user_name), 1, ex=20)  # 20초로 설정
        else:
            # 이미 키가 존재하는 경우, 요청 카운트를 증가
            request_count = self.redis_client.incr(self.rate_limit_key.format(user_name))
            print("middleware-request_count", request_count)
            # 요청 횟수 제한 설정 (예: 초당 5회)
            request_limit = 5
            if request_count ==1:
                self.redis_client.expire(self.rate_limit_key.format(user_name), 30)  # 10초로 설정

            if request_count > request_limit:
                retry_after_seconds = 30  # 30초 후에 다시 시도하도록 설정
                response = HttpResponse(
                    f"검색 요청 횟수가 초과되었습니다. {retry_after_seconds}초 후에 다시 시도하세요.",
                    content_type="text/plain",
                    status=429,  # HTTP 상태 코드 429 (너무 많은 요청)
                )
                response["Retry-After"] = str(retry_after_seconds)
                
                if retry_after_seconds==0:
                    self.redis_client.delete(self.rate_limit_key.format(user_name))
                return response

        response = self.get_response(request)
        return response