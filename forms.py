from flask import Flask, request, render_template
import sys
import base64
import sqlite3
app = Flask(__name__, template_folder='templates')

database = 'here'
def main(databse_path = "D:\\test\\database.db"):
    print('!!!')
    
    global database
    database = databse_path
    print(database)
    app.run(debug=True)
def get_data_from_db(database, to_search, extension):
    db_name = database
    #  выполнять в оперативке
    #db_name = ':memory:'
    db = sqlite3.connect(db_name)
    cur = db.cursor()
    result = []
    if extension == 'any':
        query = cur.execute(f"SELECT id,title,author,year,ext,file_hash FROM books_txt WHERE title LIKE '%{to_search}%' OR author LIKE '%{to_search}%'")
        for line in query:
            s = list(line)
            result.append(s)
        query = cur.execute(f"SELECT id,title,author,year,ext,file_hash,cover FROM books_pdf WHERE title LIKE '%{to_search}%' OR author LIKE '%{to_search}%'")
        for line in query:
            s = list(line)
            base_64 = base64.b64encode((s[6]))
            base_64 = base_64.decode()
            s[6] = base_64
            result.append(s)
        query = cur.execute(f"SELECT id,title,author,year,ext,file_hash,cover FROM books_epub WHERE title LIKE '%{to_search}%' OR author LIKE '%{to_search}%'")
        for line in query:
            s = list(line)
            base_64 = base64.b64encode((s[6]))
            base_64 = base_64.decode()
            s[6] = base_64
            result.append(s)
        query = cur.execute(f"SELECT id,title,author,year,ext,file_hash,cover FROM books_fb2 WHERE title LIKE '%{to_search}%' OR author LIKE '%{to_search}%'")
        for line in query:
            s = list(line)
            base_64 = base64.b64encode((s[6]))
            base_64 = base_64.decode()
            s[6] = base_64
            result.append(s)
    else: 
        if extension == 'txt':query = cur.execute(f"SELECT id,title,author,year,ext,file_hash FROM books_{extension} WHERE title LIKE '%{to_search}%' OR author LIKE '%{to_search}%'")
        else: query = cur.execute(f"SELECT id,title,author,year,ext,file_hash,cover FROM books_{extension} WHERE title LIKE '%{to_search}%' OR author LIKE '%{to_search}%'")
        for line in query:
            s = list(line)
            if len(s)==7: 
                base_64 = base64.b64encode((s[6]))
                base_64 = base_64.decode()
                s[6] = base_64
            result.append(s)

    return result
def get_text_from_book(database,book,ext):
    db_name = database
    #  выполнять в оперативке
    #db_name = ':memory:'
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

@app.route('/submit', methods=['GET'])
def submit():
    show_text = request.args.get('show_text', '') 
    extension = request.args.get('ext', '')
    if (show_text):
        text = get_text_from_book(database, show_text,extension)
        return render_template('index.html', extension = database, texting = text,title = show_text)
    title = request.args.get('text', '')
    extension = request.args.get('ext', '')
    result_array = get_data_from_db(database, title, extension)
    # Render the template with the submitted form data
    return render_template('index.html', name=title, extension = database, my_list = result_array)

if __name__ == '__main__':
    #eneble during prod
    database_path = sys.argv[1]
    #database = ""
    main()
    #app.run(debug=True)


    