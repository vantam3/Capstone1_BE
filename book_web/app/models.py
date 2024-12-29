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
    download_link = models.TextField(null=True, blank=True)  # Lưu cả URL hoặc nội dung sách
    gutenberg_id = models.IntegerField(unique=True)
    image = models.URLField(default='https://example.com/default-image.jpg', blank=True)
    subject = models.TextField(null=True, blank=True)  # Đổi tên từ summary sang subject
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
    


#embedding
from django.db import models
import pickle

class Embedding(models.Model):
    book = models.OneToOneField(
        'Book',
        on_delete=models.CASCADE,
        related_name='embedding'
    )
    vector = models.BinaryField()  # Lưu trữ dữ liệu dưới dạng nhị phân

    def set_vector(self, array):
        """Lưu numpy.array dưới dạng binary"""
        self.vector = pickle.dumps(array)

    def get_vector(self):
        """Truy xuất numpy.array từ binary"""
        return pickle.loads(self.vector)

class FavoriteBook(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="favorite_books")
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    
    class Meta:
        unique_together = ('user', 'book')  # Ensure a book is only favorited once by a user

    def __str__(self):
        return f'{self.user.username} - {self.book.title}'
    
    
class ReadingHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reading_history')
    book = models.ForeignKey('Book', on_delete=models.CASCADE, related_name='history')
    read_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} read {self.book.title}"
    
    
class UserBook(models.Model):
    GENRE_CHOICES = [
        ('fiction', 'Fiction'),
        ('non-fiction', 'Non-fiction'),
        ('fantasy', 'Fantasy'),
        ('science', 'Science'),
        ('history', 'History'),
        ('other', 'Other'),

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