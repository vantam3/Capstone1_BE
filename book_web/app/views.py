from django.shortcuts import render
from django.http import JsonResponse
from .models import Book, Genre, Author, Review, UserPreference
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User

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

def get_book_reviews(request, book_id):
    reviews = Review.objects.filter(book_id=book_id)
    return JsonResponse(list(reviews.values()), safe=False)

@csrf_exempt
def add_review(request):
    if request.method == 'POST':
        book_id = request.POST.get('book_id')
        user_id = request.POST.get('user_id')
        rating = request.POST.get('rating')
        comment = request.POST.get('comment')

        book = Book.objects.get(id=book_id)
        user = User.objects.get(id=user_id)

        review = Review.objects.create(book=book, user=user, rating=rating, comment=comment)
        return JsonResponse({'status': 'success', 'review_id': review.id})
