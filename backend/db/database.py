import psycopg2

def get_connection():
    return psycopg2.connect(
        host="localhost",
        database="neurocore",
        user="neurocore_user",
        password="123456",
        port="5432"
    )