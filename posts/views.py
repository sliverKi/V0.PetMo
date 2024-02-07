from django.shortcuts import render
from django.core.paginator import Paginator
from django.core.cache import cache
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import SessionAuthentication
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, serializers
from rest_framework.exceptions import NotFound, PermissionDenied, ParseError, ValidationError
from rest_framework.pagination import CursorPagination

from .models import Post, Comment
from petCategories.models import Pet

from users.models import User
from addresses.models import Address
from .serializers import (
    PostSerializers,PostListSerializer,
    PostListSerializers, PostDetailSerializers, 
    CommentSerializers, ReplySerializers,
    v2_PostListSerializer, v3_PostListSerializer
    )
from .pagination import PaginaitionHandlerMixin
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.db.models import Prefetch
from django.db.models import Count
from django.db.models import Subquery, CharField, OuterRef, Value

from django.shortcuts import get_object_or_404
# silk
# from django.utils.decorators import method_decorator
# from silk.profiling.profiler import silk_profile
# #elasticsearch
# import operator
# from elasticsearch_dsl import Q as QQ
# from functools import reduce
# from django_elasticsearch_dsl.search import Search
# from django_elasticsearch_dsl_drf.viewsets import DocumentViewSet

# from django_elasticsearch_dsl_drf.filter_backends import (
#     FilteringFilterBackend, CompoundSearchFilterBackend)



class Comments(APIView):#등록되어진 모든 댓글
    def get(self,request):
        all_comments=Comment.objects.filter(parent_comment=None).order_by('-createdDate')
        serializer=ReplySerializers(all_comments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        #예외 : 존재 하지 않는 게시글에 댓글 작성 불가
        #예외 : 존재 하지 않는 게시글에 대댓글 작성 불가
        #에외 : 존재 하지 않는 댓글에 대댓글 작성 불가
        content=request.data.get("content")
        post_id=request.data.get("post")
        parent_comment_id = request.data.get("parent_comment", None)#부모댓글 정보 #부모댓글 정보가 전달 되지 않을 경우, None할당(=댓글)
        
        try:
            post=Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            return Response({"error":"해당 게시글이 존재하지 않습니다."}, status=status.HTTP_404_NOT_FOUND)

        if parent_comment_id is not None:#대댓글
            try:
                parent_comment = Comment.objects.get(id=parent_comment_id)
                print(parent_comment)
            except Comment.DoesNotExist:
                return Response({"error":"해당 댓글이 존재하지 않습니다."}, status=status.HTTP_404_NOT_FOUND)
        
            comment=Comment.objects.create(
                content=content,
                user=request.user,
                post=parent_comment.post,
                parent_comment=parent_comment
            )
            serializer = ReplySerializers(comment)
            return Response(serializer.data, status=status.HTTP_201_CREATED)           
        else: #댓글
            print("댓글")
            serializer=CommentSerializers(data=request.data)
            if serializer.is_valid():
                comment=serializer.save(
                    post=post,
                    user=request.user,
                )
                serializer=CommentSerializers(comment)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
class CommentDetail(APIView):# 댓글:  조회 생성, 수정, 삭제(ok)
    
    def get_object(self, pk):
        try:
            return Comment.objects.get(pk=pk)
        except Comment.DoesNotExist:
            raise NotFound

    def get(self, request, pk):#댓글의 pk로 접속시 해당 댓글이 갖고 있는 대댓글도 같이 조회함
        comment=self.get_object(pk=pk)
        serializer=ReplySerializers(
            comment,
            context={"request":request},                                    
        )
        return Response(serializer.data, status=status.HTTP_200_OK)
  
    def put(self, request,pk): 
        #예외 댓글 수정시에 해당 댓글이 있는지 우선 확인해야]
        
        comment=self.get_object(pk=pk)
        
        if comment.parent_comment:
            if comment.parent_comment.post.id!=comment.post.id:
                return Response({"error":"해당 댓글이 게시글에 존재하지 않습니다."}, status=status.HTTP_400_BAD_REQUEST)
        serializer=CommentSerializers(#before : commentDetailSerializers
            comment, 
            data=request.data,
            partial=True
        )
        if serializer.is_valid():
            updated_comment=serializer.save()
            return Response(CommentSerializers(updated_comment).data, status=status.HTTP_202_ACCEPTED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request,pk):
        #댓글 삭제시 대댓글도 삭제 
        comment=self.get_object(pk)
        
        if comment.user!=request.user:
            raise PermissionDenied
        comment.delete()
        return Response(status=status.HTTP_200_OK)

# @method_decorator(silk_profile(name='v1Posts'), name='dispatch')
class v1Posts(APIView):#게시글 조회~> 3개의 게시글: 31query발생 
    
    permission_classes=[IsAuthenticated]
    # @silk_profile(name='View get movie data')
    def get(self, request):#local에서는 get으로 testing / prod에는 post로 변경할 것.
        user_address = request.user.address.regionDepth2 if request.user.address else '연수구'
        boardAnimalTypes=request.data.get("boardAnimalTypes", [])
        categoryType=request.data.get("categoryType", "")
        
        # filter_conditions = {}
        # if user_address:
        #     filter_conditions['user__user_address__regionDepth2'] = user_address
        filter_conditions = {'author__user_address__regionDepth2': user_address}
        if boardAnimalTypes and "전체" not in boardAnimalTypes:
            filter_conditions['boardAnimalTypes__animalTypes__in'] = boardAnimalTypes
        if categoryType and categoryType != "전체":
            filter_conditions['categoryType__categoryType'] = categoryType
        # if boardAnimalTypes:
        #     if "전체" in boardAnimalTypes:
        #         boardAnimalTypes = animalTypes
        #     filter_conditions['boardAnimalTypes__animalTypes__in'] = boardAnimalTypes
        # if categoryType:
        #     if categoryType == "전체":
        #         categoryType=all_categoryType
        #         filter_conditions['categoryType__categoryType__in'] = categoryType
        #     else:
        #         filter_conditions['categoryType__categoryType'] = categoryType

        # print("filter_conditions", filter_conditions)
        filtered_posts = Post.objects.filter(**filter_conditions).distinct()
        serializers=PostListSerializers(filtered_posts, many=True)
        return Response(serializers.data, status=status.HTTP_200_OK if filtered_posts.exists() else status.HTTP_204_NO_CONTENT)
    # {  "boardAnimalTypes":["강아지"], 
    #   "categoryType":"자유"
    # }
class makePost(APIView):#image test 해보기 - with front 
    # authentication_classes=[SessionAuthentication]
    # permission_classes=[IsAuthenticated]
  
    def post(self, request):#게시글 생성    
    #input data:{"content":"test post", "boardAnimalTypes":["강아지"], "Image":[], "categoryType":"장소후기"} 
    #input data: {"content":"test post", "boardAnimalTypes":["새"], "Image":[{"img_path":"https://storage.enuri.info/pic_upload/knowbox/mobile_img/202201/2022010406253633544.jpg"}], "categoryType":"장소후기"}  
        serializer=PostSerializers(data=request.data)
        print("re: ", request.data)
        
        if serializer.is_valid():  
            post=serializer.save(
                author=request.user,
                categoryType=request.data.get("categoryType"),
                boardAnimalTypes=request.data.get("boardAnimalTypes")
            )
            serializer=PostListSerializers(
                post,
                context={'request': request}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PostDetail(APIView):#게시글의 자세한 정보
    def get_object(self, pk):
        try:
            return Post.objects.get(pk=pk)
        except Post.DoesNotExist:
            raise NotFound

    def get(self,request,pk):#1개의 게시글 조회시 15개의 쿼리 발생(15 queries including 8 similar and 8 duplicates) 
        post=self.get_object(pk)
        print("post", post)
        post.viewCount+=1 # 조회수 카운트
        post.save()
        
        serializer = PostDetailSerializers(
            post,
            context={"request":request},
        )
        return Response(serializer.data, status=status.HTTP_200_OK)
        
    def put(self, request, pk):
        post=self.get_object(pk=pk)
        if post.author != request.user:
            raise PermissionDenied
        
        serializer=PostDetailSerializers(
            post, 
            data=request.data,
            partial=True
        )
        print("re: ", request.data)
        if serializer.is_valid():
            try:
                post=serializer.save(
                    category=request.data.get("categoryType"),
                    boardAnimalTypes=request.data.get("boardAnimalTypes"),
                    # Image=request.data.get("Image")
                )
            except serializers.ValidationError as e: 
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
                
            post = serializer.save(category=request.data.get("categoryType"))    
            serializer=PostDetailSerializers(post)
            return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request,pk):#게시글 삭제
        post=self.get_object(pk)    
        if request.user!=post.author:
            raise PermissionDenied("게시글 삭제 권한이 없습니다.")
        post.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
class PostComments(APIView):#게시글에 등록 되어진 댓글, 대댓글
    def get_object(self, pk):
        try:
            return Post.objects.get(pk=pk)
        except Post.DoesNotExist:
            raise NotFound

    def get(self, request, pk):
        comments=Comment.objects.filter(post=pk, parent_comment=None).order_by('createdDate')
         # Pagination 설정
        paginator = Paginator(comments, 5)  # 페이지당 5개의 댓글을 보여줄 경우
        page_number = request.GET.get('page')  # 현재 페이지 번호
        page_obj = paginator.get_page(page_number)

        serializer = ReplySerializers(page_obj, many=True)

        response_data = {
            "comments": serializer.data,
            "total_pages": paginator.num_pages,  # 전체 페이지 수
            "current_page": page_obj.number,  # 현재 페이지 번호
            "has_previous": page_obj.has_previous(),  # 이전 페이지 존재 여부
            "has_next": page_obj.has_next(),  # 다음 페이지 존재 여부
        }
        return Response(response_data, status=status.HTTP_200_OK)
    
    def post(self, request,pk):
        #예외 : 존재 하지 않는 게시글에 댓글 작성 불가
        #예외 : 존재 하지 않는 게시글에 대댓글 작성 불가
        #에외 : 존재 하지 않는 댓글에 대댓글 작성 불가
        #input data:
        # {
        # "parent_comment": null,
        # "content": "댓글1"
        # }
        content=request.data.get("content")
        post=self.get_object(pk=pk)
        print("test: ", post)
        if not content or content.strip()=="":
            return Response({"error":"작성하실 내용을 입력해 주세요."}, status=status.HTTP_400_BAD_REQUEST) 
        
        parent_comment_id = request.data.get("parent_comment", None)#부모댓글 정보 #부모댓글 정보가 전달 되지 않을 경우, None할당(=댓글)
        print("parent_comment_id: ",parent_comment_id)
       
        if parent_comment_id is not None:#대댓글
            try:
                parent_comment = Comment.objects.get(id=parent_comment_id)
                print("parent_comment",parent_comment)
            except Comment.DoesNotExist:
                return Response({"error":"해당 댓글이 존재하지 않습니다."}, status=status.HTTP_404_NOT_FOUND)
        
            comment=Comment.objects.create(
                content=content,
                user=request.user,
                post=parent_comment.post,
                parent_comment=parent_comment
            )
            serializer = ReplySerializers(comment)
            return Response(serializer.data, status=status.HTTP_201_CREATED)           
        
        else: #댓글
            print("댓글")
            comment = Comment.objects.create(
                content=content,
                user=request.user,
                post=post,
                parent_comment=None
            )
            serializer = CommentSerializers(comment)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
           
class PostCommentsDetail(APIView):

    def get_post(self, pk):
        try: 
            return Post.objects.get(pk=pk)
        except Post.DoesNotExist:
            raise NotFound    
        
    def get_comment(self, pk):
        try:
            return Comment.objects.get(pk=pk)
        except Comment.DoesNotExist:
            raise NotFound    
        
    def get(self, request, pk, comment_pk):
        comment=self.get_comment(comment_pk)
        
        return Response(ReplySerializers(comment).data, status=status.HTTP_200_OK)
        # if comment_pk(5)==self.get_post(pk):
        # else:
            # raise NotFound
        
    def put(self, request, pk, comment_pk):#댓글 or 대댓글 수정
        comment=self.get_comment(comment_pk)
        content=request.data.get("content")
        if request.user !=comment.user:
            raise PermissionDenied("수정 권한이 없습니다.")
        
        if not content or content.strip()=="":
            return Response({"error":"수정하실 내용을 입력해 주세요."}, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = ReplySerializers(
            comment,
            data=request.data,
            partial=True,
        )
        if serializer.is_valid():
            comment=serializer.save()
            serializer=ReplySerializers(comment)
            return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

    def delete(self, request,pk, comment_pk):#댓글 삭제
        comment=self.get_comment(comment_pk)
        if request.user!=comment.user:
            raise PermissionDenied("삭제 권한이 없습니다.")
        comment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


def trigger_error(request):
    division_by_zero = 1 / 0





##V2: query-Optomized ~> Model 수정           

class v2_Posts(APIView):#쿼리 최적화 적용 

    permission_classes=[IsAuthenticated]
    def get(self, request):
        
        user_address = request.user.address
       
        if user_address:
            cache_key = f'user_address_{request.user.id}'
            user_regionDepth2 = self._get_user_regionDepth2(cache_key, user_address)
            posts = Post.objects.filter(address__regionDepth2=user_regionDepth2)
        else:
            posts = Post.objects.all().order_by('-createdDate')[:10]
        
        posts = self._optimize_query(posts)
            
        serializer = v2_PostListSerializer(posts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

    def _get_user_regionDepth2(self, cache_key, user_address):
        cache_user_address = cache.get(cache_key)
        if not cache_user_address:
            cache.set(cache_key, user_address, timeout=3600)  #Cache  1 hour
            cache_user_address = user_address
        return cache_user_address.regionDepth2 if cache_user_address else user_address.regionDepth2

    def _optimize_query(self, posts):
        return posts.select_related(
            'author', 'categoryType', 'address'
        ).prefetch_related(
            'boardAnimalTypes'
        ).only(
            'author__username', 'author__profile', 'content', 'categoryType', 'address__regionDepth2',
            'address__regionDepth3', 'viewCount', 'createdDate', 'updatedDate'
        )
    
    def post(self, request): # cacheX: 7_query / cache O: 6_query
        
        user_address = cache.get(f'user_address_{request.user.id}')
        if not user_address:
            user_address = request.user.address
            if user_address:
                cache.set(f'user_address_{request.user.id}', user_address, timeout=3600)  # 1시간 동안 캐시

        if user_address:
            user_regionDepth2 = user_address.regionDepth2
            posts = Post.objects.filter(address__regionDepth2=user_regionDepth2)
        else:
            # 주소가 없는 경우, 빈 결과 반환
            posts = Post.objects.none()
       
        # 필요한 필드만 선택하여 쿼리 최적화
        posts = posts.select_related('author', 'categoryType', 'address').prefetch_related('boardAnimalTypes')
    
        categoryType = request.data.get('categoryType')
        animal_types = request.data.get('boardAnimalTypes')
       
        if categoryType:
            posts = posts.filter(categoryType__boardCategoryType=categoryType)
        if animal_types:
            posts = posts.filter(boardAnimalTypes__animalTypes=animal_types)

        serializer = v2_PostListSerializer(posts, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)
    
    # def post(self,request):
        
    #     posts=Post.objects.select_related(
    #         'author', 'categoryType', 'address'
    #     ).prefetch_related(
    #         'boardAnimalTypes'
    #     )

    #     categoryType = request.data.get('categoryType')
    #     animal_types = request.data.get('boardAnimalTypes')
       
    #     if categoryType:
    #         posts = posts.filter(categoryType__boardCategoryType=categoryType)
    #     if animal_types:
    #         posts = posts.filter(boardAnimalTypes__animalTypes=animal_types)

    #     serializer = v2_PostListSerializer(posts, many=True)

    #     return Response(serializer.data, status=status.HTTP_200_OK)

        
class v3_Posts(APIView):

    permission_classes=[IsAuthenticated]

    def get(self, request):

        user_address = cache.get(f'user_address_{request.user.id}')
        if not user_address:
            user_address = request.user.user_address
            if user_address:
                cache.set(f'user_address_{request.user.id}', user_address, timeout=3600)  # 1시간 동안 캐시

        if user_address:
            user_regionDepth = user_address.regionDepth2
        
        address_regionDepth = Subquery(
            Address.objects.filter(user_id=OuterRef('author')).values('regionDepth2')[:1].values('regionDepth3')[:1], 
            output_field=CharField()
        )
        
        # user_regionDepth = request.user.user_address.first().regionDepth2
        posts = Post.objects.filter(
            address__regionDepth2=user_regionDepth
            ).select_related(
                'author', 'categoryType', 'address'
            ).prefetch_related(
                'boardAnimalTypes'
            ).annotate(
                regionDepth2=address_regionDepth#user_address를 동적으로 전달
            ).only(
                'author__username', 'author__profile',
                'content', 'categoryType', 'address__regionDepth2','address__regionDepth3','viewCount','createdDate', 'updatedDate' 
            )
        serializer = v3_PostListSerializer(posts, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)