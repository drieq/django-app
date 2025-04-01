from django import forms
from django.contrib.auth.models import User, Group
from .models import Album

class AlbumAdminForm(forms.ModelForm):
    class Meta:
        model = Album
        fields = '__all__'

    def clean_clients(self):
        clients = self.cleaned_data.get('clients', [])
        client_group = Group.objects.get(name="Clients")

        # ✅ Only allow users in the "Clients" group
        valid_clients = User.objects.filter(groups=client_group, id__in=clients)

        return valid_clients