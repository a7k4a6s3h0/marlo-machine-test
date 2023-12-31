# Generated by Django 4.2.6 on 2023-10-27 19:49

import app.data_validation_fun
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0003_blog_post_alter_custom_usermodel_profile_picture_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='blog_post',
            name='comments',
        ),
        migrations.AlterField(
            model_name='blog_post',
            name='content',
            field=models.TextField(validators=[app.data_validation_fun.Data_validation.validate_content]),
        ),
        migrations.AlterField(
            model_name='blog_post',
            name='files',
            field=models.FileField(null=True, upload_to='files/', validators=[django.core.validators.FileExtensionValidator(allowed_extensions=['mp4', 'mov']), app.data_validation_fun.Data_validation.Blog_video_file_validation]),
        ),
        migrations.AlterField(
            model_name='blog_post',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='images/', validators=[django.core.validators.FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'gif', 'webp', 'svg']), app.data_validation_fun.Data_validation.Blog_img_validator]),
        ),
        migrations.AlterField(
            model_name='blog_post',
            name='title',
            field=models.CharField(max_length=128, validators=[app.data_validation_fun.Data_validation.validate_title]),
        ),
        migrations.AlterField(
            model_name='comment',
            name='blog_post',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comments', to='app.blog_post'),
        ),
        migrations.AlterField(
            model_name='custom_usermodel',
            name='profile_picture',
            field=models.ImageField(default='default-img/unknown.jpg', upload_to='images/', validators=[django.core.validators.FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'gif', 'webp', 'svg']), app.data_validation_fun.Data_validation.img_validation]),
        ),
    ]
