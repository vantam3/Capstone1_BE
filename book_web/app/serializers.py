from rest_framework import serializers
from .models import Book, Review, Genre, BookCreation


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
class BookCreationSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookCreation
        fields = ['id', 'title', 'author', 'genre', 'description', 'text',]        
