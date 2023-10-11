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
    with connect_to_db() as conn:
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


def add_client(first_name, last_name, email, phone=[]):
    with connect_to_db() as conn:
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


def add_phone(client_id, phone):
    with connect_to_db() as conn:
        if conn:
            with conn.cursor() as cursor:
                cursor.execute('''
                    INSERT INTO phones (client_id, phone_number)
                    VALUES (%s, %s)
                ''', (client_id, phone))


def update_client(client_id, first_name=None, last_name=None, email=None):
    with connect_to_db() as conn:
        if conn:
            with conn.cursor() as cursor:
                if first_name is None and last_name is None and email is None:
                    print("Не указаны данные для обновления.")
                    return

                query = 'UPDATE clients SET '
                values = []

                if first_name is not None:
                    query += 'first_name = %s, '
                    values.append(first_name)

                if last_name is not None:
                    query += 'last_name = %s, '
                    values.append(last_name)

                if email is not None:
                    query += 'email = %s, '
                    values.append(email)
                query = query[:-2]

                query += ' WHERE id = %s'
                values.append(client_id)

                cursor.execute(query, tuple(values))


def delete_phone(client_id, phone):
    with connect_to_db() as conn:
        if conn:
            with conn.cursor() as cursor:
                cursor.execute('''
                    DELETE FROM phones
                    WHERE client_id = %s AND phone_number = %s
                ''', (client_id, phone))


def delete_client(client_id):
    with connect_to_db() as conn:
        if conn:
            with conn.cursor() as cursor:
                cursor.execute('''
                    DELETE FROM clients
                    WHERE id = %s
                ''', (client_id,))


def find_client(first_name=None, last_name=None, email=None, phone=None):
    conn = connect_to_db()
    if conn:
        with conn.cursor() as cursor:
            query = '''
                SELECT clients.*, phones.phone_number
                FROM clients
                LEFT JOIN phones ON clients.id = phones.client_id
            '''

            conditions = []

            if first_name is not None:
                conditions.append('first_name ILIKE %s')
            if last_name is not None:
                conditions.append('last_name ILIKE %s')
            if email is not None:
                conditions.append('email ILIKE %s')
            if phone is not None:
                conditions.append('phone_number ILIKE %s')

            if conditions:
                query += ' WHERE ' + ' AND '.join(conditions)

            cursor.execute(query, tuple(['%' + param + '%' for param in [first_name, last_name, email, phone] if param is not None]))
            result = cursor.fetchall()
            conn.close()

            for row in result:
                print(
                    f"ID: {row[0]}\nFirst Name: {row[1]}\nLast Name: {row[2]}\nEmail: {row[3]}\nPhone Number: {row[4] if row[4] else 'N/A'}")
                print("=" * 30)



if __name__ == "__main__":
    create_tables()

    add_client('Ivan', 'Ivanov', 'ivan.ivanov@example.com', ['88127736612'])
    add_client('Sergey', 'Petrov', 'sergey.petrov@example.com', [])
    add_client('Maria', 'Smirnova', 'maria.smirnova@example.com', ['8124992347'])

    # Добавляем телефон для существующего клиента
    add_phone(1, '75545489')

    # Изменяем данные о клиенте
    update_client(3, 'Alesha')
    update_client(3, last_name='Petrov', email='sergey.petrov@example.com')

    # Удаляем телефон для существующего клиента
    delete_phone(1, '88127736612')

    # Удаляем существующего клиента
    delete_client(2)

    # Ищем клиентов
    #find_client()
    find_client('Alesha', 'Petrov')
    find_client('maria', email='maria.smirnova@example.com')