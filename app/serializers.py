from rest_framework import serializers
from . models import *
from . data_validation_fun import Data_validation

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = custom_usermodel
        fields = ('id', 'username', 'email', 'profile_picture', 'phone_number')


class user_registration(serializers.ModelSerializer):
    
    re_enter_password = serializers.CharField(write_only=True)
    
    class Meta:
        model = custom_usermodel
        fields = ('username', 'email', 'password', 're_enter_password', 'phone_number', 'profile_picture')
        write_only_fields = ('re_enter_password',)
        extra_kwargs = {'password': {'write_only': True}}

    def get_profile_picture_url(self, obj):
       
        request = self.context.get('request')
        
        if obj.profile_picture:
            
            return request.build_absolute_uri(obj.profile_picture.url)
        else:
            
            return None
  
    
    def create(self, validated_data):
        
        """
        Ensure that the email, password and phone number are in a valid format before saving to database
        """  

        validation_obj = Data_validation()
        validation_obj.email_validation(validated_data.get('email'))
        validation_obj.password_validation(validated_data.get('password'))

        password = validated_data.pop('password', None)
        # Remove the 're_enter_password' field from the validated_data dictionary
        password2 = validated_data.pop('re_enter_password', None)
        user_country = validation_obj.phone_number_validation(validated_data.get('phone_number'))
        instance = self.Meta.model(**validated_data)

        if password is not None:
            if password != password2:
                raise serializers.ValidationError({"error":"Both password is not matching"})
            instance.set_password(password)
            instance.country = user_country

        instance.save()
        return instance
    
   

class login_serilalizer(serializers.Serializer):

    email = serializers.CharField(required=True)
    password = serializers.CharField(required=True)

    def validate(self, attrs):
        """
        Ensure that the email and password are in a valid format
        """

        validation_obj = Data_validation()

        if 'email' in attrs:
            validation_obj.email_validation(attrs['email'])
        if 'password' in attrs:
           validation_obj.password_validation(attrs['password'])

        return attrs 
    
class Create_blog_serializer(serializers.ModelSerializer):

    class Meta:
        model = Blog_post
        fields = ('title', 'content', 'image', 'files')  

    def create(self, validated_data):
        request = self.context.get("request")
        try:
            user = custom_usermodel.objects.filter(id=request.user.id).first()
            blog_instance = Blog_post(author=user, **validated_data)
            blog_instance.save()
        except ValidationError as e:
            raise serializers.ValidationError('AUthendication Error. Please check your details')
        return blog_instance
         
class BlogPostSerializer(serializers.ModelSerializer):

    author = UserSerializer(read_only=True)

    class Meta:
        model = Blog_post
        fields = '__all__'

    def get_blog_picture_url(self, obj):
       
        request = self.context.get('request')
        if obj.image:
            
            return request.build_absolute_uri(obj.image.url)
        else:
            
            return None         

    def get_files_url(self, obj):
        request = self.context.get('request')
        if obj.files:
            return request.build_absolute_uri(obj.files.url)
        else:
            return None        
        


class LikeOtherSerializer(serializers.ModelSerializer):

    post_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Blog_post
        fields = ('post_id', 'total_likes','total_dislike')
        write_only_fields = ('post_id',)

    def to_representation(self, instance):
        user = self.context['request'].user
       
        return {
            'commenter': UserSerializer(user).data,
            'comment': instance.comments,
            'post_id': instance.id,
        }    

    def update(self, instance, validated_data):
        post_id = validated_data.pop('post_id', None)
        try:
            blog_post = Blog_post.objects.get(id=post_id)
            
            # Check if the user has already liked the post
            if instance.id not in blog_post.likers.values_list('id', flat=True):
                # Add the user to the likers for the blog post
                blog_post.likers.add(instance.id)
                blog_post.total_likes = validated_data.get('total_likes', blog_post.total_likes)
                blog_post.total_dislike = validated_data.get('total_dislike', blog_post.total_dislike)
                blog_post.save()

                Comment.objects.create(user=instance, blog_post=blog_post, text=validated_data.get('comments', None)).save()

        except ValidationError:
            raise serializers.ValidationError('Blog Not Found..........')    
        return instance
    

    
class Blog_Edit(serializers.ModelSerializer):
    post_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Blog_post
        fields = ['title', 'content', 'image', 'files', 'post_id']
        write_only_fields = ('post_id',)

    def update(self, instance, validated_data):
        post_id = validated_data.pop('post_id', None)
        try:
            blog_post = Blog_post.objects.get(id=post_id)
            blog_post.title = validated_data.get('title', blog_post.title)
            blog_post.content = validated_data.get('content', blog_post.content)
            blog_post.image = validated_data.get('image', blog_post.image)
            blog_post.files = validated_data.get('files', blog_post.files)
            blog_post.save()
        except ValidationError:
            raise serializers.ValidationError('Post Not Found.........')
        return instance
    

class DeleteBlogSerializer(serializers.Serializer):

    post_id = serializers.IntegerField(required=True)


# class ListUsersBlogSerializer(serializers.ModelSerializer):
#     author = UserSerializer(read_only=True)
#     class Meta:
#         model = Blog_post
#         fields = ('title', 'content', 'total_likes','total_dislike', 'author')


class ListUsersBlogSerializer(serializers.ListSerializer):
    child = BlogPostSerializer()    


class blockuser_serializer(serializers.Serializer):

    user_id = serializers.ImageField(required=True)
    