from so_create_adm import create_default_admin
from so_terms_login import main
from so_create_db import connect, create_tables 

if __name__ == "__main__":
    tunnel, mydb = connect()

    if mydb:
        try:
            create_tables(mydb)					# Cria as Tabelas
            create_default_admin(mydb)  # Passa a conexão para a função
            main(tunnel, mydb)					# Passa a conexão para o main também
        finally:
            mydb.close()
            tunnel.close()
    else:
        print("Erro ao conectar ao banco de dados.")
