from django.urls import path
from . import views

urlpatterns = [
    # Xem tất cả sách
    path('books/', views.list_books, name='list_books'),
    
    # Xem sách theo tác giả
    path('books/author/<str:author_name>/', views.books_by_author, name='books_by_author'),

    # Xem sách theo thể loại
    path('books/genre/<str:genre_name>/', views.books_by_genre, name='books_by_genre'),

    # Xem đánh giá cho một cuốn sách
    path('books/<int:book_id>/reviews/', views.book_reviews, name='book_reviews'),

    # Thêm đánh giá cho sách
    path('books/<int:book_id>/reviews/add/', views.add_review, name='add_review'),
        
    #add book
    path('books/import/<str:genre_name>/', views.import_books_from_api, name='import_books_from_api'),

]
