from django.urls import path
from . import views

urlpatterns = [
    path('books/genre/<int:genre_id>/', views.get_books_by_genre, name='books_by_genre'),
    path('books/author/<int:author_id>/', views.get_books_by_author, name='books_by_author'),
    path('books/preference/<int:user_id>/', views.get_books_by_user_preference, name='books_by_preference'),
    path('reviews/book/<int:book_id>/', views.get_book_reviews, name='book_reviews'),
    path('reviews/add/', views.add_review, name='add_review'),
]
