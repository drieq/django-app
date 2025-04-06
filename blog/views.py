from django.conf import settings
from django.core.mail import send_mail
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.models import User, Group
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.sites.models import Site
from django.contrib.sites.shortcuts import get_current_site
from django.forms import modelformset_factory
from django.http import JsonResponse
from django.urls import reverse
from django.utils import timezone
from django.utils.html import escape
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.shortcuts import render, get_object_or_404, redirect
from django.template.loader import render_to_string
from django.views.decorators.http import require_POST
from .models import Profile, Post, Album, Photo, Tag
from .forms import PostForm, RegistrationForm, PhotoForm, AlbumForm, EditProfileForm, ClientRegistrationForm
import json

# Helper function to check if the user is a photographer
def is_photographer(user):
    return user.groups.filter(name="Photographers").exists()

def custom_user_passes_test(test_func, redirect_url='post_list', error_message="You don't have permission to access this page"):
    """
    Custom decorator to check a test condition.
    If the test fails, redirect the user to a specified URL with an error message.
    """
    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            if not test_func(request.user):
                # Show an error message and redirect to a specified page
                messages.error(request, error_message)
                return redirect(reverse('post_list'))  # Redirect to the desired page (e.g., post_list or home)
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator

# View to list all published posts (Accessible by photographers)
@login_required(login_url='login')
def post_list(request):

    if request.user.groups.filter(name="Photographers").exists():

        albums = Album.objects.filter(owner=request.user).order_by('created_at')
        return render(request, 'blog/post_list.html', {'albums': albums})

    elif request.user.groups.filter(name="Clients").exists():

        shared_albums = Album.objects.filter(clients=request.user)
        return render(request, 'blog/post_list_client.html', {'shared_albums': shared_albums})

    albums = {}
    return render(request, 'blog/post_list.html', {'albums': albums})


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

# View to create a new post (Photographers only)
@login_required(login_url='login')
@user_passes_test(is_photographer)
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

# View to create a new album (Photographers only)
@login_required(login_url='login')
@user_passes_test(is_photographer)
def create_album(request):
    if request.method == 'POST':
        form = AlbumForm(request.POST, request.FILES)
        if form.is_valid():
            album = form.save(user=request.user)
            return redirect('album_detail', album_id=album.id)
    else:
        form = AlbumForm()

    return render(request, 'blog/create_album.html', {'form': form})

# View to edit the title of an album
@login_required(login_url='login')
@user_passes_test(is_photographer)
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
@user_passes_test(is_photographer)
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

def get_tags(request):
    query = request.GET.get('search', '')
    tags = Tag.objects.filter(name__icontains=query)  # Case-insensitive search
    tag_data = [{'name': tag.name} for tag in tags]
    return JsonResponse(tag_data, safe=False)

def update_album_tags(request, album_id):
    if request.method == 'POST' and request.is_ajax():
        album = get_object_or_404(Album, id=album_id)
        tags_data = request.POST.get('tags', '').split(',')
        tags = Tag.objects.filter(name__in=tags_data)  # Filter tags by names

        album.tags.set(tags)  # Update the tags for the album
        album.save()

        return JsonResponse({'message': 'Tags updated successfully'}, status=200)
    return JsonResponse({'message': 'Invalid request'}, status=400)

@login_required(login_url='login')
@user_passes_test(is_photographer)
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
@user_passes_test(is_photographer)
def delete_album(request, album_id):
    # Get the photo object or return a 404 error if not found
    album = get_object_or_404(Album, id=album_id)

    # Check if the user is the owner of the photo or album
    if album.owner == request.user:

        for photo in album.photos.all():
            photo.image.delete()
            photo.delete()

        album.delete()

        return redirect(reverse('post_list'))
    else:
        # If the user is not the owner, redirect them or raise an error
        return redirect('album_detail', album_id=album.id)

# View to upload a photo to an album (Photographers only)
@login_required(login_url='login')
@custom_user_passes_test(is_photographer, redirect_url='post_list', error_message="You are not authorized to perform this action.")
def upload_photos(request, album_id):

    album = get_object_or_404(Album, id=album_id, owner=request.user)

    if not request.user.groups.filter(name="Photographers").exists():
        return JsonResponse({'error': 'You are not authorized to upload photos.'}, status=403)

    if request.method == 'POST':
        # formset = modelformset_factory(Photo, form=PhotoForm, extra=0)
        files = request.FILES.getlist('images')
        uploaded_photos = []

        rendered_html = []
        success = True

        for file in files:
            try:
                photo = Photo(album=album,
                              image=file,
                              caption=file.name,
                              order=album.photos.count() + 1)
                photo.save()
                uploaded_photos.append({
                    'id': photo.id,
                    'url': photo.image.url,
                    'caption': photo.caption,
                })

                photo_html = render_to_string("blog/partials/photo_card.html", {
                    "photo": photo
                }, request=request)

                rendered_html.append(photo_html)


            except Exception as e:
                success = False
                print(f"Error uploading photo {file.name}: {e}")

        if success:
            return JsonResponse({'uploaded_photos': uploaded_photos, "rendered_html": rendered_html})
        else:
            return JsonResponse({'error': 'Some photos could not be uploaded.'}, status=500)
    else:
        formset = PhotoForm()

    return render(request, 'blog/upload_photos.html', {'formset': formset, 'album': album})


        # if request.FILES.getlist('images'):

        #     uploaded_photos = []
        #     for image in request.FILES.getlist('images'):
        #         photo = Photo.objects.create(album=album, image=image)
        #         uploaded_photos.append({
        #             'id': photo.id,
        #             'url': photo.image.url,
        #         })
        #     print("Uploaded photos list:", uploaded_photos)  # Debugging line
        #     return JsonResponse({'uploaded_photos': uploaded_photos})

        # return JsonResponse({'error': 'Invalid requesttt'}, status=400)

    # -----------------------------

    #     formset = modelformset_factory(Photo, form=PhotoForm, extra=0)
    #     files = request.FILES.getlist('images')

    #     for file in files:
    #         photo = Photo(album=album, image=file, caption=file.name)
    #         photo.save()

    #     return redirect('album_detail', album_id=album.id)
    # else:
    #     formset = PhotoForm()

    # return render(request, 'blog/upload_photos.html', {'formset': formset, 'album': album})

@login_required(login_url='login')
@require_POST
def update_caption(request, photo_id):
    try:
        photo = Photo.objects.get(id=photo_id, album__owner=request.user)
    except Photo.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Photo not found or access denied.'}, status=404)

    try:
        data = json.loads(request.body)
        new_caption = data.get('caption', '').strip()

        if new_caption:
            photo.caption = new_caption
            photo.save()
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'error': 'Caption cannot be empty.'}, status=400)

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

# View to display album details (Accessible by both photographers and clients)
@login_required(login_url='login')
def album_detail(request, album_id):
    album = get_object_or_404(Album, id=album_id)
    is_photographer = request.user.groups.filter(name="Photographers").exists()

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest' and request.method == 'GET':
        if not is_photographer:
            return JsonResponse({'error': 'You are not authorized to upload photos.'}, status=403)

    if album.owner != request.user and request.user not in album.clients.all():
        messages.error(request, "You do not have access to this album.")
        return redirect(reverse('post_list'))

    # photos = album.photos.all()
    photos = album.photos.order_by('order', 'id')

    return render(request, 'blog/album_detail.html', {'album': album, 'photos': photos, 'is_photographer': is_photographer})

@login_required(login_url='login')
@require_POST
def reorder_photos(request, album_id):
    album = get_object_or_404(Album, id=album_id, owner=request.user)

    try:
        data = json.loads(request.body)
        photo_ids = data.get('order', [])

        for index, photo_id in enumerate(photo_ids):
            Photo.objects.filter(id=photo_id, album=album).update(order=index)

        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)

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

# View for clients to view albums (Clients only)
@login_required(login_url='login')
@user_passes_test(lambda u: u.groups.filter(name="Clients").exists())
def client_dashboard(request):
    albums = Album.objects.filter(clients=request.user)
    return render(request, 'blog/client_dashboard.html', {'albums': albums})

# View to handle user registration
def registerPage(request):

    if request.user.is_authenticated:
        return redirect(reverse('post_list'))

    form = RegistrationForm()

    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()

            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(str(user.pk).encode())

            current_site = get_current_site(request)
            mail_subject = 'Activate Your Account'
            message = render_to_string('blog/activation_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': uid,
                'token': token,
            })
            send_mail(mail_subject, message, settings.EMAIL_HOST_USER, [user.email])
            messages.success(request, 'Please check your email to activate your account.')
            return redirect(reverse('login'))

    context = {'form': form}
    return render(request, 'blog/register.html', context)

# View to activate account
def activate_account(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = get_user_model().objects.get(pk=uid)

        if default_token_generator.check_token(user, token):
            user.is_active = True
            user.save()
            messages.success(request, 'Your account has been activated. You can now log in.')
            return redirect(reverse('login'))
        else:
            messages.error(request, 'The activation link is invalid or has expired.')
            return redirect(reverse('login'))

    except (TypeError, ValueError, OverflowError, get_user_model().DoesNotExist):
        messages.error(request, 'Invalid activation link')
        return redirect(reverse('login'))

# View to handle user login
def loginPage(request):

    if request.user.is_authenticated:
        return redirect(reverse('post_list'))

    if request.method == 'POST':
        username = escape(request.POST.get('username'))
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect(reverse('post_list'))
        else:
            messages.error(request, 'Incorrect username or password.')
    context = {}
    return render(request, 'blog/login.html', context)

# View to handle user logout
def logoutUser(request):
    logout(request)
    return redirect(reverse('login'))

# View to handle client registration (Photographers only)
@login_required(login_url='login')
@user_passes_test(is_photographer)
def create_client(request):
    form = ClientRegistrationForm()

    if request.method == "POST":
        form = ClientRegistrationForm(request.POST)
        if form.is_valid():
            client = form.save(commit=False)
            client.set_password(form.cleaned_data['password1'])
            client.save()

            client.groups.clear()

            # Assign client to Clients group
            client_group = Group.objects.get_or_create(name="Clients")[0]
            client.groups.add(client_group)

            username = escape(client.username)
            messages.success(request, f'Account was created for {username}')
            return redirect(reverse('post_list'))

    return render(request, "blog/create_client.html", {"form": form})
