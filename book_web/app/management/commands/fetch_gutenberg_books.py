# myapp/management/commands/fetch_gutenberg_books.py

import requests
import random
from django.core.management.base import BaseCommand
from app.models import Book

class Command(BaseCommand):
    help = 'Fetch random books data from Project Gutenberg and save to MySQL without duplicates'

    def add_arguments(self, parser):
        parser.add_argument('--size', type=int, default=20, help='Number of books to fetch (default: 20)')
        parser.add_argument('--max_page', type=int, default=100, help='Max number of pages to select randomly')

    def handle(self, *args, **options):
        size = options['size']
        max_page = options['max_page']
        
        # Chọn một trang ngẫu nhiên
        random_page = random.randint(1, max_page)
        url = f"https://gutendex.com/books?page={random_page}&size={size}"
        
        response = requests.get(url)
        data = response.json()

        for book_data in data['results']:
            title = book_data['title']
            author = book_data['authors'][0]['name'] if book_data['authors'] else 'Unknown'
            download_link = book_data['formats'].get('text/plain; charset=utf-8') or book_data['formats'].get('text/html')
            # Dùng `update_or_create` để tránh trùng lặp
            Book.objects.update_or_create(
                gutenberg_id=book_data['id'],
                defaults={
                    'title': title,
                    'author': author,
                    'download_link': download_link,
                }
            )

        self.stdout.write(self.style.SUCCESS(f'Successfully fetched {size} books from random page {random_page} without duplicates'))
