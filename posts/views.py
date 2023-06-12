from django.shortcuts import render

from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import SessionAuthentication
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, serializers
from rest_framework.exceptions import NotFound, PermissionDenied, ParseError, ValidationError
from rest_framework.pagination import CursorPagination

from .models import Post, Comment
from .serializers import (
    PostSerializers,PostListSerializer,
    PostListSerializers, PostDetailSerializers, 
    CommentSerializers, ReplySerializers
    )
from .pagination import PaginaitionHandlerMixin
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

# #elasticsearch
# import operator
# from elasticsearch_dsl import Q as QQ
# from functools import reduce
# from django_elasticsearch_dsl.search import Search
# from django_elasticsearch_dsl_drf.viewsets import DocumentViewSet

# from django_elasticsearch_dsl_drf.filter_backends import (
#     FilteringFilterBackend, CompoundSearchFilterBackend)

class CommentPagination(CursorPagination):
    page_size=5
    ordering='createdDate'#createdDate 기준으로 오름차순 정렬

class Comments(APIView, PaginaitionHandlerMixin):
    pagination_class=CommentPagination
    @swagger_auto_schema(
        operation_summary='댓글, 대댓글 조회',
        operation_description='Retrieve paginated list of top-level comments',
        responses={
            200: 'Success',
            400: 'Bad request',
            401: 'Authentication failed',
            403: 'Access denied',
            404: 'Not found',
            500: 'Internal server error'
        },
    )
    def get(self,request):
        all_comments=Comment.objects.filter(parent_comment=None)
        page=self.paginate_queryset(all_comments)
        if page is not None:
            serializer=ReplySerializers(page, many=True)
            return self.get_paginated_response(serializer.data)
        else:
            serializer=ReplySerializers(all_comments, many=True)
        # serializer=ReplySerializers(all_comments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @swagger_auto_schema(
        operation_summary='댓글, 대댓글 생성',
        request_body=openapi.Schema(

            type=openapi.TYPE_OBJECT,
            properties={
                'content': openapi.Schema(
                    description='내용',
                    type=openapi.TYPE_STRING),
                'post': openapi.Schema(
                    description='댓글 or 대댓글이 작성되어진 게시글 번호',
                    type=openapi.TYPE_INTEGER),
                'parent_comment': openapi.Schema(
                    description='댓글 대댓글 구분 토글, if parent_comment==Null: 댓글, else: 대댓글 ',
                    type=openapi.TYPE_INTEGER),
            },
            required=['content', 'post'],
        ),
        responses={
            201: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                    'content': openapi.Schema(type=openapi.TYPE_STRING),
                    'user': openapi.Schema(type=openapi.TYPE_INTEGER),
                    'post': openapi.Schema(type=openapi.TYPE_INTEGER),
                    'parent_comment': openapi.Schema(type=openapi.TYPE_INTEGER),
                    'createdDate': openapi.Schema(type=openapi.TYPE_STRING),
                    'updatedDate': openapi.Schema(type=openapi.TYPE_STRING),
                },
                required=['id', 'content', 'user', 'post', 'createdDate', 'updatedDate'],
            ),
            400: 'Invalid request data',
            404: 'The post or comment does not exist',
            500: 'Internal server error',
        }
    )
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
    
    @swagger_auto_schema(
        operation_summary="특정 댓글 조회",
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'id': openapi.Schema(
                        description="댓글 or 대댓글의 id",
                        type=openapi.TYPE_INTEGER),
                    'content': openapi.Schema(
                        description="댓글 or 대댓글의 내용",
                        type=openapi.TYPE_STRING),
                    'user': openapi.Schema(
                        description="댓글 or 대댓글의 작성자의 pk",
                        type=openapi.TYPE_OBJECT),
                    'post': openapi.Schema(
                        description="댓글 or 대댓글이 존재하는 게시글의 pk",
                        type=openapi.TYPE_INTEGER),
                    'parent_comment': openapi.Schema(
                        description="댓글 or 대댓글 인지 구분(null이면 댓글, 값이면 해당 값을 가진 댓글의 대댓글)",
                        type=openapi.TYPE_INTEGER),
                    'createdDate': openapi.Schema(type=openapi.TYPE_STRING),
                    'updatedDate': openapi.Schema(type=openapi.TYPE_STRING),
                },
                required=['id', 'content', 'user', 'post', 'createdDate', 'updatedDate'],
            ),
            404: 'The comment does not exist',
            500: 'Internal server error',
        }
    )
    def get(self, request, pk):#댓글의 pk로 접속시 해당 댓글이 갖고 있는 대댓글도 같이 조회함
        comment=self.get_object(pk=pk)
        serializer=ReplySerializers(
            comment,
            context={"request":request},                                    
        )
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @swagger_auto_schema(
        operation_summary="특정 댓글 수정",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'content': openapi.Schema(type=openapi.TYPE_STRING),
            },
            required=['content'],
        ),
        responses={
            202: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                    'content': openapi.Schema(type=openapi.TYPE_STRING),
                    'user': openapi.Schema(type=openapi.TYPE_OBJECT),
                    'post': openapi.Schema(type=openapi.TYPE_INTEGER),
                    'parent_comment': openapi.Schema(type=openapi.TYPE_INTEGER),
                    'createdDate': openapi.Schema(type=openapi.TYPE_STRING),
                    'updatedDate': openapi.Schema(type=openapi.TYPE_STRING),
                },
                required=['id', 'content', 'user', 'post', 'createdDate', 'updatedDate'],
            ),
            400: 'Invalid input',
            404: 'The comment does not exist',
            500: 'Internal server error',
        }
    )
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

    @swagger_auto_schema(
        operation_summary="특정 댓글삭제. 해당 댓글 삭제시 종속되어진 대댓글도 모두 삭제",
        responses={
            200: 'OK',
            403: 'Permission denied',
            404: 'Not found'
        }
    )
    def delete(self, request,pk):
        #댓글 삭제시 대댓글도 삭제 
        comment=self.get_object(pk)
        
        if comment.user!=request.user:
            raise PermissionDenied
        comment.delete()
        return Response(status=status.HTTP_200_OK)


    
class PostPagination(CursorPagination):
    page_size=10
    ordering='-createdDate'#생성일 기준 내림차순정렬(5-4-3-2-1)        
class Posts(APIView, PaginaitionHandlerMixin):#image test 해보기 - with front 
    # authentication_classes=[SessionAuthentication]
    # permission_classes=[IsAuthenticated]
    pagination_class=PostPagination
    @swagger_auto_schema(
        operation_summary="모든 게시글 목록 조회",
        responses={
            200: PostListSerializers(many=True)
        },
        
    )
    def get(self, request, format=None):
        all_posts=Post.objects.all()
        page=self.paginate_queryset(all_posts)
        if page is not None:
            serializer=PostListSerializers(page,many=True)
            return self.get_paginated_response(serializer.data)
        else:
            serializer=PostListSerializers(all_posts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @swagger_auto_schema(
        operation_summary="단일 게시글 생성",
        request_body=PostSerializers,
        responses={
            status.HTTP_201_CREATED: PostListSerializers,
            status.HTTP_400_BAD_REQUEST: "Bad Request"
        }
    )
    def post(self, request):#게시글 생성
    #input data:{"content":"test post", "boardAnimalTypes":["강아지"], "Image":[], "categoryType":"장소후기"} 
    #input data: {"content":"test post", "boardAnimalTypes":["새"], "Image":[{"img_path":"https://storage.enuri.info/pic_upload/knowbox/mobile_img/202201/2022010406253633544.jpg"}], "categoryType":"장소후기"}  
        serializer=PostSerializers(data=request.data)
        print("re: ", request.data)
        
        if serializer.is_valid():  
            post=serializer.save(
                user=request.user,
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

class PostDetail(APIView):#게시글의 자세한 정보(+댓글 포함)
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
    
class PostComments(APIView, PaginaitionHandlerMixin ):#게시글에 등록 되어진 댓글, 대댓글
    pagination_class=CommentPagination
    def get_object(self, pk):
        try:
            return Post.objects.get(pk=pk)
        except Post.DoesNotExist:
            raise NotFound

    def get(self, request, pk):
        comments=Comment.objects.filter(post=pk, parent_comment=None)
        page=self.paginate_queryset(comments)
        if page is not None:
            serializer=ReplySerializers(page, many=True)
            return self.get_paginated_response(serializer.data)
        else:
            serializer=ReplySerializers(comments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
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



                




