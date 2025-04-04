from django.urls import path
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('', views.post_list, name='post_list'),

    path('post/<int:pk>/', views.post_detail, name='post_detail'),
    path('post/new/', views.post_new, name='post_new'),
    path('post/<int:pk>/edit/', views.post_edit, name='post_edit'),

    path('register/', views.registerPage, name='register'),
    path('login/', views.loginPage, name='login'),
    path('logout/', views.logoutUser, name='logout'),

    path('user/<str:user_username>/', views.profile, name='profile'),
    path('user/<str:user_username>/update-about-me/', views.update_about_me, name='update_about_me'),

    path('create-client/', views.create_client, name='create_client'),

    path('create_album/', views.create_album, name='create_album'),
    path('album/<int:album_id>/', views.album_detail, name='album_detail'),
    path('album/<int:album_id>/update-title/', views.update_album_title, name='update_album_title'),
    path('album/<int:album_id>/update-description/', views.update_album_description, name='update_album_description'),
    # path('album/<int:album_id>/edit/', views.edit_album, name='edit_album'),
    path('album/<int:album_id>/upload/', views.upload_photos, name='upload_photos'),
    
    path('delete_photo/<int:photo_id>/', views.delete_photo, name='delete_photo'),
    path('photo/<int:photo_id>/', views.photo_detail, name='photo_detail'),
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)