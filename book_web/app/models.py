# app/models.py
from django.db import models
from django.utils.text import slugify
from django.contrib.auth.models import User

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
    
class UserBook(models.Model):
    GENRE_CHOICES = [
        ('fiction', 'Fiction'),
        ('non-fiction', 'Non-fiction'),
        ('fantasy', 'Fantasy'),
        ('science', 'Science'),
        ('history', 'History'),
    ]
    
    title = models.CharField(max_length=500)
    author = models.CharField(max_length=255)
    genre = models.CharField(max_length=50, choices=GENRE_CHOICES, default='fiction')
    description = models.TextField()
    content = models.TextField()  # Text content of the book
    cover_image = models.ImageField(upload_to='book_covers/', null=True, blank=True)
    is_approved = models.BooleanField(default=False)  # Admin approval status
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Link to the user who created the book
    original_book = models.ForeignKey('Book', on_delete=models.CASCADE, related_name="user_books", null=True, blank=True)

    def __str__(self):
        return self.title









