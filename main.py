import psycopg2
import configparser

config = configparser.ConfigParser()
config.read('config.ini')


def connect_to_db():
    try:
        conn = psycopg2.connect(
            dbname=config['database']['DB_NAME'],
            user=config['database']['DB_USER'],
            password=config['database']['DB_PASSWORD'],
            host=config['database']['DB_HOST'],
            port=config['database']['DB_PORT']
        )
        # print("Успешно подключено к базе данных")
        return conn
    except Exception as e:
        print(f"Ошибка при подключении к базе данных: {e}")
        return None


def create_tables():
    conn = connect_to_db()
    if conn:
        with conn.cursor() as cursor:
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS clients (
                    id SERIAL PRIMARY KEY,
                    first_name VARCHAR(255),
                    last_name VARCHAR(255),
                    email VARCHAR(255)
                )
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS phones (
                    id SERIAL PRIMARY KEY,
                    client_id INTEGER REFERENCES clients(id),
                    phone_number VARCHAR(20)
                )
            ''')
            conn.commit()
            conn.close()


def add_client(first_name, last_name, email, phone=[]):
    conn = connect_to_db()
    if conn:
        with conn.cursor() as cursor:
            cursor.execute('''
                INSERT INTO clients (first_name, last_name, email)
                VALUES (%s, %s, %s)
                RETURNING id
            ''', (first_name, last_name, email))
            client_id = cursor.fetchone()[0]
            for number in phone:
                cursor.execute('''
                    INSERT INTO phones (client_id, phone_number)
                    VALUES (%s, %s)
                ''', (client_id, number))
            conn.commit()
            conn.close()


def add_phone(client_id, phone):
    conn = connect_to_db()
    if conn:
        with conn.cursor() as cursor:
            cursor.execute('''
                INSERT INTO phones (client_id, phone_number)
                VALUES (%s, %s)
            ''', (client_id, phone))
            conn.commit()
            conn.close()


def update_client(client_id, first_name, last_name, email):
    conn = connect_to_db()
    if conn:
        with conn.cursor() as cursor:
            cursor.execute('''
                UPDATE clients
                SET first_name = %s, last_name = %s, email = %s
                WHERE id = %s
            ''', (first_name, last_name, email, client_id))
            conn.commit()
            conn.close()


def delete_phone(client_id, phone):
    conn = connect_to_db()
    if conn:
        with conn.cursor() as cursor:
            cursor.execute('''
                DELETE FROM phones
                WHERE client_id = %s AND phone_number = %s
            ''', (client_id, phone))
            conn.commit()
            conn.close()


def delete_client(client_id):
    conn = connect_to_db()
    if conn:
        with conn.cursor() as cursor:
            cursor.execute('''
                DELETE FROM clients
                WHERE id = %s
            ''', (client_id,))
            conn.commit()
            conn.close()


def find_client(query):
    conn = connect_to_db()
    if conn:
        with conn.cursor() as cursor:
            cursor.execute('''
                SELECT clients.*, phones.phone_number
                FROM clients
                LEFT JOIN phones ON clients.id = phones.client_id
                WHERE first_name ILIKE %s 
                OR last_name ILIKE %s 
                OR email ILIKE %s 
                OR phone_number ILIKE %s
            ''', ('%' + query + '%', '%' + query + '%', '%' + query + '%', '%' + query + '%'))
            result = cursor.fetchall()
            conn.close()

            for row in result:
                if query.lower() in [str(field).lower() for field in row]:
                    print(
                        f"ID: {row[0]}\nFirst Name: {row[1]}\nLast Name: {row[2]}\nEmail: {row[3]}\nPhone Number: {row[4] if row[4] else 'N/A'}")
                    print("=" * 30)


create_tables()

add_client('Ivan', 'Ivanov', 'ivan.ivanov@example.com', ['88127736612'])
add_client('Sergey', 'Petrov', 'sergey.petrov@example.com', [])
add_client('Maria', 'Smirnova', 'maria.smirnova@example.com', ['8124992347'])

# Добавляем телефон для существующего клиента
add_phone(1, '75545489')

# Изменяем данные о клиенте
update_client(3, 'Sergey', 'Vasilyev', 'sergey.petrov@example.com')

# Удаляем телефон для существующего клиента
delete_phone(1, '88127736612')

# Удаляем существующего клиента
delete_client(2)

# Ищем клиентов
result = find_client('Maria')
print(result)
