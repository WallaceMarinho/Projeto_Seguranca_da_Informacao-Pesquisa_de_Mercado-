from dotenv import load_dotenv
import os
import subprocess

# Carrega as variáveis de ambiente
load_dotenv()

def restore_backup():
    db_host = os.getenv("DB_HOST_BACKUP")
    db_user = os.getenv("DB_USER")
    db_password = os.getenv("DB_PASSWORD")
    db_name = os.getenv("DB")
    backup_file = "backup.sql"

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
        with open(backup_file, "r") as backup:
            result = subprocess.run(
                command,
                stdin=backup,
                text=True,
                shell=True,
                timeout=50  # Tempo limite de 5 minutos
            )
            print(result)

            if result.returncode == 0:
                print("Restauração realizada com sucesso.")
            else:
                print("Erro ao realizar a restauração:", result.stderr)
    except FileNotFoundError:
        print(f"Erro: Arquivo de backup '{backup_file}' não encontrado.")
    except subprocess.TimeoutExpired:
        print("Erro: O processo de restauração excedeu o tempo limite.")

if __name__ == "__main__":
    restore_backup()
