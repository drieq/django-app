from django.urls import path
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    # Home Page (list posts)
    path('', views.post_list, name='post_list'),

    # User authentication URLs
    path('register/', views.registerPage, name='register'),
    path('activate/<str:uidb64>/<str:token>/', views.activate_account, name='activate_account'),
    path('login/', views.loginPage, name='login'),
    path('logout/', views.logoutUser, name='logout'),

    # User Profile URLs
    path('user/<str:user_username>/', views.profile, name='profile'),
    path('user/<str:user_username>/update-about-me/', views.update_about_me, name='update_about_me'),

    # Client Registration URL
    path('create-client/', views.create_client, name='create_client'),

    # Album URLs
    path('create-album/', views.create_album, name='create_album'),
    path('album/<int:album_id>/', views.album_detail, name='album_detail'),
    path('album/<int:album_id>/update-title/', views.update_album_title, name='update_album_title'),
    path('album/<int:album_id>/update-description/', views.update_album_description, name='update_album_description'),
    path('delete_album/<int:album_id>/', views.delete_album, name='delete_album'),
    path('album/<int:album_id>/upload/', views.upload_photos, name='upload_photos'),
    path('album/<int:album_id>/reorder/', views.reorder_photos, name='reorder_photos'),

    # Photo URLs
    path('delete_photo/<int:photo_id>/', views.delete_photo, name='delete_photo'),
    path('photo/<int:photo_id>/', views.photo_detail, name='photo_detail'),
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
