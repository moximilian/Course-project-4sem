import os
from version1_0 import Book
from collections import Counter
import sqlite3
from colorama import Style, Back, Fore
import warnings
import argparse




def process_book(path, database_path):
    """Process single book and save its information to SQLite database"""
    book = Book(path)
    try:
        book.extract_metadata()
        book.extract_content()
        book.calculate_hash()
        book.extract_cover()
        book.save_to_database(database_path)
        preview_path = os.path.splitext(path)[0] + '.jpg'
        book.generate_preview(preview_path)
    except Exception as e:
        print(f'Error processing file {path}: {e}')


def process_folder(folder_path, database_path):
    """Process all books in the given folder and its subfolders"""

    for root, dirs, files in os.walk(folder_path):
        for file in files:
            _, ext = os.path.splitext(file)
            if ext.lower() not in ['.pdf', '.epub', '.txt','.fb2']:
                continue
            path = os.path.join(root, file)
            process_book(path, database_path)
        
def check_repeated_path(books, item):
    indexes = []
    for i,n in enumerate(books):
        if books[i][0] == item:
            indexes.append(i)
    if len(indexes)>1:
        return indexes

def check_repeated_books(folder_path):
    """Process all books in the given folder and its subfolders"""
    books = []
    repeated_dirs = []
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            path = os.path.join(root, file)
            book = Book(path)
            book_title = book.extract_metadata()
            books.append([book_title,root])
    printed = [None,]
    
    for book in books:
        direction = []
        repeated_books = check_repeated_path(books,book[0])
        if repeated_books and book[0] not in printed:
            
            for rp in repeated_books:
                direction.append(books[rp][1])
            print(Back.BLACK + Fore.MAGENTA +f'Книга "{book[0]}" повторяется в { "|".join(direction) }')
            printed.append(book[0])
                





def main():

    warnings.filterwarnings("ignore")

    parser = argparse.ArgumentParser(description='Process books and save their information to SQLite database')
    parser.add_argument('folder_path', metavar='FOLDER_PATH', help='Path to folder with the books')
    parser.add_argument('database_path', metavar='DATABASE_PATH', help='Path to SQLite database file')
    args = None
    try:
        args,unknown = parser.parse_known_args()
    except argparse.ArgumentError as e:
        print(f'Argument error: {e}')
        return

    process_folder(args.folder_path, args.database_path)
    check_repeated_books(args.folder_path)

if __name__ == '__main__':
    main()