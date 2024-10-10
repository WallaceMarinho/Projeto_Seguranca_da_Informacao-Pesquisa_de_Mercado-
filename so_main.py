import socket
from so_create_adm import create_default_admin
from so_terms_login import main
from so_create_db import connect, create_tables 

from flask import Flask, render_template  # Importe as classes Flask
from flask_socketio import SocketIO, emit  # Importe as classes SocketIO

app = Flask(__name__)  # Crie a instância do Flask
socketio = SocketIO(app)  # Crie a instância do SocketIO

@app.route('/')  # Opcional: Rota para renderizar o index.html
def index():
    return render_template('index.html')

@socketio.on('connect')
def handle_connect():
    print('Client connected')
    emit('server_info', {'data': get_server_info()})

def get_server_info():
    # ... sua lógica para obter informações do servidor
    hostname = socket.gethostname()
    ip_address = socket.gethostbyname(hostname)
    return f"Hostname: {hostname}, IP: {ip_address}"

if __name__ == "__main__":
    tunnel, mydb = connect()

    if mydb:
        try:
            create_tables(mydb)  # Cria as Tabelas
            create_default_admin(mydb)  # Passa a conexão para a função
            main(tunnel, mydb)  # Passa a conexão para o main também
        finally:
            mydb.close()
            tunnel.close()
    else:
        print("Erro ao conectar ao banco de dados.")

    socketio.run(app, host='192.168.1.7', port=8080)  # Inicie o Flask e o SocketIO