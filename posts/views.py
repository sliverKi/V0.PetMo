from django.shortcuts import render
from django.core.paginator import Paginator

from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import SessionAuthentication
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, serializers
from rest_framework.exceptions import NotFound, PermissionDenied, ParseError, ValidationError
from rest_framework.pagination import CursorPagination

from .models import Post, Comment
from users.models import User
from addresses.models import Address
from .serializers import (
    PostSerializers,PostListSerializer,
    PostListSerializers, PostDetailSerializers, 
    CommentSerializers, ReplySerializers,
    v2_PostListSerializer
    )
from .pagination import PaginaitionHandlerMixin
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.db.models import Q
from django.db.models import Count
from django.db.models import Subquery, CharField, OuterRef, Value
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


class v1Posts(APIView):#게시글 조회
    
    permission_classes=[IsAuthenticated]

    def get(self, request):#local에서는 get으로 testing / prod에는 post로 변경할 것.
        user_address = request.user.user_address.regionDepth2 if request.user.user_address else '연수구'
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
        filtered_posts = Post.objects.filter(**filter_conditions).distinct()#47-> 30개 쿼리~> 14쿼리 ~> 4개쿼리
        # filtered_posts = Post.objects.filter(**filter_conditions).annotate(#집계 최적화~> remove @property field 
        #     commentCount=Count('post_comments',  filter=Q(post_comments__parent_comment=None), distinct=True), 
        #     likeCount=Count('postLike', distinct=True),  
        #     bookmarkCount=Count('bookmarks', distinct=True),
        # ).select_related('author', 'author__user_address', 'categoryType').prefetch_related('boardAnimalTypes').distinct()
        print("filter_posts", filtered_posts)

        serializers=PostListSerializers(filtered_posts, many=True)
        
        # 응답 반환
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
                boardAnimalTypes=request.data.get("boardAnimalTypes"),
                Image=request.data.get("Image")
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

    def get(self,request,pk):
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
        print("re: ", request.data)
        if serializer.is_valid():
            try:
                post=serializer.save(
                    category=request.data.get("categoryType"),
                    boardAnimalTypes=request.data.get("boardAnimalTypes"),
                    Image=request.data.get("Image")
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
        if request.user!=post.user:
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

class v2_Posts(APIView):#쿼리 최적화 적용 - 게시글 조회 1. 접속 유저와 동일한 리전의 게시글 목록

    permission_classes=[IsAuthenticated]

    def get(self, request):
        address_regionDepth2 = Subquery(
            Address.objects.filter(user_id=OuterRef('author')).values('regionDepth2')[:1], 
            output_field=CharField()
        )
        user_regionDepth2 = request.user.user_address.regionDepth2
        posts = Post.objects.filter(
            address__regionDepth2=user_regionDepth2
            ).select_related(
                'author', 'categoryType', 'address'
            ).prefetch_related(
                'boardAnimalTypes'
            ).all().annotate(
                regionDepth2=address_regionDepth2
            )
        serializer = v2_PostListSerializer(posts, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)
        
class v2_PostCreate(APIView):
    pass

