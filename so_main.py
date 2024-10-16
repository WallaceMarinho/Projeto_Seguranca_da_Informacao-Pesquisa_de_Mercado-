import os
import signal
from flask import Flask, request, jsonify
from routes import app_routes
from session_config import configure_session
from so_create_adm import create_default_admin
from db_connection import mydb, tunnel, keep_connection_alive
from so_create_db import create_tables

app = Flask(__name__)

configure_session(app)

def init_app():
    if mydb:
        try:
            create_tables(mydb)
            create_default_admin(mydb)
        except Exception as e:
            print(f"Erro ao executar a inicialização: {e}")
    else:
        raise ConnectionError("Erro ao conectar ao banco de dados.")

def close_connection():
    global tunnel, mydb
    if mydb:
        try:
            mydb.close()
            print("Conexão com o banco de dados fechada.")
        except Exception as e:
            print(f"Erro ao fechar a conexão com o banco de dados: {e}")
    if tunnel:
        try:
            if tunnel.is_active:
                tunnel.close()
                print("Túnel SSH fechado.")
        except Exception as e:
            print(f"Erro ao fechar o túnel SSH: {e}")

# Função para lidar com SIGINT (CTRL+C)
def handle_sigint(signal, frame):
    print("CTRL+C capturado! Encerrando a aplicação...")
    close_connection()
    exit(0)

if os.environ.get('WERKZEUG_RUN_MAIN') != 'true':
    signal.signal(signal.SIGINT, handle_sigint)

    try:
        init_app()

        import threading
        threading.Thread(target=keep_connection_alive, daemon=True).start()

    except ConnectionError as e:
        print(e)
        exit(1)

app.register_blueprint(app_routes)

@app.route('/shutdown', methods=['POST'])
def shutdown():
    shutdown_code = request.json.get('shutdown_code')
    correct_code = os.getenv('SHUTDOWN_CODE')

    if shutdown_code == correct_code:
        close_connection()
        shutdown_func = request.environ.get('werkzeug.server.shutdown')
        if shutdown_func is None:
            raise RuntimeError('Não foi possível encerrar o servidor.')
        shutdown_func()
        return jsonify({"message": "Servidor encerrado com sucesso."}), 200
    else:
        return jsonify({"message": "Código de shutdown incorreto."}), 403

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
