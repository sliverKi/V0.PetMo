from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination
from posts.serializers import PostSearchSerializer
from .documents import PostDocument
from elasticsearch_dsl import Q
from elasticsearch_dsl.connections import connections
from datetime import datetime
from elasticsearch import Elasticsearch
from history.models import History
from django.contrib.auth.models import AnonymousUser
from config.settings import awsauth, DEBUG, ELASTICSEARCH_DSL
class SearchPost(APIView, PageNumberPagination):
    post_serializer=PostSearchSerializer
    search_document=PostDocument

    def log_search_query(self, query, user):
        if DEBUG:
            es = Elasticsearch([{'host': 'localhost', 'port': 9200}])#개발환경인경우 'host'를 localhost로 변경, prod-mode: 'host':'elasticsearch'
        else:
            # 프로덕션 환경: AWS OpenSearch
            es = Elasticsearch(
                hosts=ELASTICSEARCH_DSL['default']['hosts'],
                http_auth=ELASTICSEARCH_DSL['default'].get('http_auth'),
                use_ssl=ELASTICSEARCH_DSL['default'].get('use_ssl', True),
                verify_certs=ELASTICSEARCH_DSL['default'].get('verify_certs', True),
                connection_class=ELASTICSEARCH_DSL['default'].get('connection_class')
            )
        log_body = {
            "query": query,
            "timestamp": datetime.utcnow()
        }
        es.index(index="search_post_logs", doc_type="_doc", body=log_body)
        # Django DB에 검색 기록 저장
        History.objects.create(
        user=user if not isinstance(user, AnonymousUser) else None,  # 로그인한 사용자인 경우에만 user 정보 저장
        query=query
        )
   
    def get(self, request, query=None):
        try:
            # self.log_search_query(query)
            self.log_search_query(query, user=request.user)
            print(query)

            q=Q(
                "multi_match",
                query=query,
                fields=["content", "user.username", "boardAnimalTypes.animalTypes", "categoryType.categoryType"],
                fuzziness="auto",
            )& Q(
                minimum_should_match=1, 
            )
            search = self.search_document.search().query(q)
            response = search.execute()

            results = self.paginate_queryset(response, request, view=self)
            serializer = self.post_serializer(results, many=True)
            return self.get_paginated_response(serializer.data)

        except Exception as e:
            return HttpResponse(str(e), status=500)
        
    