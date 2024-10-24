import requests
from django.core.management.base import BaseCommand
from app.models import Book, Author, Genre
from datetime import datetime

class Command(BaseCommand):
    help = 'Fetch books from Google Books API based on genre and store them in the database'

    def fetch_books_by_genre(self, genre_name):
        api_url = f'https://www.googleapis.com/books/v1/volumes?q=subject:{genre_name}'
        response = requests.get(api_url)
        books_data = response.json()

        if response.status_code == 200 and 'items' in books_data:
            for item in books_data['items']:
                book_info = item['volumeInfo']
                
                # Lấy hoặc tạo tác giả
                author_name = book_info.get('authors', ['Unknown Author'])[0]
                author, _ = Author.objects.get_or_create(name=author_name)
                
                # Lấy hoặc tạo thể loại
                genre, _ = Genre.objects.get_or_create(name=genre_name)

                # Xử lý ngày xuất bản
                published_date = book_info.get('publishedDate', None)
                if published_date:
                    # Nếu chỉ có năm, thêm -01-01
                    if len(published_date) == 4:
                        published_date = f'{published_date}-01-01'
                    try:
                        # Kiểm tra định dạng ngày hợp lệ
                        published_date = datetime.strptime(published_date, '%Y-%m-%d').date()
                    except ValueError:
                        published_date = None

                # Tạo và lưu sách vào cơ sở dữ liệu
                Book.objects.create(
                    title=book_info.get('title', 'No Title'),
                    author=author,
                    genre=genre,
                    description=book_info.get('description', 'No Description'),
                    published_date=published_date,
                    thumbnail=book_info['imageLinks']['thumbnail'] if 'imageLinks' in book_info else None
                )
                print(f"Book '{book_info.get('title', 'No Title')}' added under genre '{genre_name}'")
        else:
            print(f"Failed to fetch data for genre: {genre_name}")

    def handle(self, *args, **kwargs):
        genres = ['fiction', 'science', 'technology', 'history', 'fantasy']
        for genre in genres:
            print(f"Fetching books for genre: {genre}")
            self.fetch_books_by_genre(genre)
