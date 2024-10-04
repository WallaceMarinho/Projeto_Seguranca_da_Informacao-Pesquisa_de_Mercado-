from sshtunnel import SSHTunnelForwarder
import mysql.connector
from mysql.connector import errorcode
from config import config

def connect():

  ssh_config = config['ssh']
  mysql_config = config['mysql']

  tunnel = SSHTunnelForwarder(
      ssh_config['host'],
      ssh_port=ssh_config['port'],
      ssh_username=ssh_config['username'],
      ssh_password=ssh_config['password'],
      remote_bind_address=ssh_config['remote_bind_address']
  )
  tunnel.start()

  mysql_config['port'] = tunnel.local_bind_port

  try:
      conn = mysql.connector.connect(**mysql_config)
      print("Connection established")

  except mysql.connector.Error as err:
    if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
        print("Something is wrong with the user name or password")
    else:
        print(err)

  else:
    # Crie um objeto cursor para executar comandos SQL
    mycursor = conn.cursor()

    # Execute o comando para verificar e criar se o banco de dados não existir
    mycursor.execute("CREATE DATABASE IF NOT EXISTS debiandb")

    return tunnel, conn