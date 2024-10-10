import os
from flask import Flask, render_template
from flask_socketio import SocketIO, emit

app = Flask(__name__)
socketio = SocketIO(app)

@app.route('/')
def index():
    # Obtém o nome do servidor da variável de ambiente
    server_name = os.environ.get('SERVER_NAME', 'unknown')
    return render_template('index.html', server_name=server_name)

@socketio.on('connect')
def handle_connect():
    print('Client connected')
    server_name = os.environ.get('SERVER_NAME', 'unknown')
    emit('server_info', {'data': server_name})

if __name__ == "__main__":
    # Executa o Flask com host e porta configuráveis por variável de ambiente
    socketio.run(app, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
