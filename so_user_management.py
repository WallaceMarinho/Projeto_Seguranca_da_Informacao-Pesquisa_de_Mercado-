import datetime
import os
import bcrypt
from flask import session
from pymysql.cursors import DictCursor
from db_connection import mydb
from so_terms_login import format_optional_code

def log_adm_event(event, changed_data=None, failed_attempt=False):
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    log_file_path = os.path.join(log_dir, "admLog.txt")

    admin_id = session.get('user_id')  # Pega o ID do usuário logado
    log_message = f"{datetime.datetime.now()} | Admin ID: {admin_id} | Evento: {event}"

    if changed_data:
        log_message += f" | Dados alterados: {changed_data}"
    if failed_attempt:
        log_message += " | Tentativa falha de salvar alterações"

    with open(log_file_path, "a") as log_file:
        log_file.write(log_message + "\n")

def fetch_user_dashboard_data(user_id):
    with mydb.cursor(cursor=DictCursor) as cursor:
        cursor.execute("USE surveydb")
        cursor.execute("SELECT id, email, role, is_default_admin, provider FROM user_login WHERE id = %s", (user_id,))
        user = cursor.fetchone()
    return user

def update_user(user_id, form_data):
    try:
        with mydb.cursor() as cursor:
            cursor.execute("SELECT * FROM user_login WHERE id = %s", (user_id,))
            user = cursor.fetchone()

            nome = form_data.get('nome', user['nome'])
            sobrenome = form_data.get('sobrenome', user['sobrenome'])
            telefone = form_data.get('telefone', user['telefone'])
            bairro = form_data.get('bairro', user['bairro'])
            senha = form_data.get('senha') or user['password']

            update_query = """
                UPDATE user_login 
                SET nome = %s, sobrenome = %s, telefone = %s, bairro = %s, password = %s
                WHERE id = %s
            """
            cursor.execute(update_query, (nome, sobrenome, telefone, bairro, senha, user_id))
            mydb.commit()
            return True
    except Exception as e:
        print("Erro ao atualizar usuário:", e)
        return False

def fetch_current_policy_terms(mydb, tipo):
    with mydb.cursor(cursor=DictCursor) as cursor:
        cursor.execute("USE surveydb")
        cursor.execute("SELECT version, content FROM terms_and_privacy_policy WHERE type = %s AND is_current = TRUE", (tipo,))
        row = cursor.fetchone()

        if row:
            return {
                'success': True,
                'version': row['version'],  # Retorna a versão atual
                'content': row['content']    # Retorna o conteúdo atual
            }
        return {'success': False, 'message': 'Termo não encontrado.'}

def update_terms_policy(mydb, type, content):
    if mydb:
        try:
            with mydb.cursor() as cursor:
                print(type)
                cursor.execute("USE surveydb")
                cursor.execute(""" 
                    SELECT version FROM terms_and_privacy_policy
                    WHERE type = %s AND is_current = TRUE
                """, (type,))
                result = cursor.fetchone()['version']
                print(result)

                if result is None:
                    raise ValueError("Verifique o erro, não é possível versão None.")

                max_version = int(result)
                new_version = str(max_version + 1).zfill(4)
                print(new_version)

                # Desativa a versão atual
                cursor.execute(""" 
                    UPDATE terms_and_privacy_policy 
                    SET is_current = FALSE 
                    WHERE type = %s AND is_current = TRUE
                """, (type,))

                cursor.execute(""" 
                    INSERT INTO terms_and_privacy_policy (version, content, type, is_current) 
                    VALUES (%s, %s, %s, TRUE)
                """, (new_version, content, type))

                mydb.commit()
                print("Política/Termo atualizado com sucesso.")
        except Exception as e:
            print(f"Erro ao atualizar política/termos: {e}")
            mydb.rollback()
            raise

def fetch_current_terms():
    try:
        cursor = mydb.cursor(DictCursor)
        cursor.execute("USE surveydb")
        cursor.execute("SELECT id, optional_code, version, content FROM optional_terms WHERE is_current = TRUE")
        return cursor.fetchall()
    except Exception as e:
        print(f"Erro ao buscar termos opcionais atuais: {e}")
        return []

def insert_optional_term_in_db(content):
    with mydb.cursor(cursor=DictCursor) as cursor:
        cursor.execute("USE surveydb")
        cursor.execute(
            "INSERT INTO optional_terms (content, is_current) VALUES (%s, TRUE)",
            (content,)
        )
        
        mydb.commit()

def update_optional_term_in_db(term_id, new_content):
    with mydb.cursor(cursor=DictCursor) as cursor:
        try:
            cursor.execute("USE surveydb")
            cursor.execute(
                "SELECT optional_code FROM optional_terms WHERE id = %s",
                (term_id,)
            )
            result = cursor.fetchone()
            if not result:
                raise ValueError(f"Termo opcional não encontrado para o ID {term_id}.")
            
            optional_code = result['optional_code']
            cursor.execute(
                """
                SELECT LPAD(COALESCE(MAX(CAST(version AS UNSIGNED)) + 1, 1), 4, '0') AS new_version
                FROM optional_terms 
                WHERE id = %s
                """,
                (term_id,)
            )

            version_result = cursor.fetchone()
            new_version = version_result['new_version']

            cursor.execute(
                "UPDATE optional_terms SET is_current = FALSE WHERE id = %s",
                (term_id,)
            )

            cursor.execute(
                """
                INSERT INTO optional_terms (optional_code, version, content, is_current)
                VALUES (%s, %s, %s, TRUE)
                """,
                (optional_code, new_version, new_content)
            )

            mydb.commit()

        except Exception as e:
            print(f"Ocorreu um erro durante a execução da consulta: {e}")
            mydb.rollback()

def remove_optional_term(term_id):
    with mydb.cursor(cursor=DictCursor) as cursor:
        cursor.execute("USE surveydb")
        cursor.execute("DELETE FROM optional_terms WHERE id = %s", (term_id,))
        mydb.commit()

def format_timestamp(ts):
    if ts is not None:
        return ts.strftime("%d/%m/%Y %H:%M:%S")
    return "N/A"

def list_users(mydb, role):
    if mydb:
        try:
            if role == 'user':
                role_condition = "role = 'user'"
            elif role == 'admin':
                role_condition = "role = 'admin' AND is_default_admin = FALSE"
            else:
                print("Opção inválida. Por favor, escolha 'admin' ou 'user'.")
                return []

            with mydb.cursor(cursor=DictCursor) as cursor:
                cursor.execute("USE surveydb")
                cursor.execute(f"SELECT * FROM user_login WHERE {role_condition} ORDER BY id")
                users = cursor.fetchall() or []

                if users:
                    for user in users:
                        cursor.execute("SELECT answer FROM survey_responses WHERE user_id = %s", (user['id'],))
                        respostas = cursor.fetchall() or []
                        if respostas:
                            print("Respostas do questionário:")
                            for resposta in respostas:
                                print(f"- {resposta['answer']}")
                        else:
                            print("Nenhuma resposta do questionário encontrada.")
                        print("---")
                else:
                    print("Nenhum usuário encontrado.")
                
                return users
        except Exception as e:
            print(f"Erro ao listar usuários: {e}")
            return []
    else:
        print("Erro ao conectar ao banco de dados.")
        return []

def validate_admin_password(adm_id, senha):
    if not mydb:
        return False

    with mydb.cursor() as cursor:
        cursor.execute("USE surveydb")
        cursor.execute("SELECT password FROM user_login WHERE id = %s", (adm_id,))
        admin_user = cursor.fetchone()

        if admin_user:
            hashed_password = admin_user['password']
            if bcrypt.checkpw(senha.encode('utf-8'), hashed_password.encode('utf-8')):
                return True
                
    return False

def update_user_email_in_db(user_id, new_email):
    if not mydb:
        raise Exception("Erro ao conectar ao banco de dados.")

    try:
        with mydb.cursor() as cursor:
            cursor.execute("UPDATE user_login SET email = %s WHERE id = %s", (new_email, user_id))
            mydb.commit()
    except Exception as e:
        raise Exception(f"Erro ao atualizar e-mail: {e}")

def remove_user_by_id(user_id):
    try:
        with mydb.cursor() as cursor:
            # Exclui o usuário do banco de dados pelo ID
            cursor.execute("DELETE FROM user_login WHERE id = %s", (user_id,))
            mydb.commit()
            return True
    except Exception as e:
        print(f"Erro ao remover o usuário: {e}")
        return False

def remove_admin_by_id(user_id, admin_email, mydb):
    if mydb:
        try:
            with mydb.cursor() as cursor:
                cursor.execute("SELECT * FROM user_login WHERE id = %s", (user_id,))
                user_to_remove = cursor.fetchone()
                cursor.execute("SELECT * FROM user_login WHERE email = %s", (admin_email,))
                admin_user = cursor.fetchone()

                if user_to_remove:
                    if user_to_remove['role'] == 'admin' and admin_user['is_default_admin'] != True:
                        print("Você não tem permissão para remover um usuário admin.")
                        return False

                    confirm = input("Tem certeza que deseja remover este usuário? (s/n): ").strip().lower()
                    
                    if confirm == 's':
                        cursor.execute("DELETE FROM user_login WHERE id = %s", (user_id,))
                        mydb.commit()
                        print("Usuário removido com sucesso.")
                        return True
                    else:
                        print("Operação cancelada.")
                        return False
                else:
                    print("Nenhum usuário encontrado com o ID fornecido.")
                    return False
        except Exception as e:
            print(f"Erro ao remover o usuário: {e}")
            return False
    else:
        print("Erro ao conectar ao banco de dados.")
        return False

def create_admin(nome, sobrenome, telefone, email, password, mydb):
    if mydb:
        try:
            with mydb.cursor() as cursor:
                cursor.execute("SELECT * FROM user_login WHERE email = %s", (email,))
                existing_user = cursor.fetchone()

                if existing_user:
                    print("Email já está em uso. Por favor, use um email diferente.")
                else:
                    cursor.execute("""INSERT INTO user_login (nome, sobrenome, telefone, email, password, role, bairro)
                                      VALUES (%s, %s, %s, %s, %s, 'admin', 'NENHUM')""",
                                   (nome, sobrenome, telefone, email, password))
                    mydb.commit()
                    print("Novo usuário admin criado com sucesso.")
        except Exception as e:
            print(f"Erro ao criar usuário admin: {e}")
    else:
        print("Erro ao conectar ao banco de dados.")