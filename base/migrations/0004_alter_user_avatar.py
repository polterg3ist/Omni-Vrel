# Generated by Django 5.0 on 2024-01-24 17:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0003_user_avatar'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='avatar',
            field=models.ImageField(default='avatars/avatar.svg', null=True, upload_to=''),
        ),
    ]
