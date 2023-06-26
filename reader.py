import os
from version1_0 import Book_pdf,Book_epub,Book_fb2,Book_txt
from collections import Counter
import sqlite3
from colorama import Style, Back, Fore
import threading
import argparse




def process_book(path, database_path):
    """Обрабатывает одну книгу и сохранет информацию о ней в базу данных"""
    _, ext = os.path.splitext(path)
    match ext:
        case ".pdf":
            book = Book_pdf(path)
            try:
                book.extract_metadata()
                book.extract_content()
                book.calculate_hash()
                book.extract_cover()
                book.save_to_database(database_path)
                preview_path = os.path.splitext(path)[0] + '.jpg'
                book.generate_preview(preview_path)
            except Exception as e:
                print(f'Ошибка получения данных из файла: {path}: {e}')
        case ".epub":
            book = Book_epub(path)
            try:
                book.extract_metadata()
                book.extract_content()
                book.calculate_hash()
                book.extract_cover()
                book.save_to_database(database_path)
                preview_path = os.path.splitext(path)[0] + '.jpg'
                book.generate_preview(preview_path)
            except Exception as e:
                print(f'Ошибка получения данных из файла: {path}: {e}')
        case ".fb2":
            book = Book_fb2(path)
            try:
                book.extract_metadata()
                book.extract_content()
                book.calculate_hash()
                book.extract_cover()
                book.save_to_database(database_path)
                preview_path = os.path.splitext(path)[0] + '.jpg'
                book.generate_preview(preview_path)
            except Exception as e:
                print(f'Ошибка получения данных из файла: {path}: {e}')
        case ".txt":
            book = Book_txt(path)
            try:
                book.extract_metadata()
                book.extract_content()
                book.calculate_hash()
                book.save_to_database(database_path)
            except Exception as e:
                print(f'Ошибка получения данных из файла: {path}: {e}')


def process_folder(folder_path, database_path = './database_temp.db'):
    """Обрабатывает целую папку с книгами"""
    folder_path = str(folder_path)
    # print(folder_path,database_path)
    import os
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

def count_books(directions:list)->str:
    """Подсчитыает количество книг повторяющихся в директориях

    Args:
        direction (list): массив строк с директориями, где повторяется книга

    Returns:
        str: стркоа, в которой указаны директории и количество раз сколько этот путь встречался
    """
    resulting = Counter(directions)
    result = 'повторяется в '
    count=0
    for k,v in resulting.items():
        count+=1
        if count>1: result += ', '
        result += k +" "+ str(v) + " раза"
    return result
    
def check_repeated_books(folder_path):
    """Проверяет повторяющиеся книги в разных папках"""
    books = []
    folder_path = folder_path.replace("\\", "/")
    repeated_dirs = []
    for root,dirs, files in os.walk(folder_path):
        for file in files:
            path = os.path.join(root, file)
            _, ext = os.path.splitext(path)
            book = None
            match ext:
                case '.pdf':
                    book = Book_pdf(path)
                    book_title = book.extract_metadata()
                    books.append([book_title,root])
                case '.txt':
                    book = Book_txt(path)
                    book_title = book.extract_metadata()
                    books.append([book_title,root])
                case '.epub':
                    book = Book_epub(path)
                    book_title = book.extract_metadata()
                    books.append([book_title,root])
                case '.fb2':
                    book = Book_fb2(path)
                    book_title = book.extract_metadata()
                    books.append([book_title,root])
                case _:
                    continue
            
    printed = [None,]
    
    for book in books:
        direction = []
        repeated_books = check_repeated_path(books,book[0])
        if repeated_books and book[0] not in printed:
            for rp in repeated_books:
                direction.append(books[rp][1])
                #если пути одинаковые, то пишу количество раз они повторяются в этой папке, иначе указываю пути
            result = count_books(direction)
            print(Back.BLACK + Fore.MAGENTA +f"Книга '{book[0]}' {result}")
            printed.append(book[0])
                
def start_web_server(database_path = './database_temp.db'):
    import forms
    try:
        forms.main(database_path)
    except Exception as e:
        print(F"Working database — {database_path}")
    

def start_all():
    folder_path = ''
    for root,dirs,files in os.walk('.'):
        for file in files:
            if 'git' in root:continue
            if 'node' in root:continue
            ext = file.split('.')[1] 
            if  len(file.split('.')) != 3 and  ext in ['epub','pdf','txt','fb2'] and 'my_books' not in root:
                folder_path = root
                break
        if folder_path == root:
            break
        
    t1 = threading.Thread(target = check_repeated_books, args=(folder_path,))
    t2 = threading.Thread(target = process_folder, args=(folder_path,))

    t1.start()
    t2.start()
    
    
    t3 = threading.Thread(target = start_web_server)
    t3.start()

    t1.join()
    t2.join()
    t3.join()
    


parser = argparse.ArgumentParser()
subparsers = parser.add_subparsers()

# Команда для автоматического старта всей программы
start_all_parser = subparsers.add_parser('start_all')
start_all_parser.add_argument('start', help='Напишите "Вперед! "')

# Команда для определения повторяющихся файлов
is_repeated_parser = subparsers.add_parser('check_repeated_books')
is_repeated_parser.add_argument('folger_path', help='Путь к папке с книгами')

# Команда для обработки папки в бд
process_all_parser = subparsers.add_parser('process_folder')
process_all_parser.add_argument('folger_path2', help='Путь к папке с книгами')
process_all_parser.add_argument('database_path', help='Путь к бд с книгами')


# Команда для запуска веб приложения
web_start_parser = subparsers.add_parser('start_web_server')
web_start_parser.add_argument('database_path2', help='Путь к бд с книгами')

if __name__ == '__main__':
    args = parser.parse_args()
    if hasattr(args, 'start'): 
        start_all()
    
    if hasattr(args, 'folger_path'): 
        check_repeated_books(args.folger_path)
    if hasattr(args, 'folger_path2') and hasattr(args, 'database_path'):
        process_folder(args.folger_path2,args.database_path)
    if hasattr(args, 'database_path2'): 
        start_web_server(args.database_path2)