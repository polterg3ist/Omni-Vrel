from django.db import models
from django.contrib.auth.models import AbstractUser
#from django.core.files.storage import MediaStorage
from django.conf import settings

from io import BytesIO
import sys
import os
from PIL import Image
from django.core.files.uploadedfile import InMemoryUploadedFile

from .utils import upload_to

from django.utils import timezone
from django.core.cache import cache


# Create your models here.

# class OverwriteStorage(MediaStorage):
#     def get_available_name(self, name, max_length=None):
#         if self.exists(name):
#             os.remove(os.path.join(settings.MEDIA_ROOT, name))
#         return name

class User(AbstractUser):
    name = models.CharField(max_length=200, null=True)
    email = models.EmailField(unique=True, null=True)
    email_verify = models.BooleanField(default=False)
    bio = models.TextField(null=True)
    #avatar = models.ImageField(null=True, default="avatar.svg", storage=OverwriteStorage(),
    #                          upload_to=lambda inst, fn: upload_to(inst, fn, 'avatar'))
    avatar = models.ImageField(null=True, default="avatar.svg", upload_to=lambda inst, fn: upload_to(inst, fn, 'avatar'))
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def save(self, *args, **kwargs):
        # Проверяем, было ли уже загружено изображение
        if self.avatar and not self.avatar._committed:
            # Если изображение не было загружено ранее, сжимаем его
            self.avatar = self.compress_image(self.avatar)
        super(User, self).save(*args, **kwargs)

    def compress_image(self, avatar):
        image_temporary = Image.open(avatar)
        image_temporary = image_temporary.convert('RGB')
        output_io_stream = BytesIO()
        # Производим сжатие до нужных размеров или качества
        # Например, изменяем размер до 1020x573 и качество до 60%
        original_width, original_height = image_temporary.size
        aspect_ratio = round(original_width / original_height, 2)
        desired_height = 100  # Edit to add your desired height in pixels
        desired_width = int(desired_height * aspect_ratio)
        image_temporary_resized = image_temporary.resize((desired_width, desired_height))
        image_temporary_resized.save(output_io_stream, format='JPEG', quality=60)
        output_io_stream.seek(0)
        # Создаем новый экземпляр InMemoryUploadedFile с сжатым изображением
        compressed_avatar = InMemoryUploadedFile(output_io_stream, 'ImageField', "%s.jpg" % avatar.name.split('.')[0],
                                                 'image/jpeg', sys.getsizeof(output_io_stream), None)
        return compressed_avatar

    def is_online(self):
        last_seen = cache.get(f'last-seen-{self.id}')
        if last_seen is not None and timezone.now() < last_seen + timezone.timedelta(seconds=300):
            return True
        return False


class Topic(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class Room(models.Model):
    host = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    topic = models.ForeignKey(Topic, on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    participants = models.ManyToManyField(User, related_name='participants', blank=True)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-updated', '-created']

    def __str__(self):
        return self.name


class Message(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    body = models.TextField()
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-updated', '-created']

    def __str__(self):
        if len(self.body) > 80:
            return f"{self.body[0:80]}..."
        return self.body
