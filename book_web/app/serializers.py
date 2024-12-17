from rest_framework import serializers
from .models import Book, Review, Genre, Embedding, FavoriteBook
from .models import ReadingHistory

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
            'subject',  
            'isbn', 
            'language', 
            'create_at', 
            'reviews'  # Gắn đánh giá vào sách
        ]
    def get_average_rating(self, obj):
        reviews = obj.reviews.all()
        if reviews:
            avg_rating = sum([review.rating for review in reviews]) / len(reviews)
            return round(avg_rating, 1)
        return 0


class EmbeddingSerializer(serializers.ModelSerializer):
    book = BookSerializer(read_only=True)  # Sử dụng nested serializer cho sách

    class Meta:
        model = Embedding
        fields = ['id', 'book','similarity']  # Không còn 'similarity' nếu không có trong model

# serializers.py
from rest_framework import serializers

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
    confirm_password = serializers.CharField(required=True)


class FavoriteBookSerializer(serializers.ModelSerializer):
    book = BookSerializer()

    class Meta:
        model = FavoriteBook
        fields = ['id', 'book']

class ReadingHistorySerializer(serializers.ModelSerializer):
    book_title = serializers.CharField(source='book.title')
    book_author = serializers.CharField(source='book.author')
    book_image = serializers.CharField(source='book.image')

    class Meta:
        model = ReadingHistory
        fields = ['id', 'book_title', 'book_author', 'book_image', 'read_at']