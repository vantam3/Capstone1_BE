from django.urls import path
from . import views

urlpatterns = [
    #view books
    path('books/', views.list_books, name='list_books'),
    path('books/genre/<int:genre_id>/', views.get_books_by_genre, name='books_by_genre'),
    path('books/author/<int:author_id>/', views.get_books_by_author, name='books_by_author'),
    path('books/preference/<int:user_id>/', views.get_books_by_user_preference, name='books_by_preference'),
    
    # path('books/<int:book_id>/reviews', views.get_book_reviews, name='book_reviews'),
    
    #show rating of books 
    path('books/<int:book_id>/reviews/', views.get_reviews_for_book, name='get_reviews_for_book'),
    
    #add comment,  add
    path('books/reviews/add/', views.add_review, name='add_review'),
]
