# app/models.py

from django.db import models
from django.utils.text import slugify
from django.contrib.auth.models import User

class Book(models.Model):
    title = models.CharField(max_length=500)
    slug = models.SlugField(unique=True, blank=True, max_length=255)
    author = models.CharField(max_length=255, null=True, blank=True)
    download_link = models.URLField()
    gutenberg_id = models.IntegerField(unique=True)
    
    image = models.URLField(default='https://example.com/default-image.jpg', blank=True)
    
    summary = models.TextField(null=True, blank=True)
    isbn = models.CharField(max_length=13, unique=True, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    language = models.CharField(max_length=20, null=True, blank=True)
    total_pages = models.IntegerField(null=True, blank=True)
    view_count = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=20, default='Available')
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            while Book.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

class Review(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField(null=True, blank=True)  # Rating from 1 to 5
    comment = models.TextField(null=True, blank=True)  # Review content
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review for {self.book.title} - Rating: {self.rating}"
