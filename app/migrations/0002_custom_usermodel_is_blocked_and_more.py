# Generated by Django 4.2.6 on 2023-10-27 12:42

import app.data_validation_fun
import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='custom_usermodel',
            name='is_blocked',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='custom_usermodel',
            name='profile_picture',
            field=models.ImageField(default='default-img/unknown.jpg', upload_to='images/', validators=[django.core.validators.FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'gif', 'webp', 'svg']), app.data_validation_fun.Data_validation.img_validation]),
        ),
    ]