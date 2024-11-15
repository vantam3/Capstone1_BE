# app/urls.py
from .views import register_user, login_user
from django.urls import path
from . import views
from .views import BookSearchAPIView

urlpatterns = [
    path('', views.home, name='home'),
    #Đăng ký
    path('api/register/', register_user, name='register_user'),
    #Đăng nhập
    path('api/login/', login_user, name='login_user'),
    #Tìm sách
    path('api/books/search/', BookSearchAPIView.as_view(), name='book-search'), 
    #xem sach
    path('api/books/', views.all_books, name='all_books'),
    path('api/books/<int:book_id>/', views.book_detail_view, name='book_detail_view'),

    path('api/books/<int:book_id>/content/', views.book_content_by_id, name='book_content_by_id'),
    path('api/books/author/<str:author_name>/', views.books_by_author, name='books_by_author'),

    # API endpoints for reviews
    path('api/books/<int:book_id>/add_review/', views.add_review, name='add_review'),
    path('api/books/<int:book_id>/reviews/', views.get_book_reviews, name='get_book_reviews'),
]


