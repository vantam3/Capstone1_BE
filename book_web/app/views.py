from django.shortcuts import render
from django.http import JsonResponse
from .models import Book, Genre, Author, Review, UserPreference
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User

def list_books(request):
    books = Book.objects.all()  # Truy vấn tất cả sách từ cơ sở dữ liệu
    book_list = list(books.values('id', 'title', 'author', 'genre', 'description'))  # Chuyển đổi QuerySet thành list dạng JSON
    return JsonResponse(book_list, safe=False)
def get_books_by_genre(request, genre_id):
    books = Book.objects.filter(genre_id=genre_id)
    return JsonResponse(list(books.values()), safe=False)

def get_books_by_author(request, author_id):
    books = Book.objects.filter(author_id=author_id)
    return JsonResponse(list(books.values()), safe=False)

def get_books_by_user_preference(request, user_id):
    user_preference = UserPreference.objects.get(user_id=user_id)
    books = Book.objects.filter(genre__in=user_preference.favorite_genres.all())
    return JsonResponse(list(books.values()), safe=False)

# def get_book_reviews(request, book_id):
#     reviews = Review.objects.filter(book_id=book_id)
#     return JsonResponse(list(reviews.values()), safe=False)
def get_reviews_for_book(request, book_id):
    try:
        book = Book.objects.get(id=book_id)
    except Book.DoesNotExist:
        return JsonResponse({'error': 'Book not found'}, status=404)

    reviews = Review.objects.filter(book=book)
    review_list = list(reviews.values('user__username', 'rating', 'comment','created_at'))

    return JsonResponse(review_list, safe=False)


@csrf_exempt
def add_review(request):
    if request.method == 'POST':
        book_id = request.POST.get('book_id')
        user_id = request.POST.get('user_id')
        rating = request.POST.get('rating')
        comment = request.POST.get('comment')
    
         # Đảm bảo các trường rating và book_id đều có giá trị hợp lệ
        if not (1 <= int(rating) <= 5):
            return JsonResponse({'error': 'Invalid rating value, must be between 1 and 5'}, status=400)

        try:
            book = Book.objects.get(id=book_id)
            user = User.objects.get(id=user_id)
        except Book.DoesNotExist:
            return JsonResponse({'error': 'Book not found'}, status=404)
        except User.DoesNotExist:
            return JsonResponse({'error': 'User not found'}, status=404)


        review = Review.objects.create(book=book, user=user, rating=rating, comment=comment)
        return JsonResponse({'status': 'success', 'review_id': review.id})
