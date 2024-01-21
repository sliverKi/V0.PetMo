from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination
from posts.serializers import PostSearchSerializer
from .documents import PostDocument
from elasticsearch_dsl import Q
from datetime import datetime
from elasticsearch import Elasticsearch

class SearchPost(APIView, PageNumberPagination):
    post_serializer=PostSearchSerializer
    search_document=PostDocument

    def log_search_query(self, query):
        es = Elasticsearch([{'host': 'elasticsearch', 'port': 9200}])
        log_body = {
            "query": query,
            "timestamp": datetime.utcnow()
        }
        es.index(index="search_logs", doc_type="_doc", body=log_body)

   
    def get(self, request, query=None):
        try:
            
            self.log_search_query(query)
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
        
    