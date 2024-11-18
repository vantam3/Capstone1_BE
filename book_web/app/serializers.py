from rest_framework import serializers
from .models import Book, Review

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



class BookSerializer(serializers.ModelSerializer):
    reviews = ReviewSerializer(many=True, read_only=True)  # Danh sách các đánh giá cho sách

    class Meta:
        model = Book
        fields = [
            'id', 
            'title', 
            'slug', 
            'author', 
            'download_link', 
            'gutenberg_id', 
            'image', 
            'summary', 
            'note', 
            'credits', 
            'isbn', 
            'language', 
            'create_at', 
            'reviews'  # Gắn đánh giá vào sách
        ]
