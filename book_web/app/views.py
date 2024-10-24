from django.shortcuts import render
from django.http import JsonResponse
from .models import Book, Genre, Author, Review
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
import requests
from django.http import JsonResponse
import json
from django.shortcuts import get_object_or_404

def list_books(request):
    books = Book.objects.all()
    books_data = [
        {
            'title': book.title,
            'author': book.author.name,
            'genre': book.genre.name,
            'description': book.description,
            'published_date': book.published_date,
            'thumbnail': book.thumbnail
        } for book in books
    ]
    return JsonResponse(books_data, safe=False) 
    books = Book.objects.all()  # Truy vấn tất cả sách từ cơ sở dữ liệu
    book_list = list(books.values('id', 'title', 'author', 'genre', 'description'))  # Chuyển đổi QuerySet thành list dạng JSON
    return JsonResponse(book_list, safe=False)

def books_by_genre(request, genre_name):
    try:
        genre = Genre.objects.get(name=genre_name)
        books = Book.objects.filter(genre=genre)

        books_data = [
            {
                'title': book.title,
                'author': book.author.name,
                'description': book.description,
                'published_date': book.published_date,
                'thumbnail': book.thumbnail
            } for book in books
        ]
        return JsonResponse({'genre': genre_name, 'books': books_data}, safe=False)
    except Genre.DoesNotExist:
        return JsonResponse({'error': 'Genre not found'}, status=404)


def books_by_author(request, author_name):
    try:
        author = Author.objects.get(name=author_name)
        books = Book.objects.filter(author=author)

        books_data = [
            {
                'title': book.title,
                'genre': book.genre.name,
                'description': book.description,
                'published_date': book.published_date,
                'thumbnail': book.thumbnail
            } for book in books
        ]
        return JsonResponse({'author': author_name, 'books': books_data}, safe=False)
    except Author.DoesNotExist:
        return JsonResponse({'error': 'Author not found'}, status=404)

def book_reviews(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    reviews = Review.objects.filter(book=book)
    reviews_data = [{"user": review.user.username, "rating": review.rating, "comment": review.comment} for review in reviews]
    return JsonResponse(reviews_data, safe=False)




@csrf_exempt
def add_review(request,book_id):
    if request.method == 'POST':
        try:
            # Lấy dữ liệu từ request body
            data = json.loads(request.body)
            book_id = data.get('book_id')
            user_id = data.get('user_id')
            rating = data.get('rating')
            comment = data.get('comment')

            # Kiểm tra nếu cuốn sách và người dùng tồn tại
            book = Book.objects.get(id=book_id)
            user = User.objects.get(id=user_id)

            # Tạo một đối tượng Review và lưu vào cơ sở dữ liệu
            review = Review.objects.create(
                book=book,
                user=user,
                rating=rating,
                comment=comment
            )

            return JsonResponse({'status': 'success', 'review_id': review.id})
        except Book.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Book not found'}, status=404)
        except User.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'User not found'}, status=404)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)



def import_books_from_api(request, genre_name):
    # Tạo URL để gọi API Google Books
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

            # Lưu sách vào cơ sở dữ liệu
            book, created = Book.objects.get_or_create(
                title=book_info.get('title', 'No Title'),
                author=author,
                genre=genre,
                description=book_info.get('description', 'No Description'),
                published_date=book_info.get('publishedDate', None),
                thumbnail=book_info['imageLinks']['thumbnail'] if 'imageLinks' in book_info else None
            )
            if created:
                print(f"Book '{book.title}' added under genre '{genre_name}'")
            else:
                print(f"Book '{book.title}' already exists in database.")

        return JsonResponse({'message': f"Books from genre '{genre_name}' successfully imported."})
    else:
        return JsonResponse({'error': f"Failed to fetch data for genre: {genre_name}"}, status=400)
# API lấy sách theo thể loại
def books_by_genre_view(request, genre_name):
    try:
        genre = Genre.objects.get(name=genre_name)
        books = Book.objects.filter(genre=genre)

        books_data = []
        for book in books:
            books_data.append({
                'title': book.title,
                'author': book.author.name,
                'genre': book.genre.name,
                'description': book.description,
                'published_date': book.published_date,
                'thumbnail': book.thumbnail
            })

        return JsonResponse({'genre': genre_name, 'books': books_data}, safe=False)
    except Genre.DoesNotExist:
        return JsonResponse({'error': 'Genre not found'}, status=404)
    # Gọi hàm fetch để lấy dữ liệu từ Google Books API
    fetch_books_by_genre(genre_name)

    # Lấy danh sách sách theo thể loại từ cơ sở dữ liệu
    genre = Genre.objects.get(name=genre_name)
    books = Book.objects.filter(genre=genre)

    # Trả về JSON response
    books_data = []
    for book in books:
        books_data.append({
            'title': book.title,
            'author': book.author.name,
            'genre': book.genre.name,
            'description': book.description,
            'published_date': book.published_date,
            'thumbnail': book.thumbnail
        })

    return JsonResponse({'genre': genre_name, 'books': books_data})

    # Gọi hàm kéo dữ liệu từ Google Books API và lưu vào database
    fetch_books_by_genre(genre_name)

    # Lấy danh sách sách theo thể loại
    genre = Genre.objects.get(name=genre_name)
    books = Book.objects.filter(genre=genre)

    return render(request, 'books_by_genre.html', {'genre': genre, 'books': books})

