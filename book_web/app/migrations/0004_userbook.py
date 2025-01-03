# Generated by Django 5.1.1 on 2024-12-18 17:21

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0003_readinghistory'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='UserBook',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=500)),
                ('author', models.CharField(max_length=255)),
                ('genre', models.CharField(choices=[('fiction', 'Fiction'), ('non-fiction', 'Non-fiction'), ('fantasy', 'Fantasy'), ('science', 'Science'), ('history', 'History')], default='fiction', max_length=50)),
                ('description', models.TextField()),
                ('content', models.TextField()),
                ('cover_image', models.ImageField(blank=True, null=True, upload_to='book_covers/')),
                ('is_approved', models.BooleanField(default=False)),
                ('original_book', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='user_books', to='app.book')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
