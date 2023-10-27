from django.db import models
from django.contrib.auth import get_user_model
from . manager import UserManager
from django.contrib.auth.models import AbstractUser
from django.core.validators import FileExtensionValidator
from . data_validation_fun import *

# Create your models here.

class custom_usermodel(AbstractUser):
    validate = Data_validation()
    email = models.CharField(null=False, unique=True, max_length=50)
    profile_picture = models.ImageField(upload_to='images/', default='default-img/unknown.jpg', validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'gif', 'webp', 'svg']), validate.img_validation])
    phone_number = models.BigIntegerField(unique=True, null=False)
    is_blocked = models.BooleanField(default=False, null=False)
    country = models.CharField(null=False, max_length=50)


    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username',"phone_number"]


    def __str__(self) -> str:
        return self.username    
    
class Blog_post(models.Model):
    validation = Data_validation()
    title = models.CharField(max_length=128, validators=[validation.validate_title])
    content = models.TextField(validators=[validation.validate_content])
    author = models.ForeignKey(custom_usermodel, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    total_likes = models.IntegerField(null=True, default=0)
    image = models.ImageField(upload_to='images/', blank=True, null=True, validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'gif', 'webp', 'svg']), validation.Blog_img_validator])
    likers = models.ManyToManyField(custom_usermodel, related_name="BlogPostLikers", blank=True)
    files = models.FileField(upload_to='files/', max_length=100, null=True, validators=[FileExtensionValidator(allowed_extensions=['mp4', 'mov']), validation.Blog_video_file_validation])
    total_dislike = models.IntegerField(null=True, default=0)

    class Meta:
        ordering = ["-created_at", "-updated_at"]

    def __str__(self) -> str:

        return f"{self.author.username} - {self.title} Blog"
    

class Comment(models.Model):

    user = models.ForeignKey(custom_usermodel, on_delete=models.CASCADE)
    blog_post = models.ForeignKey(Blog_post, on_delete=models.CASCADE, related_name="comments")
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)


    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Comment by {self.user.username} on {self.blog_post.title} blog"    