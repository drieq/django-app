from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Profile, Post, Album, Photo, Tag

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

    def clean_email(self):
        email = self.cleaned_data.get('email')

        # Check if the email already exists
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Email already exists.")

        return email

class AlbumForm(forms.ModelForm):
    tags = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'Add tags separated by commas'}),
        required=False,
        help_text="Enter tags separated by commas. Existing tags can be selected below."
    )

    class Meta:
        model = Album
        fields = ['title', 'description', 'tags']

    def save(self, user=None, commit=True):
        album = super().save(commit=False)

        if user:
            album.owner = user
        else:
            raise ValueError("Cannot find user, album requires an owner.")

        if commit:
            album.save()

        # Handle tags
        tag_names = self.cleaned_data['tags']
        if tag_names:
            tag_names = [name.strip() for name in tag_names.split(',')]
            tags = []
            for name in tag_names:
                tag, created = Tag.objects.get_or_create(name=name, user=user)
                tags.append(tag)
            album.tags.set(tags)
        else:
            album.tags.clear()

        return album

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

class ClientRegistrationForm(UserCreationForm):

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]