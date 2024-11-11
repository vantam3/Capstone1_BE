from rest_framework import serializers
from .models import Book, Review
from django.db.models import Avg

class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = [
            'book_id', 'title', 'author', 'isbn', 'description', 'language',
            'cover_image', 'total_pages', 'view_count', 'status', 'create_at', 'update_at'
        ]

class ReviewSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)  # Hiển thị tên người dùng, chỉ đọc

    class Meta:
        model = Review
        fields = ['id', 'book', 'user', 'rating', 'content', 'created_at']

class BookDetailSerializer(serializers.ModelSerializer):
    reviews = ReviewSerializer(many=True, read_only=True)  # Danh sách các đánh giá của sách

    class Meta:
        model = Book
        fields = [
            'book_id', 'title', 'author', 'isbn', 'description', 'language',
            'cover_image', 'total_pages', 'view_count', 'status', 'create_at', 'update_at', 'reviews'
        ]
    def get_average_rating(self, obj):
        return obj.reviews.aggregate(Avg('rating'))['rating__avg']