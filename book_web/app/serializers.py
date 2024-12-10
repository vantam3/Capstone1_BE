from rest_framework import serializers
from .models import Book, Review, Genre, Embedding

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
            'subject',  # Đổi từ 'summary' thành 'subject'
            'isbn', 
            'language', 
            'create_at', 
            'reviews'  # Gắn đánh giá vào sách
        ]


class EmbeddingSerializer(serializers.ModelSerializer):
    book = BookSerializer(read_only=True)  # Sử dụng nested serializer cho sách

    class Meta:
        model = Embedding
        fields = ['id', 'book','similarity']  # Không còn 'similarity' nếu không có trong model
