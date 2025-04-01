from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.utils.html import escape  # Import for sanitizing user inputs
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.forms import modelformset_factory
from django.contrib.auth.decorators import login_required
from django.urls import reverse  # Import for using reverse instead of hardcoding URLs
from django.contrib.auth.models import User
from django.http import JsonResponse
from .models import Profile, Post, Album, Photo
from .forms import PostForm, RegistrationForm, PhotoForm, AlbumForm, EditProfileForm

# Create your views here.

# View to list all published posts
@login_required(login_url='login')
def post_list(request):
    posts = Post.objects.filter(published_date__lte=timezone.now()).order_by('published_date')
    albums = Album.objects.filter(owner=request.user).order_by('created_at')
    return render(request, 'blog/post_list.html', {'posts': posts, 'albums': albums})

# View to display the details of a specific post
@login_required(login_url='login')
def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    return render(request, 'blog/post_detail.html', {'post': post})

# View to display the profile of a user
@login_required(login_url='login')
def profile(request, user_username):
    user = get_object_or_404(User, username=user_username)
    return render(request, 'blog/profile.html', {'user': user, 'profile': user.profile})

# View to update the about me of the current user
@login_required(login_url='login')
def update_about_me(request, user_username):
    if request.method == 'POST':
        try:
            new_about_me = request.POST.get('about_me')
            if not new_about_me:
                return JsonResponse({'error': 'Description is required'}, status=400)

            user = get_object_or_404(User, username=user_username)
            # Ensure the logged-in user is the one being updated
            if request.user != user:
                return JsonResponse({'error': 'You are not allowed to update this user\'s profile'}, status=403)
            
            user.profile.about_me = new_about_me
            user.profile.save()

            return JsonResponse({'about_me': user.profile.about_me})

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Invalid request method'}, status=405)

# View to edit your own profile
@login_required(login_url='login')
def edit_profile(request):

    profile = request.user.profile

    if request.method == "POST":
        form = EditProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            return redirect(reverse('profile', args=[request.user.username]))
    else:
        form = EditProfileForm(instance=profile)

    return render(request, 'blog/edit_profile.html', {'form': form})

# View to create a new post
@login_required(login_url='login')
def post_new(request):
    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.published_date = timezone.now()
            post.save()
            return redirect('post_detail', pk=post.pk)
    else:
        form = PostForm()
    return render(request, 'blog/post_edit.html', {'form': form})

# View to edit an existing post
@login_required(login_url='login')
def post_edit(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.user != post.author:
        messages.error(request, 'You are not allowed to edit that post.')
        return redirect(reverse('post_list'))  # Use reverse for URL
    else:
        if request.method == "POST":
            form = PostForm(request.POST, instance=post)
            if form.is_valid():
                post = form.save(commit=False)
                post.author = request.user
                post.published_date = timezone.now()
                post.save()
                return redirect('post_detail', pk=post.pk)
        else:
            form = PostForm(instance=post)
        return render(request, 'blog/post_edit.html', {'form': form})

# View to handle user registration
def registerPage(request):
    if request.user.is_authenticated:
        return redirect(reverse('post_list'))  # Use reverse for URL
    else:
        form = RegistrationForm()
        if request.method == 'POST':
            form = RegistrationForm(request.POST)
            if form.is_valid():
                form.save()
                user = escape(form.cleaned_data.get('username'))
                messages.success(request, f'Account was created for {user}')  # Use f-string for clarity
                return redirect(reverse('login'))  # Use reverse for URL
        context = {'form': form}
        return render(request, 'blog/register.html', context)

# View to handle user login
def loginPage(request):
    if request.user.is_authenticated:
        return redirect(reverse('post_list'))  # Use reverse for URL
    if request.method == 'POST':
        username = escape(request.POST.get('username'))
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect(reverse('post_list'))  # Use reverse for URL
        else:
            messages.error(request, 'Username OR password is incorrect')
    context = {}
    return render(request, 'blog/login.html', context)

# View to handle user logout
def logoutUser(request):
    logout(request)
    return redirect(reverse('login'))  # Use reverse for URL

# View to create a new album
@login_required(login_url='login')
def create_album(request):
    if request.method == 'POST':
        form = AlbumForm(request.POST)
        if form.is_valid():
            album = form.save(commit=False)
            album.owner = request.user  # Assign the current user to the album
            album.save()
            return redirect('album_detail', album_id=album.id)
    else:
        form = AlbumForm()

    return render(request, 'blog/create_album.html', {'form': form})

# View to upload a photo to an album
@login_required(login_url='login')
def upload_photos(request, album_id):
    album = get_object_or_404(Album, id=album_id, owner=request.user)  # Only allow the album owner
    if request.method == 'POST':
        formset = modelformset_factory(Photo, form=PhotoForm, extra=0)

        files = request.FILES.getlist('images')

        for file in files:
            photo = Photo(album=album, image=file, caption=file.name)
            photo.save()

        return redirect('album_detail', album_id=album.id)

    else:
        formset = PhotoForm()

    return render(request, 'blog/upload_photos.html', {'formset': formset, 'album': album})

# View to display the details of an album
@login_required(login_url='login')
def album_detail(request, album_id):
    album = get_object_or_404(Album, id=album_id)  # Only allow album owners to see

    # Check if the album belongs to the logged-in user
    if album.owner != request.user:
        # Redirect to another page, e.g., an error page or their album list
        messages.error(request, "You tried to visit an album that is not yours.")
        return redirect(reverse('post_list'))

    photos = album.photos.all()
    return render(request, 'blog/album_detail.html', {'album': album, 'photos': photos})

# # View to edit an existing album
# @login_required(login_url='login')
# def edit_album(request, album_id):
#     album = get_object_or_404(Album, id=album_id)

#     # Check if the user is the owner of the album
#     if album.owner != request.user:
#         messages.error(request, 'You are not allowed to edit that album.')
#         return redirect(reverse('post_list'))

#     if request.method == 'POST':
#         form = AlbumForm(request.POST, instance=album)
#         if form.is_valid():
#             album = form.save(commit=False)
#             album.owner = request.user
#             album.save()
#             return redirect('album_detail', album_id=album.id)

#     else:
#         form = AlbumForm(instance=album)
#     return render(request, 'blog/edit_album.html', {'form': form, 'album': album})

# View to edit the title of an album
@login_required(login_url='login')
def update_album_title(request, album_id):
    if request.method == 'POST':
        try:
            new_title = request.POST.get('title')
            if not new_title:
                return JsonResponse({'error': 'Title is required'}, status=400)

            album = get_object_or_404(Album, id=album_id)

            album.title = new_title
            album.save()

            return JsonResponse({'title': album.title})

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request method'}, status=405)
    
# View to update the description of an album
@login_required(login_url='login')
def update_album_description(request, album_id):
    if request.method == 'POST':
        try:
            new_description = request.POST.get('description')
            if not new_description:
                return JsonResponse({'error': 'Description is required'}, status=400)

            album = get_object_or_404(Album, id=album_id)

            album.description = new_description
            album.save()

            return JsonResponse({'description': album.description})

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Invalid request method'}, status=405)

@login_required(login_url='login')
def delete_photo(request, photo_id):
    # Get the photo object or return a 404 error if not found
    photo = get_object_or_404(Photo, id=photo_id)

    # Check if the user is the owner of the photo or album
    if photo.album.owner == request.user:
        # Delete the photo file
        photo.image.delete()  # Delete the file from the filesystem
        # Delete the photo object from the database
        photo.delete()
        return redirect('album_detail', album_id=photo.album.id)
    else:
        # If the user is not the owner, redirect them or raise an error
        return redirect('album_detail', album_id=photo.album.id)

@login_required(login_url='login')
def photo_detail(request, photo_id):
    photo = Photo.objects.get(id=photo_id)

    if photo.album.owner != request.user:
        messages.error(request, 'You are not allowed to see that photo.')
        return redirect(reverse('post_list'))

    exif_metadata = photo.exif_metadata
    lens_model = photo.lens_model
    camera_model = photo.camera_model

    context = {
        'photo': photo,
        'exif_metadata': exif_metadata,
        'lens_model': lens_model,
        'camera_model': camera_model,
    }
    return render(request, 'blog/photo_detail.html', context)