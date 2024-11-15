# app/serializers.py

from rest_framework import serializers
from .models import Book, Review
from django.db.models import Avg

class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ['id', 'title', 'slug', 'author', 'download_link', 'gutenberg_id', 'image', 'summary']

class ReviewSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)  # Display username, read-only

    class Meta:
        model = Review
        fields = ['id', 'book', 'user', 'rating', 'comment', 'created_at']

class BookDetailSerializer(serializers.ModelSerializer):
    reviews = ReviewSerializer(many=True, read_only=True)  # List of book reviews
    average_rating = serializers.SerializerMethodField()  # Average rating

    class Meta:
        model = Book
        fields = [
            'id', 'title', 'author', 'isbn', 'description', 'language', 
            'total_pages', 'view_count', 'status', 'create_at', 
            'update_at', 'reviews', 'average_rating','image'
        ]

    def get_average_rating(self, obj):
        return obj.reviews.aggregate(Avg('rating'))['rating__avg']
