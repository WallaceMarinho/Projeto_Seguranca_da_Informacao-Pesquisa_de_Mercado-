from dotenv import load_dotenv
import os
import subprocess
import json
import mysql.connector

# Carrega as variáveis de ambiente
load_dotenv()


def restore_backup():
    db_host = os.getenv("DB_HOST_BACKUP")
    db_user = os.getenv("DB_USER")
    db_password = os.getenv("DB_PASSWORD")
    db_name = os.getenv("DB")
    backup_file = "backup.sql"
    excluded_users_file = "excluded_users.json"

    # Verifica se todas as variáveis de ambiente estão definidas
    if not all([db_host, db_user, db_password, db_name]):
        print("Erro: Verifique se todas as variáveis de ambiente (DB_HOST, DB_USER, DB_PASSWORD, DB) estão definidas.")
        return

    try:
        # Conecta ao MySQL para verificar/criar o banco
        connection = mysql.connector.connect(
            host=db_host,
            user=db_user,
            password=db_password
        )
        cursor = connection.cursor()

        # Cria o banco de dados se não existir
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
        connection.commit()
        print(f"Banco de dados '{db_name}' garantido com sucesso.")
        cursor.close()
        connection.close()

        # Restaura o banco de dados a partir do backup
        command = [
            "C:/Program Files/MySQL/MySQL Server 8.0/bin/mysql.exe",
            "-h", db_host,
            "-P", "3306",
            "-u", db_user,
            f"-p{db_password}",
            db_name
        ]
        with open(backup_file, "r") as backup:
            result = subprocess.run(
                command,
                stdin=backup,
                text=True,
                shell=True,
                timeout=50  # Tempo limite de 50 segundos
            )

        if result.returncode == 0:
            print("Restauração realizada com sucesso.")
            # Processa usuários excluídos após a restauração
            process_excluded_users(db_host, db_user, db_password, db_name, excluded_users_file)
        else:
            print(f"Erro ao realizar a restauração. Código de erro: {result.returncode}")
    except FileNotFoundError:
        print(f"Erro: Arquivo de backup '{backup_file}' não encontrado.")
    except subprocess.TimeoutExpired:
        print("Erro: O processo de restauração excedeu o tempo limite.")
    except mysql.connector.Error as err:
        print(f"Erro ao conectar ao MySQL: {err}")
    except Exception as e:
        print(f"Erro geral: {e}")


def process_excluded_users(db_host, db_user, db_password, db_name, excluded_users_file):
    if not os.path.exists(excluded_users_file):
        print("Nenhuma lista de usuários excluídos encontrada.")
        return

    try:
        with open(excluded_users_file, "r") as file:
            excluded_users = json.load(file)

        if not excluded_users:
            print("A lista de usuários excluídos está vazia.")
            return

        # Conecta ao banco de dados
        mydb = mysql.connector.connect(
            host=db_host,
            user=db_user,
            password=db_password,
            database=db_name
        )
        print("Conexão com o banco de dados estabelecida com sucesso.")
        cursor = mydb.cursor()

        for user_id in excluded_users:
            if remove_user_and_register(user_id, mydb):
                print(f"Usuário com ID {user_id} removido após a restauração.")
            else:
                print(f"Falha ao remover o usuário com ID {user_id}.")
                print(f"Tipo de user_id: {type(user_id)}")
                print(f"Conteúdo de user_id: {user_id}")

        cursor.close()
    except Exception as e:
        print(f"Erro ao processar a lista de usuários excluídos: {e}")



def remove_user_and_register(user_id, mydb, log_exclusion=True):
    try:
        print(f"\n--- Iniciando remoção para o usuário com ID: {user_id} ---")

        cursor = mydb.cursor()

        # Verifica se o ID é um dicionário
        if isinstance(user_id, dict) and 'id' in user_id:
            user_id = user_id['id']

        # Verifica se o usuário existe no banco
        cursor.execute("SELECT id FROM user_login WHERE id = %s", (user_id,))
        result = cursor.fetchone()

        if not result:
            print(f"Usuário com ID {user_id} não encontrado no banco.")
            cursor.close()
            return False

        user_id_found = result[0] if isinstance(result, tuple) else result['id']
        print(f"Usuário encontrado no banco com ID: {user_id_found}")

        # Remove o usuário
        cursor.execute("DELETE FROM user_login WHERE id = %s", (user_id_found,))
        mydb.commit()
        print(f"Usuário com ID {user_id_found} removido com sucesso do banco.")

        # Registro no JSON
        if log_exclusion:
            excluded_users_file = "excluded_users.json"
            if os.path.exists(excluded_users_file):
                with open(excluded_users_file, "r") as file:
                    excluded_users = json.load(file)
            else:
                excluded_users = []

            # Verifica duplicação no JSON
            if not any(user["id"] == str(user_id_found) for user in excluded_users):
                excluded_users.append({"id": str(user_id_found)})
                with open(excluded_users_file, "w") as file:
                    json.dump(excluded_users, file, indent=4)
                print(f"Usuário com ID {user_id_found} registrado na lista de excluídos.")
            else:
                print(f"Usuário com ID {user_id_found} já está na lista de excluídos.")

        print(f"Operação concluída para o usuário com ID: {user_id_found}\n")
        cursor.close()
        return True

    except Exception as e:
        print(f"Erro: {str(e)}")
        return False



if __name__ == "__main__":
    restore_backup()