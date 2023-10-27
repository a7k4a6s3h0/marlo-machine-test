from django.urls import path
from . import views 

urlpatterns = [
    path('register/api',views.User_register.as_view(), name='register/api'),
    path('login/api',views.User_login.as_view(), name='login/api'),
    path('create_blog/api', views.Create_Blog.as_view(), name='create_blog/api'),
    path('blog-posts/', views.BlogPostList.as_view(), name='blog-post-list'),
    path('like/', views.add_like_other.as_view(), name='add-like'),
    path('delete_blog/api', views.delete_blog, name='delete_blog/api'),
    path('edit_blog/api', views.EditBlog.as_view(), name='edit_blog/api'),
    path('block_user/api', views.block_user.as_view(), name='block_user/api'),
    path('list_users/api', views.ListUsers.as_view(), name='list_users/api'),
]
