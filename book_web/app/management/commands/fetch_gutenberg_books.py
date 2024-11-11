# myapp/management/commands/fetch_gutenberg_books.py

import requests
import random
import os
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
        url = f"https://gutendex.com/books?languages=en&page={random_page}&size={size}"        
        response = requests.get(url)
        
        if response.status_code != 200:
            self.stdout.write(self.style.ERROR("Failed to fetch data from API"))
            return
        
        data = response.json()
        download_links = []
        
        for book_data in data['results']:
            title = book_data['title']
            author = book_data['authors'][0]['name'] if book_data['authors'] else 'Unknown'
            formats = book_data.get('formats', {})
            
            # Bao gồm mọi link hợp lệ
            download_link = (
                formats.get('text/html') or
                formats.get('text/plain; charset=utf-8') or
                formats.get('text/plain') or
                formats.get('text/html.images')
            )
            
            # Kiểm tra nếu có link download hợp lệ
            if download_link:
                download_links.append(download_link)
                
            # Dùng `update_or_create` để lưu vào MySQL
            Book.objects.update_or_create(
                gutenberg_id=book_data['id'],
                defaults={
                    'title': title,
                    'author': author,
                    'download_link': download_link,
                }
            )
        # Ghi các link vào file dataAI.txt trong thư mục app/data
        with open("app/data/dataAI.txt", "a", encoding="utf-8") as file:
            for link in download_links:
                file.write(link + "\n")

        self.stdout.write(self.style.SUCCESS(f'Successfully fetched {size} books from random page {random_page} without duplicates'))
