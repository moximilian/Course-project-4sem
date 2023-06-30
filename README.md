Курсовой проект по дисциплине "Объектно ориентированное программирование"  
_"Инструмент исследования книг"_  
Выполнил Сыров Максим Евгеньевич  
Группа 211-361  

**Перед запуском необходимо:**  
- `$ pip install -r requirements.txt`  
- **Скопировать папку с книгами в папку репозитория**   

**МЕТОДЫ:**  
 
Запустить всё:  
- `$ python reader.py start_all ANY_TEXT`
  - http://localhost:8080/

Проверить на повтор книги в папке:  
- `$ python reader.py check_repeated_books BOOKS_PATH`

Распарсить книги и добавить их в бд:  
- `$ python reader.py process_folder BOOKS_PATH DATABASE_PATH`

Запустить веб-приложение с фильтрами в браузере:  
- `$ python reader.py start_web_server DATABASE_PATH`
    - http://localhost:8080/

_Примечание_  
  Если путь к папке с книгами не указывается, то программа сама определит папку с книгами  
  Рекоммендуется использовать команду `start_all`  
Пример использования в test.ipynb ## Тестирование консоли  

