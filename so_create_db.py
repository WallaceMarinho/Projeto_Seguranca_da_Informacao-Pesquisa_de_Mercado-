import pymysql
from sshtunnel import SSHTunnelForwarder
from config import config

def connect():
    ssh_config = config['ssh']
    mysql_config = config['mysql']

    try:
        tunnel = SSHTunnelForwarder(
            ssh_config['host'],
            ssh_port=ssh_config['port'],
            ssh_username=ssh_config['username'],
            ssh_password=ssh_config['password'],
            #ssh_pkey=ssh_config['private_key'],
            remote_bind_address=ssh_config['remote_bind_address']
        )

        tunnel.start()
        print("Conexão SSH estabelecida com sucesso.")

    except Exception as e:
        print(f"Erro ao estabelecer conexão SSH: {e}")
        return None, None

    mysql_config['port'] = tunnel.local_bind_port

    try:
        conn = pymysql.connect(
            host=mysql_config['host'],
            user=mysql_config['user'],
            password=mysql_config['password'],
            port=mysql_config['port'],
            cursorclass=pymysql.cursors.DictCursor,
            connect_timeout=60
        )
        print("Conexão com o banco de dados MariaDB/MySQL estabelecida com sucesso.")

        return tunnel, conn

    except pymysql.MySQLError as err:
        print("Erro ao conectar-se ao banco de dados:")
        print(f"Erro de conexão: {err}")

    return None, None

def create_tables(mydb):
    with open('ddl.sql', 'r') as f:
        ddl_script = f.read()
    with mydb.cursor() as cursor:
        for statement in ddl_script.split(';'):
            if statement.strip():
                cursor.execute(statement)
        mydb.commit()
        print("Tabelas criadas com sucesso.")

# TESTAR ddl.sql e A CONEXÃO com DB
if __name__ == "__main__":
    tunnel, mydb = connect()
    if mydb:
        create_tables(mydb)
        mydb.close() 
        tunnel.stop() 
    else:
        print("Falha ao conectar ao banco de dados.")
