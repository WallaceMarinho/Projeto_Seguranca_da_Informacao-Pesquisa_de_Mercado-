from dotenv import load_dotenv
import os
import subprocess

# Carrega as variáveis de ambiente
load_dotenv()

def realizar_backup():
    db_host = os.getenv("DB_HOST_BACKUP")
    print(db_host)
    db_user = os.getenv("DB_USER")
    db_password = os.getenv("DB_PASSWORD")
    db_name = os.getenv("DB")

    # Verifica se todas as variáveis de ambiente estão definidas
    if not all([db_host, db_user, db_password, db_name]):
        print("Erro: Verifique se todas as variáveis de ambiente (DB_HOST, DB_USER, DB_PASSWORD, DB) estão definidas.")
        return

    backup_file = "backup.sql"
    command = [
        "C:/Program Files/MySQL/MySQL Server 8.0/bin/mysqldump.exe",
        "-h", db_host,      # Certifique-se de que db_host está correto
        "-u", db_user,
        "-p", db_name  
    ]

    with open(backup_file, "w") as backup:
        result = subprocess.run(command, stdout=backup, text=True)
        
        if result.returncode == 0:
            print(f"Backup realizado com sucesso. Arquivo de backup: {backup_file}")
        else:
            print("Erro ao realizar o backup:", result.stderr)

if __name__ == "__main__":
    realizar_backup()
