# Generated by Django 5.1.7 on 2025-04-04 19:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0007_album_clients'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='photo',
            options={'ordering': ['order']},
        ),
        migrations.AddField(
            model_name='photo',
            name='order',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
