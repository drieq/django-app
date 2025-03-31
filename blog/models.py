from django.conf import settings
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from .utils import get_exif_data
from PIL import Image

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    about_me = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.user.username

class Post(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    text = models.TextField()
    created_date = models.DateTimeField(default=timezone.now)
    published_date = models.DateTimeField(blank=True, null=True)

    def publish(self):
        self.published_date = timezone.now()
        self.save()

    def __str__(self):
        return self.title

# Album model to group photos together
class Album(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='albums')

    def __str__(self):
        return self.title

# Photo model to store images and their metadata
class Photo(models.Model):
    album = models.ForeignKey(Album, on_delete=models.CASCADE, related_name='photos')
    image = models.ImageField(upload_to='photos/%Y/%m/%d/')
    caption = models.CharField(max_length=255, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # Set caption to the filename if it's not set already (on first save)
        if not self.caption:
            self.caption = self.image.name.split('/')[-1]  # Get the filename from the image path
        super().save(*args, **kwargs)  # Call the original save method

    @property
    def exif_metadata(self):
        return get_exif_data(self.image.path)  # Retrieve metadata

    @property
    def lens_model(self):
        exif = self.exif_metadata
        return exif.get("LensModel", "Unknown") if exif else "Unknown"

    @property
    def camera_model(self):
        exif = self.exif_metadata
        return exif.get("Model", "Unknown") if exif else "Unknown"

    def __str__(self):
        return self.caption or f"Photo {self.id}"