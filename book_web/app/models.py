# app/models.py
from django.db import models
from django.utils.text import slugify
from django.contrib.auth.models import User
class Genre(models.Model):
    name = models.CharField(max_length=100, unique=True)

class Genre(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class Book(models.Model):
    title = models.CharField(max_length=500)
    author = models.CharField(max_length=255, null=True, blank=True)
    download_link = models.URLField()
    gutenberg_id = models.IntegerField(unique=True)
    image = models.URLField(default='https://example.com/default-image.jpg', blank=True)
    summary = models.TextField(null=True, blank=True)
    note = models.TextField(null=True, blank=True)  # Ghi chú
    credits = models.TextField(null=True, blank=True)  # Credits của sách
    isbn = models.CharField(max_length=13, unique=True, null=True, blank=True)
    language = models.CharField(max_length=20, null=True, blank=True)
    create_at = models.DateTimeField(auto_now_add=True)
    genres = models.ManyToManyField(Genre, related_name='books')  # Quan hệ nhiều-nhiều với Genre

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
    
class BookCreation(models.Model):
    title = models.CharField(max_length=255)  # Tên sách
    author = models.CharField(max_length=255)  # Tác giả
    genre = models.CharField(max_length=100)  # Thể loại 
    description = models.TextField()  # Mô tả
    text = models.TextField()  # Nội dung

    def __str__(self):
        return self.title

