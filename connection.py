import psycopg2
from psycopg2 import OperationalError


def get_connection():
    try:
        conn = psycopg2.connect(
            dbname="insurance_db",
            user="postgres",
            password="12345",   # твой пароль
            host="localhost",
            port="5432",
            options="-c client_encoding=UTF8"
        )
        return conn
    except OperationalError as e:
        print("Ошибка подключения к базе данных")
        print(e)
        return None