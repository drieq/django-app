from django.contrib import admin
from django.contrib.auth.models import User, Group
from .models import Profile, Post, Album, Photo

class AlbumAdmin(admin.ModelAdmin):
    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == "clients":
            try:
                client_group, created = Group.objects.get_or_create(name="Clients")
                kwargs["queryset"] = User.objects.filter(groups=client_group.id)  # ✅ Show only Clients
            except Group.DoesNotExist:
                kwargs["queryset"] = User.objects.none()  # If Clients group doesn't exist, show empty list

        return super().formfield_for_manytomany(db_field, request, **kwargs)

admin.site.register(Profile)
admin.site.register(Post)
admin.site.register(Album, AlbumAdmin)
admin.site.register(Photo)