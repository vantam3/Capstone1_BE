from rest_framework import serializers
from .models import Book, Review
from django.db.models import Avg
from django.contrib.auth.models import User

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    confirm_password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'confirm_password', 'first_name', 'last_name')

    def validate(self, attrs):
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError({"password": "Mật khẩu không khớp."})
        return attrs

    def create(self, validated_data):
        validated_data.pop('confirm_password')
        user = User.objects.create_user(
            username=validated_data['email'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name']
        )
        return user

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