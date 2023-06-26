from flask import Flask, request, render_template,send_file
import base64
import sqlite3
import sys
from datetime import datetime,timedelta
import math
app = Flask(__name__, template_folder='templates')
"""
Заполнение полей из GET запроса DONE (где необходимо)
Список авторов DONE
Фильтры по дате добавления DONE
10 книг на странице DONE
Фильтр по годам DONE
Путь в базу данных DONE
---------------------------------------------------------
Размер файла при скачивании DONE
Темная тема DONE
Кнопка с настрйоками, количество книг на странице DONE
дата добавлания - интервал DONE
Избранное \ (теги) DONE
"""
database = 'here'
def main(databse_path = "D:\\test\\database2.db"):
    global database
    database = databse_path
    print(database)
    app.run(debug=True)
def get_data_from_db(database, to_search, extension,add_date:str = '3', max_year = 2023, selected_page = 1,books_page = 3,include_fav = ''):
    db_name = database
    db = sqlite3.connect(db_name)
    cur = db.cursor()
    
    today = datetime.date(datetime.now())
    add_date_int = int(add_date)
    new_today = today - timedelta(days = add_date_int)
    add_date = new_today
    whole_array = []
    query = cur.execute(f"SELECT author FROM books_txt")
    for line in query:
        s = list(line)
        whole_array.append(s)
    query = cur.execute(f"SELECT author FROM books_pdf ")
    for line in query:
        s = list(line)
        whole_array.append(s)
    query = cur.execute(f"SELECT author FROM books_epub ")
    for line in query:
        s = list(line)
        whole_array.append(s)
    query = cur.execute(f"SELECT author FROM books_fb2 ")
    for line in query:
        s = list(line)
        whole_array.append(s)
            
            
    result = []
    if extension == 'any':
        if add_date!='': 
            if include_fav!='':
                query = "SELECT id,path,title,author,year,ext,file_hash,size,fav FROM books_txt WHERE (title LIKE ? OR author LIKE ?) AND year <= ? AND date_add >= ? AND fav = ?"
                params = ('%' + to_search + '%', '%' + to_search + '%', max_year,add_date,include_fav)
                query = cur.execute(query, params)
            else:
                query = "SELECT id,path,title,author,year,ext,file_hash,size,fav FROM books_txt WHERE (title LIKE ? OR author LIKE ?) AND year <= ? AND date_add >= ? "
                params = ('%' + to_search + '%', '%' + to_search + '%', max_year,add_date)
                query = cur.execute(query, params)
        else: 
            query = "SELECT id,path,title,author,year,ext,file_hash,size,fav FROM books_txt WHERE (title LIKE ? OR author LIKE ?) AND year <= ?"
            params = ('%' + to_search + '%', '%' + to_search + '%', max_year)
            query = cur.execute(query, params)
        for line in query:
            s = list(line)
            result.append(s)
            
            
        if add_date!='': 
            if include_fav!='':
                query = "SELECT id,path,title,author,year,ext,file_hash,cover,size,fav FROM books_pdf WHERE (title LIKE ? OR author LIKE ?) AND year <= ? AND date_add >= ? AND fav = ?"
                params = ('%' + to_search + '%', '%' + to_search + '%', max_year,add_date,include_fav)
                query = cur.execute(query, params)
            else:
                query = "SELECT id,path,title,author,year,ext,file_hash,cover,size,fav FROM books_pdf WHERE (title LIKE ? OR author LIKE ?) AND year <= ? AND date_add >= ?"
                params = ('%' + to_search + '%', '%' + to_search + '%', max_year,add_date)
                query = cur.execute(query, params)
        else: 
            query = "SELECT id,path,title,author,year,ext,file_hash,cover,size,fav FROM books_pdf WHERE (title LIKE ? OR author LIKE ?) AND year <= ?"
            params = ('%' + to_search + '%', '%' + to_search + '%', max_year)
            query = cur.execute(query, params)
            
        for line in query:
            s = list(line)
            base_64 = base64.b64encode((s[7]))
            base_64 = base_64.decode()
            s[7] = base_64
            result.append(s)
        if add_date!='': 
            if include_fav!='':
                query = "SELECT id,path,title,author,year,ext,file_hash,cover,size,fav FROM books_epub WHERE (title LIKE ? OR author LIKE ?) AND year <= ? AND date_add >= ? AND fav=?"
                params = ('%' + to_search + '%', '%' + to_search + '%', max_year,add_date,include_fav)
                query = cur.execute(query, params)
            else:
                query = "SELECT id,path,title,author,year,ext,file_hash,cover,size,fav FROM books_epub WHERE (title LIKE ? OR author LIKE ?) AND year <= ? AND date_add >= ?"
                params = ('%' + to_search + '%', '%' + to_search + '%', max_year,add_date)
                query = cur.execute(query, params)
        else: 
            query = "SELECT id,path,title,author,year,ext,file_hash,cover,size,fav FROM books_epub WHERE (title LIKE ? OR author LIKE ?) AND year <= ?"
            params = ('%' + to_search + '%', '%' + to_search + '%', max_year)
            query = cur.execute(query, params)     
        for line in query:
            s = list(line)
            base_64 = base64.b64encode((s[7]))
            base_64 = base_64.decode()
            s[7] = base_64
            result.append(s)
            
        if add_date!='': 
            if include_fav!='':
                query = "SELECT id,path,title,author,year,ext,file_hash,cover,size,fav FROM books_fb2 WHERE (title LIKE ? OR author LIKE ?) AND year <= ? AND date_add >= ? AND fav = ?"
                params = ('%' + to_search + '%', '%' + to_search + '%', max_year, add_date,include_fav)
                query = cur.execute(query, params)
            else:
                query = "SELECT id,path,title,author,year,ext,file_hash,cover,size,fav FROM books_fb2 WHERE (title LIKE ? OR author LIKE ?) AND year <= ? AND date_add >= ?"
                params = ('%' + to_search + '%', '%' + to_search + '%', max_year, add_date)
                query = cur.execute(query, params)
        else: 
            query = "SELECT id,path,title,author,year,ext,file_hash,cover,size,fav FROM books_fb2 WHERE (title LIKE ? OR author LIKE ?) AND year <= ?"
            params = ('%' + to_search + '%', '%' + to_search + '%', max_year)
            query = cur.execute(query, params)
        for line in query:
            s = list(line)
            base_64 = base64.b64encode((s[7]))
            base_64 = base_64.decode()
            s[7] = base_64
            result.append(s)
    else: 
        if extension == 'txt':
            if add_date!='':
                if include_fav !='':
                    query = cur.execute(f"SELECT id,path,title,author,year,ext,file_hash,size,fav FROM books_{extension} WHERE (title LIKE '%{to_search}%' OR author LIKE '%{to_search}%') AND `year` <= {max_year} AND date_add >= '{add_date}' AND fav = '{include_fav}'")
                else: 
                    query = cur.execute(f"SELECT id,path,title,author,year,ext,file_hash,size,fav FROM books_{extension} WHERE (title LIKE '%{to_search}%' OR author LIKE '%{to_search}%') AND `year` <= {max_year} AND date_add >= '{add_date}'")
            else:
                if include_fav!='':
                    query = cur.execute(f"SELECT id,path,title,author,year,ext,file_hash,size,fav FROM books_{extension} WHERE (title LIKE '%{to_search}%' OR author LIKE '%{to_search}%') AND `year` <= {max_year}AND fav = '{include_fav}'")
                else: query = cur.execute(f"SELECT id,path,title,author,year,ext,file_hash,size,fav FROM books_{extension} WHERE (title LIKE '%{to_search}%' OR author LIKE '%{to_search}%') AND `year` <= {max_year}")
        else: 
            if add_date!='':
                if include_fav!='':
                    query = f"SELECT id,path,title,author,year,ext,file_hash,cover,size,fav FROM books_{extension} WHERE (title LIKE ? OR author LIKE ?) AND year <= ? AND date_add >= ? AND fav = ?"
                    params = ('%' + to_search + '%', '%' + to_search + '%', max_year, add_date,include_fav)
                    query = cur.execute(query, params)
                else: 
                    query = f"SELECT id,path,title,author,year,ext,file_hash,cover,size,fav FROM books_{extension} WHERE (title LIKE ? OR author LIKE ?) AND year <= ? AND date_add >= ?"
                    params = ('%' + to_search + '%', '%' + to_search + '%', max_year, add_date)
                    query = cur.execute(query, params)
            else:
                if include_fav!='': query = cur.execute(f"SELECT id,path,title,author,year,ext,file_hash,cover,size,fav FROM books_{extension} WHERE (title LIKE '%{to_search}%' OR author LIKE '%{to_search}%') AND `year` <= {max_year} AND fav = '{include_fav}'")
                else: query = cur.execute(f"SELECT id,path,title,author,year,ext,file_hash,cover,size,fav FROM books_{extension} WHERE (title LIKE '%{to_search}%' OR author LIKE '%{to_search}%') AND `year` <= {max_year} ")

        for line in query:
            s = list(line)
            if len(s)==8: 
                base_64 = base64.b64encode((s[7]))
                base_64 = base_64.decode()
                s[7] = base_64
            result.append(s)
            
    # print(type(books_page))
    count_of_books_on_page = books_page
    # print(count_of_books_on_page)
    # print(count_of_books_on_page)
    all_pages = math.ceil(len(result)/count_of_books_on_page)
    
    
    page_n = int(selected_page)
    count_of_missed_left = count_of_books_on_page*(page_n - 1)
    if page_n<all_pages:
        result = result[:count_of_books_on_page*page_n:1]
    result = result[count_of_missed_left:]
    return (result,all_pages,whole_array)
def get_text_from_book(database,book,ext):
    db_name = database
    print(book)
    db = sqlite3.connect(db_name)
    cur = db.cursor()
    extension =  ext[1:]
    query = cur.execute(f"SELECT content FROM books_{extension} WHERE title = '{book}' LIMIT 1 ")
    s = list(*query)
    s = s[0][:15000]
    s+='!Конец ознакомительного фрагмента!'
    return s
    
@app.route('/')
def index():
    return render_template('index.html')

def make_book_favourite(database,ext,book_id):
    
    db_name = database
    db = sqlite3.connect(db_name)
    cur = db.cursor()
    
    result = []
    query = cur.execute(f"SELECT fav FROM books_{ext} WHERE id = {book_id}")
    for line in query:
        s = list(line)
        result.append(s)
    # print(result[0][0])
    if result[0][0] == 'True':
        query = cur.execute(f"UPDATE books_{ext} SET fav = 'False' WHERE id = {book_id};")
    else:
        query = cur.execute(f"UPDATE books_{ext} SET fav = 'True' WHERE id = {book_id};")
    db.commit()
    cur.close()
    db.close()
   


    
@app.route('/download', methods=['GET'])
def download():
    file = request.args.get('book_path', '')
    file = file.replace('\\','/') 
    return send_file(file)

@app.route('/submit', methods=['GET'])
def submit():
    show_text = request.args.get('show_text', '') 
    select_page = request.args.get('page', '')
    title = request.args.get('text', '')
    extension = request.args.get('ext', '')
    max_year = request.args.get('year', '')
    add_date = request.args.get('add_date', '')
    books_page = request.args.get('books_page', type=int)
    
    id = request.args.get('id', '')
    include_fav = request.args.get('include_fav')
    # books_page = 3
    # if (books_page_str):books_page = int(books_page_str)
    if include_fav=='False':
        include_fav = ''
    if id:
        if '.' in extension:
            extension =  extension[1:]
        make_book_favourite(database,extension,id)
    if (show_text):
        text = get_text_from_book(database, show_text,extension)
        return render_template('index.html', extension = database, texting = text,title = show_text)
    if select_page:
        print(extension)
        extension='any'
        result_array,all_pages,whole_array = get_data_from_db(database, title, extension,add_date, max_year, select_page,books_page,include_fav)
        # pages_to_select = [x for x in range(1,all_pages+1)]
        # return render_template('index.html', name=title, extension = database, my_list = result_array,page_n=pages_to_select)
    else: 
        print(f"{title=},{extension=},{add_date=},{max_year=},{books_page=},{include_fav=}")
        result_array,all_pages,whole_array = get_data_from_db(database = database, to_search = title, extension = extension, add_date = add_date, max_year = max_year,books_page = books_page,include_fav = include_fav)
    
    author_list = [x[0] for x in whole_array]
    author_set = set(author_list)
    pages_to_select = [x for x in range(1,all_pages+1)]
    return render_template('index.html',page = select_page,include_fav = include_fav,add_date= add_date,books_page = books_page,year = max_year, name=title, extension = extension, my_list = result_array,page_n=pages_to_select,authors = author_set)

if __name__ == '__main__':
    #eneble during prod
    database_path = sys.argv[1]
    # main()
    # database_path = "D:\\test\\database8.db "
    #database = "D:\\test\\database2.db "
    main(database_path)
    #app.run(debug=True)


    