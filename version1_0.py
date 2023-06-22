import base64
import chardet
import os
import io
import sqlite3
import hashlib
from PIL import Image
from io import BytesIO
import fitz
import ebooklib
from ebooklib import epub,utils
import PyPDF2
from bs4 import BeautifulSoup
import ebookmeta
from colorama import Style, Back, Fore
from datetime import datetime

class Book_epub:
    def __init__(self, path):
        self.path = path
        self.title = ''
        self.author = ''
        self.year = ''
        self.ext = ''
        self.cover = None
        self.content = ''
        self.file_hash = ''

    def __repr__(self):
        return f'{self.title} by {self.author} ({self.year})'

    def extract_metadata(self):
        """Достать метаданные о книге (title, author, year)"""
        _, ext = os.path.splitext(self.path)
        self.ext = ext
        if ext.lower() == '.epub':
            book = epub.read_epub(self.path)
            metadata = book.get_metadata
            self.author = metadata('DC','creator')[0][0]
            self.title = metadata('DC','title')[0][0]
            self.year = metadata('DC','date')[0][0]
        return self.title
    
    
    def extract_content(self):
        """Достать текст книги"""
        book = epub.read_epub(self.path)
        items = list(book.get_items_of_type(ebooklib.ITEM_DOCUMENT))
        for c in items:
            soup = BeautifulSoup(c.get_body_content(), 'html.parser')
            text = [para.get_text() for para in soup.find_all('p')]
            d = ' '.join(text)
            self.content+= d


    def extract_cover(self):
        """Достать обложку книги"""
        book = epub.read_epub(self.path)
        for item in book.get_items():
            if item.get_type() == ebooklib.ITEM_IMAGE and 'cover' in item.get_name():
                self.cover = Image.open(BytesIO(item.get_content()))
                break
        
    def calculate_hash(self):
        """Калькулятор SHA256 хэша книги"""
        with open(self.path, 'rb') as file:
            content = file.read()
            self.file_hash = hashlib.sha256(content).hexdigest()
            
    def save_to_database(self, database_path):
        """Сохранeние книги в базу данных"""
        conn = sqlite3.connect(database_path)
        cursor = conn.cursor()
        #CREATE TABLE IF NOT EXISTS books (id INTEGER PRIMARY KEY,path TEXT, title TEXT, author TEXT, year TEXT, ext VARCHAR(4) , cover BLOB, content TEXT, file_hash TEXT,date_add DATETIME)
        cursor.execute('CREATE TABLE IF NOT EXISTS books_epub (id INTEGER PRIMARY KEY,path TEXT, title TEXT, author TEXT, year TEXT, ext VARCHAR(4) , cover BLOB, content TEXT, file_hash TEXT,date_add DATETIME)')

        cursor.execute('SELECT id,title FROM books_epub WHERE file_hash = ?', (self.file_hash,))
        result = cursor.fetchone()
        date_add = datetime.date(datetime.now())
        if result:
            """Обновление данных в Базе данных"""
            if self.cover:
                with BytesIO() as cover_buffer:
                    self.cover.save(cover_buffer, format='PNG')
                    cover_data = cover_buffer.getvalue()
                cursor.execute('UPDATE books_epub SET path=?, title = ?, author = ?, year = ?, ext = ?,  cover = ?, content = ? WHERE id = ?',(self.path, self.title, self.author, self.year, self.ext,  cover_data, self.content, result[0]))
            else:
                cursor.execute('UPDATE books_epub SET path=?, title = ?, author = ?, year = ?, ext = ?,  content = ? WHERE id = ?',(self.path, self.title, self.author, self.year, self.ext,  self.content, result[0]))

            print(Fore.CYAN +f'Произошло обновление книги "{result[1]}"')
            conn.commit()
            cursor.close()
            conn.close()
            return
        elif self.cover:
            with BytesIO() as cover_buffer:
                self.cover.save(cover_buffer, format='PNG')
                cover_data = cover_buffer.getvalue()
            #INSERT INTO books_epub (path, title, author, year, ext, content, file_hash,date_add) VALUES ('D:/', 'Книга', 'Автор', '2023', 'epub',  'Текст книги', '12345678','2023-06-22')
            cursor.execute('INSERT INTO books_epub (path, title, author, year, ext,  cover, content, file_hash,date_add) VALUES (?, ?, ?, ?, ?, ?, ?, ?,?)', (self.path, self.title, self.author, self.year, self.ext,  cover_data, self.content, self.file_hash,date_add))
        else:
            cursor.execute('INSERT INTO books_epub (path, title, author, year, ext, content, file_hash,date_add) VALUES (?, ?, ?, ?, ?,  ?, ?,?)', (self.path, self.title, self.author, self.year, self.ext,  self.content, self.file_hash,date_add))
        conn.commit()
        cursor.close()
        conn.close()
        print(Fore.YELLOW +f'Книга, путь которой {self.path} сохранена в базу данных books_epub')

    def generate_preview(self, preview_path):
        """Generate preview image (first page screenshot)"""

        book = epub.read_epub(self.path)
        data = None
        for item in book.get_items():
            if item.get_type() == ebooklib.ITEM_IMAGE and 'cover' in item.get_name().lower():
                data = item.get_content()
                break
        if not data:
            return
        preview = Image.open(BytesIO(data))
        preview.save(preview_path)
        print(Fore.YELLOW + f'Для книги {self.path} создано превью тут: {preview_path}')

class Book_pdf:
    def __init__(self, path):
        self.path = path
        self.title = ''
        self.author = ''
        self.year = ''
        self.ext = ''
        self.pages = 0
        self.cover = None
        self.content = ''
        self.file_hash = ''

    def __repr__(self):
        return f'{self.title} by {self.author} ({self.year}, {self.pages} pages)'

    def extract_metadata(self):
        """Достать метаданные о книге (title, author, year, pages)"""
        _, ext = os.path.splitext(self.path)
        self.ext = ext
        pdf_book = open(self.path, 'rb')
        pdfReader = PyPDF2.PdfReader(pdf_book)
        totalPages1 = len(pdfReader.pages)
            
        with fitz.open(self.path) as pdf:
            metadata = pdf.metadata
            self.title = metadata['title'].strip() if 'title' in metadata else ''
            self.author = metadata['author'].strip() if 'author' in metadata else ''
            self.year = metadata['year'] if 'year' in metadata else ''
        self.pages = totalPages1

        return self.title
    
    def extract_content(self):
        """Достать текст книги"""
        with fitz.open(self.path) as pdf:
            for page_n in range(1,self.pages):
                self.content +=pdf.get_page_text(page_n)

    def extract_cover(self):
        """Достать обложку книги"""
        doc = fitz.open(self.path)
        page = doc.load_page(0)
        for image_index, img in enumerate(page.get_images()):
            xref = img[0]
            base_image = doc.extract_image(xref)
            image_bytes = base_image["image"]
            self.cover = Image.open(io.BytesIO(image_bytes))
            break
        

    def calculate_hash(self):
        """Калькулятор SHA256 хэша книги"""
        with open(self.path, 'rb') as file:
            content = file.read()
            self.file_hash = hashlib.sha256(content).hexdigest()
            
    def save_to_database(self, database_path):
        """Сохранeние книги в базу данных"""
        conn = sqlite3.connect(database_path)
        cursor = conn.cursor()
        cursor.execute('CREATE TABLE IF NOT EXISTS books_pdf (id INTEGER PRIMARY KEY,path TEXT, title TEXT, author TEXT, year TEXT, ext VARCHAR(4) , pages INTEGER, cover BLOB, content TEXT, file_hash TEXT, date_add DATETIME)')

        cursor.execute('SELECT id,title FROM books_pdf WHERE file_hash = ?', (self.file_hash,))
        result = cursor.fetchone()
        date_add = datetime.date(datetime.now())
        if result:
            """Обновление данных в Базе данных"""
            if self.cover:
                with BytesIO() as cover_buffer:
                    self.cover.save(cover_buffer, format='PNG')
                    cover_data = cover_buffer.getvalue()
                cursor.execute('UPDATE books_pdf SET path=?, title = ?, author = ?, year = ?, ext = ?, pages = ?, cover = ?, content = ? WHERE id = ?',(self.path, self.title, self.author, self.year, self.ext, self.pages, cover_data, self.content, result[0]))
            else:
                cursor.execute('UPDATE books_pdf SET path=?, title = ?, author = ?, year = ?, ext = ?, pages = ?, content = ? WHERE id = ?',(self.path, self.title, self.author, self.year, self.ext, self.pages, self.content, result[0]))

            print(Fore.CYAN +f'Произошло обновление книги "{result[1]}"')
            conn.commit()
            cursor.close()
            conn.close()
            return
        elif self.cover:
            with BytesIO() as cover_buffer:
                self.cover.save(cover_buffer, format='PNG')
                cover_data = cover_buffer.getvalue()
            cursor.execute('INSERT INTO books_pdf (path, title, author, year, ext, pages, cover, content, file_hash,date_add) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?,?)', (self.path, self.title, self.author, self.year, self.ext, self.pages, cover_data, self.content, self.file_hash,date_add))
        else:
            cursor.execute('INSERT INTO books_pdf (path, title, author, year, ext, pages, content, file_hash,date_add) VALUES (?, ?, ?, ?, ?, ?, ?, ?,?)', (self.path, self.title, self.author, self.year, self.ext, self.pages, self.content, self.file_hash,date_add))
        conn.commit()
        cursor.close()
        conn.close()
        print(Fore.YELLOW +f'Книга, путь которой {self.path} сохранена в базу данных books_pdf')

    def generate_preview(self, preview_path):
        """Generate preview image (first page screenshot)"""
        preview = self.cover
        preview.save(preview_path)
        print(Fore.YELLOW + f'Для книги {self.path} создано превью тут: {preview_path}')

class Book_txt:
    def __init__(self, path):
        self.path = path
        self.title = ''
        self.author = ''
        self.year = ''
        self.ext = ''
        self.pages = 0
        self.content = ''
        self.file_hash = ''

    def __repr__(self):
        return f'{self.title} by {self.author} ({self.year}, {self.pages} pages)'

    def extract_metadata(self):
        """Достать метаданные о книге (title, author, year, pages)"""
        _, ext = os.path.splitext(self.path)
        self.ext = ext
        
        with open (self.path, 'rb') as f:
            block = f.read(5000)
        f.close()
        detect = chardet.detect(block)
        with open(self.path, 'r',encoding =detect['encoding'] ) as txt:
            lines = txt.read().splitlines()
            self.author = lines[0]
            self.title = lines[1] 
            self.year = 'no info'
            self.pages = len(lines[2:])
        return self.title
        
    def extract_content(self):
        """Достать текст книги"""
        with open (self.path, 'rb') as f:
            block = f.read(5000)
        f.close()
        detect = chardet.detect(block)
        with open(self.path, 'r',encoding =detect['encoding'] ) as txt:
            self.content = txt.read()
                

    def calculate_hash(self):
        """Калькулятор SHA256 хэша книги"""
        with open(self.path, 'rb') as file:
            content = file.read()
            self.file_hash = hashlib.sha256(content).hexdigest()
    
    def save_to_database(self, database_path):
        """Сохранeние книги в базу данных"""
        conn = sqlite3.connect(database_path)
        cursor = conn.cursor()
        cursor.execute('CREATE TABLE IF NOT EXISTS books_txt (id INTEGER PRIMARY KEY, path TEXT, title TEXT, author TEXT, year TEXT, ext VARCHAR(4) , pages INTEGER, content TEXT, file_hash TEXT,date_add DATETIME)')

        cursor.execute('SELECT id,path,title FROM books_txt WHERE file_hash = ?', (self.file_hash,))
        result = cursor.fetchone()
        date_add = datetime.date(datetime.now())
        if result:
            """Обновление данных в Базе данных"""
            cursor.execute('UPDATE books_txt SET path = ?, title = ?, author = ?, year = ?, ext = ?, pages = ?, content = ? WHERE id = ?',(self.path,self.title, self.author, self.year, self.ext, self.pages, self.content, result[0]))

            print(Fore.CYAN +f'Произошло обновление книги "{result[1]}"')
            conn.commit()
            cursor.close()
            conn.close()
            return
        else: cursor.execute('INSERT INTO books_txt (path,title, author, year, ext, pages, content, file_hash,date_add) VALUES (?,?, ?, ?, ?, ?, ?, ?, ?)', (self.path, self.title, self.author, self.year, self.ext, self.pages, self.content, self.file_hash,date_add))
        
        conn.commit()
        cursor.close()
        conn.close()
        print(Fore.YELLOW +f'Книга, путь которой {self.path} сохранена в базу данных books_txt')

class Book_fb2:
    def __init__(self, path):
        self.path = path
        self.title = ''
        self.author = ''
        self.year = ''
        self.ext = ''
        self.pages = 0
        self.cover = None
        self.content = ''
        self.file_hash = ''

    def __repr__(self):
        return f'{self.title} by {self.author} ({self.year}, {self.pages} pages)'

    def extract_metadata(self):
        """Достать метаданные о книге (title, author, year, pages) и вернуть название книги"""
        _, ext = os.path.splitext(self.path)
        self.ext = ext

        with open (self.path, 'rb') as f:
            block = f.read(5000)
        f.close()
        detect = chardet.detect(block)
        x = str(1234567890)
        with open(self.path, 'r',encoding=detect['encoding']) as fb2:
            soup = BeautifulSoup(fb2, 'xml')
            self.title = soup.find('book-title').string
            first_name = soup.find('first-name').string
            last_name = soup.find('last-name').string
            self.author = ' '.join([first_name,last_name])
            self.year = soup.date.text.split('-')[0] if soup.date else ''
            self.pages = len(soup.find_all('section'))

        return f'{self.title}'
    
    def extract_content(self):
        """Достать текст книги"""

        with open (self.path, 'rb') as f:
            block = f.read(5000)
        f.close()
        detect = chardet.detect(block)
        with open(self.path, 'r',encoding=detect['encoding']) as fb2:
            soup = BeautifulSoup(fb2, 'xml')
            sections = [section.text for section in soup.body.find_all('section')]
            self.content = '\n\n'.join(sections)


    def extract_cover(self):
        """Достать обложку книги"""
        meta = ebookmeta.get_metadata(self.path)
        binary = meta.cover_image_data
        stream = io.BytesIO(binary)
        image = Image.open(stream)
        self.cover = image

    def calculate_hash(self):
        """Калькулятор SHA256 хэша книги"""
        with open(self.path, 'rb') as file:
            content = file.read()
            self.file_hash = hashlib.sha256(content).hexdigest()
            
    def save_to_database(self, database_path):
        """Сохранeние книги в базу данных"""
        conn = sqlite3.connect(database_path)
        cursor = conn.cursor()
        cursor.execute('CREATE TABLE IF NOT EXISTS books_fb2 (id INTEGER PRIMARY KEY,path TEXT, title TEXT, author TEXT, year TEXT, ext VARCHAR(4) , pages INTEGER, cover BLOB, content TEXT, file_hash TEXT, date_add DATETIME)')

        cursor.execute('SELECT id,title FROM books_fb2 WHERE file_hash = ?', (self.file_hash,))
        result = cursor.fetchone()
        date_add = datetime.date(datetime.now())

        if result:
            """Обновление данных в Базе данных"""
            if self.cover:
                with BytesIO() as cover_buffer:
                    self.cover.save(cover_buffer, format='PNG')
                    cover_data = cover_buffer.getvalue()
                cursor.execute('UPDATE books_fb2 SET path=?, title = ?, author = ?, year = ?, ext = ?, pages = ?, cover = ?, content = ? WHERE id = ?',(self.path, self.title, self.author, self.year, self.ext, self.pages, cover_data, self.content, result[0]))
            else:
                cursor.execute('UPDATE books_fb2 SET path = ?, title = ?, author = ?, year = ?, ext = ?, pages = ?, content = ? WHERE id = ?',(self.path, self.title, self.author, self.year, self.ext, self.pages, self.content, result[0]))

            print(Fore.CYAN +f'Произошло обновление книги "{result[1]}"')
            conn.commit()
            cursor.close()
            conn.close()
            return
        elif self.cover:
            with BytesIO() as cover_buffer:
                self.cover.save(cover_buffer, format='PNG')
                cover_data = cover_buffer.getvalue()
            cursor.execute('INSERT INTO books_fb2 (path, title, author, year, ext, pages, cover, content, file_hash,date_add) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', (self.path, self.title, self.author, self.year, self.ext, self.pages, cover_data, self.content, self.file_hash,date_add))
        else:
            cursor.execute('INSERT INTO books_fb2 (path, title, author, year, ext, pages, content, file_hash,date_add) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)', (self.path, self.title, self.author, self.year, self.ext, self.pages, self.content, self.file_hash,date_add))
        conn.commit()
        cursor.close()
        conn.close()
        print(Fore.YELLOW +f'Книга, путь которой {self.path} сохранена в базу данных books_fb2')

    def generate_preview(self, preview_path):
        """Generate preview image (first page screenshot)"""

        meta = ebookmeta.get_metadata(self.path)
        binary = meta.cover_image_data
        stream = io.BytesIO(binary)
        image = Image.open(stream)
        preview = image

        preview.save(preview_path)
        print(Fore.YELLOW + f'Для книги {self.path} создано превью тут: {preview_path}')
