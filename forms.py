from flask import Flask, request, render_template,send_file
import base64
import sqlite3
import sys
from datetime import datetime
import math
app = Flask(__name__, template_folder='templates')
"""
Заполнение полей из GET запроса DONE (где необходимо)
Список авторов DONE
Фильтры по дате добавления
10 книг на странице DONE
Фильтр по годам DONE
Путь в базу данных DONE
"""
database = 'here'
def main(databse_path = "D:\\test\\database2.db"):
    print('!!!')
    global database
    database = databse_path
    print(database)
    app.run(debug=True)
def get_data_from_db(database, to_search, extension,add_date, max_year = 2023, selected_page = 1):
    db_name = database
    db = sqlite3.connect(db_name)
    cur = db.cursor()
    # if add_date!='':
    #     added_date = datetime.strptime(add_date, '%Y-%m-%d')
    #     print(added_date)
    
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
        query = cur.execute(f"SELECT id,path,title,author,year,ext,file_hash FROM books_txt WHERE title LIKE '%{to_search}%' OR author LIKE '%{to_search}%'")
        for line in query:
            s = list(line)
            result.append(s)
            
            
        if add_date!='': 
            query = "SELECT id,path,title,author,year,ext,file_hash,cover FROM books_pdf WHERE (title LIKE ? OR author LIKE ?) AND year <= ? AND date_add = ?"
            params = ('%' + to_search + '%', '%' + to_search + '%', max_year,add_date)
            query = cur.execute(query, params)
        else: 
            query = "SELECT id,path,title,author,year,ext,file_hash,cover FROM books_pdf WHERE (title LIKE ? OR author LIKE ?) AND year <= ?"
            params = ('%' + to_search + '%', '%' + to_search + '%', max_year)
            query = cur.execute(query, params)
            
        for line in query:
            s = list(line)
            base_64 = base64.b64encode((s[7]))
            base_64 = base_64.decode()
            s[7] = base_64
            result.append(s)
        if add_date!='': 
            query = "SELECT id,path,title,author,year,ext,file_hash,cover FROM books_epub WHERE (title LIKE ? OR author LIKE ?) AND year <= ? AND date_add = ?"
            params = ('%' + to_search + '%', '%' + to_search + '%', max_year,add_date)
            query = cur.execute(query, params)
        else: 
            query = "SELECT id,path,title,author,year,ext,file_hash,cover FROM books_epub WHERE (title LIKE ? OR author LIKE ?) AND year <= ?"
            params = ('%' + to_search + '%', '%' + to_search + '%', max_year)
            query = cur.execute(query, params)     
        for line in query:
            s = list(line)
            base_64 = base64.b64encode((s[7]))
            base_64 = base_64.decode()
            s[7] = base_64
            result.append(s)
            
        if add_date!='': 
            query = "SELECT id,path,title,author,year,ext,file_hash,cover FROM books_fb2 WHERE (title LIKE ? OR author LIKE ?) AND year <= ? AND date_add = ?"
            params = ('%' + to_search + '%', '%' + to_search + '%', max_year, add_date)
            query = cur.execute(query, params)
        else: 
            query = "SELECT id,path,title,author,year,ext,file_hash,cover FROM books_fb2 WHERE (title LIKE ? OR author LIKE ?) AND year <= ?"
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
            print('!')
            if add_date!='':
                print('!!',add_date)
                query = cur.execute(f"SELECT id,path,title,author,year,ext,file_hash FROM books_{extension} WHERE (title LIKE '%{to_search}%' OR author LIKE '%{to_search}%') AND `year` <= {max_year} AND date_add = '{add_date}'")
            else:
                query = cur.execute(f"SELECT id,path,title,author,year,ext,file_hash FROM books_{extension} WHERE (title LIKE '%{to_search}%' OR author LIKE '%{to_search}%') AND `year` <= {max_year}")
        else: 
            if add_date!='':
                query = f"SELECT id,path,title,author,year,ext,file_hash,cover FROM books_{extension} WHERE (title LIKE ? OR author LIKE ?) AND year <= ? AND date_add = ?"
                params = ('%' + to_search + '%', '%' + to_search + '%', max_year, add_date)
                query = cur.execute(query, params)
            else:query = cur.execute(f"SELECT id,path,title,author,year,ext,file_hash,cover FROM books_{extension} WHERE (title LIKE '%{to_search}%' OR author LIKE '%{to_search}%') AND `year` <= {max_year} ")

        for line in query:
            s = list(line)
            if len(s)==8: 
                base_64 = base64.b64encode((s[7]))
                base_64 = base_64.decode()
                s[7] = base_64
            result.append(s)
            
            
    count_of_books_on_page = 3
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
    
    if (show_text):
        text = get_text_from_book(database, show_text,extension)
        return render_template('index.html', extension = database, texting = text,title = show_text)
    if select_page:
        extension='any'
        result_array,all_pages,whole_array = get_data_from_db(database, title, extension,add_date, max_year, select_page)
        # pages_to_select = [x for x in range(1,all_pages+1)]
        # return render_template('index.html', name=title, extension = database, my_list = result_array,page_n=pages_to_select)
    else: result_array,all_pages,whole_array = get_data_from_db(database, title, extension,add_date, max_year)
    
    author_list = [x[0] for x in whole_array]
    author_set = set(author_list)
    pages_to_select = [x for x in range(1,all_pages+1)]
    return render_template('index.html',year = max_year, name=title, extension = database, my_list = result_array,page_n=pages_to_select,authors = author_set)

if __name__ == '__main__':
    #eneble during prod
    database_path = sys.argv[1]
    # main()
    # database_path = "D:\\test\\database3.db "
    #database = "D:\\test\\database2.db "
    main(database_path)
    #app.run(debug=True)


    