from rest_framework import serializers
from .models import Book

class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = [
            'book_id', 'title', 'author', 'isbn', 'description', 'language',
            'cover_image', 'total_pages', 'view_count', 'status', 'create_at', 'update_at'
        ]

