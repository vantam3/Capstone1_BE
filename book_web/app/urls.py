# app/urls.py

from django.urls import path
from . import views
from .views import BookSearchAPIView

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # API endpoints for books
    path('api/books/search/', BookSearchAPIView.as_view(), name='book-search'),
    path('api/books/', views.all_books, name='all_books'),
    path('api/books/<int:book_id>/', views.book_detail_view, name='book_detail_view'),

    path('api/books/<int:book_id>/content/', views.book_content_by_id, name='book_content_by_id'),
    path('api/books/author/<str:author_name>/', views.books_by_author, name='books_by_author'),

    # API endpoints for reviews
    path('api/books/<int:book_id>/add_review/', views.add_review, name='add_review'),
    path('api/books/<int:book_id>/reviews/', views.get_book_reviews, name='get_book_reviews'),
]


