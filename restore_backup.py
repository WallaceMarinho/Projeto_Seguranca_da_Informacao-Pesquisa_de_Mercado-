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

    command = [
        "C:/Program Files/MySQL/MySQL Server 8.0/bin/mysql.exe",
        "-h", db_host,
        "-P", "3306",
        "-u", db_user,
        f"-p{db_password}",
        db_name
    ]

    try:
        # Restaura o banco de dados a partir do backup
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
        print(f"Removendo conta do usuário local com ID: {user_id}")

        cursor = mydb.cursor()

        # Verifica se o usuário existe no banco
        if isinstance(user_id, dict) and 'id' in user_id:
            user_id = user_id['id']  # Extrai o ID do dicionário

        # Realiza a consulta com o ID correto
        cursor.execute("SELECT id FROM user_login WHERE id = %s", (user_id,))
        result = cursor.fetchone()  # Obtém apenas um registro ou None se não existir

        if not result:
            print(f"Usuário com ID {user_id} não encontrado no banco.")
            cursor.close()
            return False

        # Verifica se o resultado é um dicionário com a chave 'id'
        if isinstance(result, dict) and 'id' in result:
            user_id_found = result['id']  # Extrai o ID do dicionário
        elif isinstance(result, tuple):
            user_id_found = result[0]  # Extrai o ID de uma tupla
        else:
            print(f"Resultado inesperado: {result}")
            cursor.close()
            return False

        print(f"Usuário encontrado com ID: {user_id_found}")

        # Remove o usuário do banco
        cursor.execute("DELETE FROM user_login WHERE id = %s", (user_id_found,))
        mydb.commit()
        print(f"Usuário com ID {user_id_found} removido com sucesso.")

        # Registra a exclusão, se necessário
        if log_exclusion:
            excluded_users_file = "excluded_users.json"

            # Carrega ou inicializa o arquivo JSON
            if os.path.exists(excluded_users_file):
                with open(excluded_users_file, "r") as file:
                    excluded_users = json.load(file)
            else:
                excluded_users = []

            # Adiciona apenas o ID ao JSON
            excluded_users.append({"id": str(user_id_found)})

            # Salva no arquivo JSON
            with open(excluded_users_file, "w") as file:
                json.dump(excluded_users, file, indent=4)

            print(f"Usuário com ID {user_id_found} registrado na lista de excluídos.")
        else:
            print(f"Usuário com ID {user_id_found} removido sem registro.")

        cursor.close()
        return True

    except mysql.connector.Error as err:
        print(f"Erro no banco de dados: {err}, Código do erro: {err.errno}, SQL: {err.sqlstate}")
        import traceback
        traceback.print_exc()
        return False

    except Exception as e:
        print(f"Erro geral: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    restore_backup()