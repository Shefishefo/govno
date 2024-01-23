import sqlite3

def check_tables():
    # Подключение к базе данных SQLite (замените 'your_database.db' на фактическое имя вашего файла базы данных)
    conn = sqlite3.connect('black_list.db')
    cursor = conn.cursor()

    # Получение списка таблиц
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()

    # Вывод списка таблиц
    print("Список таблиц в базе данных:")
    for table in tables:
        print(table[0])

    # Закрытие соединения
    conn.close()

if __name__ == "__main__":
    check_tables()
