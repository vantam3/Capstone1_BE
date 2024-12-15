from rest_framework import serializers
from .models import Book, Review, Genre, UserBook
from django.core.exceptions import ValidationError
import logging 


class ReviewSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)  # Hiển thị tên người dùng thay vì ID

    class Meta:
        model = Review
        fields = ['id', 'book', 'user', 'rating', 'comment', 'created_at']

    def create(self, validated_data):
        # Gán user hiện tại vào review
        request = self.context.get('request')  # Lấy request từ context
        if request and request.user.is_authenticated:
            validated_data['user'] = request.user
        return super().create(validated_data)


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ['id', 'name']

class BookSerializer(serializers.ModelSerializer):
    genres = serializers.StringRelatedField(many=True)

    reviews = ReviewSerializer(many=True, read_only=True)  # Danh sách các đánh giá cho sách

    class Meta:
        model = Book
        fields = [
            'id', 
            'title', 
            'author', 
            'genres',
            'download_link', 
            'gutenberg_id', 
            'image', 
            'summary', 
            'note', 
            'credits', 
            'isbn', 
            'language', 
            'create_at', 
            'reviews'  
        ]
# Initialize logger
logger = logging.getLogger(__name__)

class UserBookSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserBook
        fields = ['title', 'author', 'genre', 'description', 'content', 'cover_image', 'is_approved', 'user', 'original_book']

    def validate_cover_image(self, value):
        if value and value.size > 5 * 1024 * 1024:
            logger.warning(f"Cover image size exceeds limit: {value.size}")  # Log warning if image size exceeds limit
            raise ValidationError("Image size should not exceed 5MB.")
        return value

    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['author'] = f"{user.first_name} {user.last_name}"  # Set author to user's name
        validated_data['user'] = user  # Automatically set the user
        try:
            logger.info(f"Creating book with validated data: {validated_data}")
            return super().create(validated_data)
        except Exception as e:
            logger.error(f"Error during book creation: {str(e)}")
            raise ValidationError("Failed to create the book.")