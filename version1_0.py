import base64
import os
import io
import sqlite3
import fnmatch
import hashlib
import subprocess
from PIL import Image
from io import BytesIO
import magic
import fitz
import ebooklib
from ebooklib import epub
from ebooklib import utils
import PyPDF2
from bs4 import BeautifulSoup
import textract
import ebookmeta
import pdf2image



class Book:
    def __init__(self, path):
        self.path = path
        self.title = ''
        self.author = ''
        self.year = ''
        self.pages = 0
        self.cover = None
        self.content = ''
        self.file_hash = ''

    def __repr__(self):
        return f'{self.title} by {self.author} ({self.year}, {self.pages} pages)'

    def extract_metadata(self):
        """Extract metadata from the book (title, author, year, pages)"""
        _, ext = os.path.splitext(self.path)
        if ext.lower() == '.pdf':
            pdf_book = open(self.path, 'rb')
            pdfReader = PyPDF2.PdfReader(pdf_book)
            totalPages1 = len(pdfReader.pages)
            
            with fitz.open(self.path) as pdf:
                metadata = pdf.metadata
                self.title = metadata['title'].strip() if 'title' in metadata else ''
                self.author = metadata['author'].strip() if 'author' in metadata else ''
                self.year = metadata['year'] if 'year' in metadata else ''
            self.pages = totalPages1
        elif ext.lower() == '.epub':
            book = epub.read_epub(self.path)
            metadata = book.get_metadata
            self.author = metadata('DC','creator')[0][0]
            self.title = metadata('DC','title')[0][0]
            self.year = metadata('DC','date')[0][0]
            self.pages = 'variable'
        elif ext.lower() == '.txt':
            with open(self.path, 'r') as txt:
                lines = txt.read().splitlines()
                self.author = lines[0]
                self.title = lines[1] 
                self.year = 'no info'
                self.pages = len(lines[2:])
        elif ext.lower() == '.fb2':
            with open(self.path, 'r') as fb2:
                soup = BeautifulSoup(fb2, 'xml')
                self.title = soup.title.text
                self.author = ' '.join([author.text for author in soup.find_all('author')])
                self.year = soup.date.text.split('-')[0] if soup.date else ''
                self.pages = len(soup.find_all('section'))
        else:
            raise Exception(f'Unknown extension: {ext}')
        
        return f"{self.title},{self.author},{self.year},{self.pages}"

    def extract_content(self):
        """Extract text content from the book"""
        _, ext = os.path.splitext(self.path)
        if ext.lower() == '.pdf':
            with fitz.open(self.path) as pdf:
                for page in pdf:
                    self.content += str(page)
                    '''.get_text()'''
        elif ext.lower() == '.epub':
            book = epub.read_epub(self.path)
            for doc in book.get_items():
                if doc.get_type() == ebooklib.ITEM_DOCUMENT:
                    soup = BeautifulSoup(doc.content, 'html.parser')
                    self.content += str(soup)
                    '''.get_text()'''
        elif ext.lower() == '.txt':
            with open(self.path, 'r') as txt:
                self.content = txt.read()
        elif ext.lower() == '.fb2':
            with open(self.path, 'r') as fb2:
                soup = BeautifulSoup(fb2, 'xml')
                sections = [section.text for section in soup.body.find_all('section')]
                self.content = '\n\n'.join(sections)
        else:
            raise Exception(f'Unknown extension: {ext}')

    def extract_cover(self):
        """Extract cover image from the book"""
        _, ext = os.path.splitext(self.path)
        if ext.lower() == '.pdf':
            doc = fitz.open(self.path)
            for img in doc:
                xref = img[0]
                pix = fitz.Pixmap(doc, xref)
                if pix.n < 5:       # this is GRAY or RGB
                    pix.writePNG("p%s-%s.png" % (0, xref))
                else:               # CMYK: convert to RGB first
                    pix1 = fitz.Pixmap(fitz.csRGB, pix)
                    pix1.writePNG("p%s-%s.png" % (0, xref))
                    pix1 = None
                pix = None
            self.cover = Image.fromarray(pix)
        elif ext.lower() == '.epub':
            book = epub.read_epub(self.path)
            for item in book.get_items():
                if item.get_type() == ebooklib.ITEM_IMAGE and 'cover' in item.get_name():
                    self.cover = Image.open(BytesIO(item.get_content()))
                    break
        elif ext.lower() == '.txt':
            pass
        elif ext.lower() == '.fb2':
            meta = ebookmeta.get_metadata(self.path)
            binary = meta.cover_image_data
            stream = io.BytesIO(binary)
            image = Image.open(stream)
            self.cover = image
        else:
            raise Exception(f'Unknown extension: {ext}')

    def calculate_hash(self):
        """Calculate SHA256 hash of the book file"""
        with open(self.path, 'rb') as file:
            content = file.read()
            self.file_hash = hashlib.sha256(content).hexdigest()

    def save_to_database(self, database_path):
        """Save book information to SQLite database"""
        conn = sqlite3.connect(database_path)
        cursor = conn.cursor()
        cursor.execute('CREATE TABLE IF NOT EXISTS books (id INTEGER PRIMARY KEY, title TEXT, author TEXT, year TEXT, pages INTEGER, cover BLOB, content TEXT, file_hash TEXT)')

        cursor.execute('SELECT id FROM books WHERE file_hash = ?', (self.file_hash,))
        result = cursor.fetchone()
        if result:
            print(f'Skipping already processed file: {self.path}')
            return result[0]

        if self.cover:
            with BytesIO() as cover_buffer:
                self.cover.save(cover_buffer, format='PNG')
                cover_data = cover_buffer.getvalue()
            cursor.execute('INSERT INTO books (title, author, year, pages, cover, content, file_hash) VALUES (?, ?, ?, ?, ?, ?, ?)', (self.title, self.author, self.year, self.pages, cover_data, self.content, self.file_hash))
        else:
            cursor.execute('INSERT INTO books (title, author, year, pages, content, file_hash) VALUES (?, ?, ?, ?, ?, ?)', (self.title, self.author, self.year, self.pages, self.content, self.file_hash))
        conn.commit()
        cursor.close()
        conn.close()
        print(f'Saved information for {self.path} to database')

    def generate_preview(self, preview_path):
        """Generate preview image (first page screenshot)"""
        _, ext = os.path.splitext(self.path)
        if ext.lower() == '.pdf':
            with fitz.open(self.path) as pdf:
                pix = pdf[0].get_pixmap()
                fmt = 'JPEG' if pix.colorspace == fitz.PIX_COLORSPACE_RGB else 'PNG'
                preview = Image.open(BytesIO(pix.get_buffer(fmt)))
        elif ext.lower() == '.epub':
            book = epub.read_epub(self.path)
            data = None
            for item in book.get_items():
                if item.get_type() == ebooklib.ITEM_IMAGE and 'cover' in item.get_name().lower():
                    data = item.get_content()
                    break
            if not data:
                return
            preview = Image.open(BytesIO(data))
        elif ext.lower() == '.txt':
            return
        else:
            raise Exception(f'Unknown extension: {ext}')

        preview.save(preview_path)
        print(f'Generated preview for {self.path}: {preview_path}')



