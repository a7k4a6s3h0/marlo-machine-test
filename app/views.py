from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.response import Response
from . serializers import *
from rest_framework.exceptions import APIException, NotFound
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import api_view, permission_classes
from django.db.models import Count
from django.db.models import OuterRef, Subquery
import json
# Create your views here.


class User_register(generics.GenericAPIView):

    serializer_class = user_registration

    def post(self, request):

        serializer = user_registration(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            response = {
                'status': status.HTTP_200_OK,
                'message': "Sucessfully Registerd",
                'result': serializer.data
            }

            return Response(response)
        
        return Response({
            'status': status.HTTP_400_BAD_REQUEST,
            'errors': serializer.errors
        })
    
class User_login(generics.GenericAPIView):

    serializer_class = login_serilalizer   

    def post(self, request):

        serializer = login_serilalizer(data=request.data)

        if serializer.is_valid():

            user = custom_usermodel.objects.filter(email = serializer.data.get("email")).first()
            
            if not user:
                raise APIException("invalid credentails..!")
            
            if not user.check_password(serializer.data.get("password")):
                    raise APIException("invalid Password..!")
            
            if not user.is_blocked:
                refresh = RefreshToken.for_user(user)
                response = {
                    'status': status.HTTP_200_OK,
                    'message':"succcesfully logined",
                    'refresh_token': str(refresh),
                    'access_token': str(refresh.access_token)
                }
                return Response(response)
            else:
                return Response({
                'status': status.HTTP_400_BAD_REQUEST,
                'message': "Your account has been Blocked By admin. Please contact Him"
            })
            
        return Response({
            'status': status.HTTP_400_BAD_REQUEST,
            'errors': serializer.errors
            })
    
class Create_Blog(generics.CreateAPIView):

    permission_classes = [IsAuthenticated]    
    serializer_class = [Create_blog_serializer]

    def post(self, request):
        
        serializer = Create_blog_serializer(data=request.data, context={'request':request})

        if serializer.is_valid():
            serializer.save()

            response = {
                'status': status.HTTP_200_OK,
                'message': 'Blog created Successfully....'
            }

            return Response(response)
        
        return Response({
            'status': status.HTTP_400_BAD_REQUEST,
            'errors': serializer.errors
            })
    
class BlogPostList(generics.ListAPIView):

    permission_classes = [IsAuthenticated]
    serializer_class = BlogPostSerializer    

    def get(self, request):

        queryset = Blog_post.objects.all().order_by('-created_at')[:15]
        serializer = BlogPostSerializer(queryset, many=True, context={'request':request})
            
        return Response({
            'status': status.HTTP_200_OK,
            'posts': serializer.data
        })    

class add_like_other(generics.UpdateAPIView):

    permission_classes = [IsAuthenticated]
    serializer_class = LikeOtherSerializer

    def get(self, request):
        try:
            blog_instance = Blog_post.objects.get(id=request.data.get('post_id', None))
            serializer = LikeOtherSerializer(instance=blog_instance, data=request.data, context={'request':request})
            if serializer.is_valid():
                serializer.save()
                
                return Response({
                    "status": 200,
                    "msg": "Success",
                    "result": serializer.data
                })
            
            return Response({
                'status': status.HTTP_400_BAD_REQUEST,
                'errors': serializer.errors
            })
        except Blog_post.DoesNotExist:
            raise NotFound("No such blog post exists")
        
class EditBlog(generics.UpdateAPIView):

    permission_classes = [IsAuthenticated]
    serializer_class = Blog_Edit

    def put(self, request):

        try:
            
            post_id = request.data['post_id']
            curr_post = Blog_post.objects.get(id=post_id)
            serializer = Blog_Edit(instance=curr_post, data=request.data)

            if serializer.is_valid():
                serializer.save()

                return Response({
                    "status": status.HTTP_200_OK,
                    "msg": "Success",
                    'updated_data': serializer.data
                })

            return Response({
                'status': status.HTTP_400_BAD_REQUEST,
                'errors': serializer.errors
            })

        except Blog_post.DoesNotExist:
            raise NotFound("No such blog post exists")
        
        


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def delete_blog(request):
    serializer = DeleteBlogSerializer(data=request.data)

    if serializer.is_valid():
        post_id = serializer.validated_data['post_id']

        try:
            blog_post = Blog_post.objects.get(id=post_id)

            # Check if the user has permission to delete the blog post
            if request.user == blog_post.author:
                blog_post.delete()
                return Response({'message': 'Blog post deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
            else:
                return Response({'message': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

        except Blog_post.DoesNotExist:
            return Response({'message': 'Blog post not found'}, status=status.HTTP_404_NOT_FOUND)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)    


class ListUsers(generics.ListAPIView):

    permission_classes = [IsAuthenticated]
    serializer_class = [ BlogPostSerializer, ListUsersBlogSerializer]

    def get(self, request):

        
        users_with_likes_dislikes_comments = custom_usermodel.objects.annotate(
            total_likes=Count('reverse_User__likers'),
            total_dislike=Count('reverse_User__total_dislike')
        )
        
        latest_blog_post = Blog_post.objects.filter(author=OuterRef('id')).order_by('-created_at')
        
        users_with_latest_blog = users_with_likes_dislikes_comments.annotate(
            latest_blog_id = Subquery(latest_blog_post.values('id')[:1]),
            latest_blog_title=Subquery(latest_blog_post.values('title')[:1]),
            latest_blog_content=Subquery(latest_blog_post.values('content')[:1]),
            latest_blog_image=Subquery(latest_blog_post.values('image')[:1]),
            latest_blog_file=Subquery(latest_blog_post.values('files')[:1]),
            latest_blog_comments=Subquery(latest_blog_post.values('comments__text')[:1])
        )

        
        result = [{
                'user': user.username,
                'total_likes': user.total_likes,
                'total_dislike': user.total_dislike,
                'latest_blog': {
                    'title': user.latest_blog_title,
                    'content': user.latest_blog_content,
                    'image': user.latest_blog_image,
                    'file': user.latest_blog_file,
                    'comments': user.latest_blog_comments,
                }
            }
            for user in users_with_latest_blog
        ]
        
        print(json.dumps(result, indent=4))
        
        blog_posts = Blog_post.objects.all()


        serializer = BlogPostSerializer(blog_posts, many=True, context={'request':request})
        
        return Response({
            'status': status.HTTP_200_OK,
            'message': 'success',
            'data': result
        })
        

class block_user(generics.UpdateAPIView):

    permission_classes = [IsAuthenticated]
    serializer_class = blockuser_serializer

    def put(self, request):

        serializer = blockuser_serializer(data=request.data)
        if serializer.is_valid():
            if request.user.is_superuser:
                curr_user = custom_usermodel.objects.get(id=serializer.get('user_id', None))
                curr_user.is_blocked = True
                curr_user.save()
                return Response({"success": "User blocked successfully"}, status=201)
            else:
                return Response({"error":"You don't have permissions for this action."}, status=403)
            
        return Response(serializer.errors, status=400)
        