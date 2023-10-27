from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.response import Response
from . serializers import *
from rest_framework.exceptions import APIException, NotFound
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import api_view, permission_classes
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
        
        serializer = LikeOtherSerializer(instance=request.user, data=request.data, context={'request':request})
        if serializer.is_valid():
            serializer.save()
            print(serializer.data)
            return Response({
                "status": 200,
                "msg": "Success"

            })
        
        return Response({
            'status': status.HTTP_400_BAD_REQUEST,
            'errors': serializer.errors
        })
    
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
    serializer_class = [ ListUsersBlogSerializer]

    def get(self, request):

        blog_list = Blog_post.objects.all()
        
        serializer = ListUsersBlogSerializer(blog_list, many=True)
        
        return Response({
            'status': status.HTTP_200_OK,
            'message': 'success',
            'data': serializer.data
        })
        # return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST) 

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
        