from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Profile, Post, Album, Photo

class EditProfileForm(forms.ModelForm):

    class Meta:
        model = Profile
        fields = ['about_me']

class PostForm(forms.ModelForm):

    class Meta:
        model = Post
        fields = ('title', 'text')

class RegistrationForm(UserCreationForm):

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class AlbumForm(forms.ModelForm):
    class Meta:
        model = Album
        fields = ['title', 'description']

class PhotoForm(forms.ModelForm):
    class Meta:
        model = Photo
        fields = ['image', 'caption']

    # Custom validation for image field to only allow JPG or PNG
    def clean_image(self):
        image = self.cleaned_data.get('image')

        # Check if file is provided
        if not image:
            raise ValidationError("No image selected.")

        # Allowed file extensions
        valid_extensions = ['.jpg', '.jpeg', '.png']

        # Get the file extension
        extension = image.name.split('.')[-1].lower()

        if extension not in valid_extensions:
            raise ValidationError("Only JPG or PNG files are allowed.")

        return image