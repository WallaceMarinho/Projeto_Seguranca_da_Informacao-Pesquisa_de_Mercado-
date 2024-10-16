import pymysql
from so_create_db import connect, create_tables
import time

tunnel, mydb = connect()

def check_connection(mydb):
    try:
        with mydb.cursor() as cursor:
            cursor.execute("SELECT 1")
        return True
    except pymysql.MySQLError as e:
        print(f"Conexão perdida com o banco de dados: {e}")
        return False

def check_database_exists(mydb, database_name='surveydb'):
    try:
        with mydb.cursor() as cursor:
            cursor.execute(f"SHOW DATABASES LIKE '{database_name}';")
            result = cursor.fetchone()
            return bool(result)
    except pymysql.MySQLError as e:
        print(f"Erro ao verificar existência do banco de dados: {e}")
        return False

def keep_connection_alive():
    global mydb, tunnel
    while True:
        if not check_connection(mydb):
            print("Tentando reconectar ao banco de dados...")
            tunnel.stop()
            tunnel.start()

            tunnel, mydb = connect()

            if mydb:
                print("Conexão reestabelecida com sucesso.")

                if not check_database_exists(mydb):
                    print("Banco de dados não encontrado, criando o banco e tabelas...")
                    create_tables(mydb)

            else:
                print("Falha ao reconectar ao banco de dados.")

        time.sleep(60)
