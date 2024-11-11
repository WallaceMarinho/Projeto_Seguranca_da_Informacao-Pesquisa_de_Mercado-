import bcrypt
from flask import session
from pymysql.cursors import DictCursor
import os
import datetime

def log_event(event, table, record_id, additional_info=None):
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    log_file_path = os.path.join(log_dir, "surveyLog.txt")

    with open(log_file_path, "a") as log_file:
        log_message = f"{datetime.datetime.now()} | Evento: {event} | Tabela: {table} | ID: {record_id}"
        if additional_info:
            log_message += f" | Info adicional: {additional_info}"
        log_file.write(log_message + "\n")

bairros = [
		'EUGÊNIO DE MELO', 'JARDIM IPÊ', 'JARDIM ITAPUÃ', 
		'RESIDENCIAL ARMANDO MOREIRA RIGHI', 'RESIDENCIAL GALO BRANCO', 
		'CONJ. HAB. JARDIM SÃO JOSÉ', 'JARDIM AMERICANO', 'JARDIM COQUEIRO', 
		'JARDIM MOTORAMA', 'JARDIM NOVA DETROIT', 'JARDIM NOVA FLORIDA', 
		'JARDIM PARARANGABA', 'JARDIM RODOLFO', 'JARDIM SANTA INÊS I', 
		'JARDIM SANTA INÊS II', 'JARDIM SANTA INÊS III', 'JARDIM SÃO JOSÉ', 
		'JARDIM SÃO VICENTE', 'RESIDENCIAL ANA MARIA', 'RESIDENCIAL CAMPO BELO', 
		'RESIDENCIAL FREI GALVÃO', 'JARDIM CASTANHEIRA', 'JARDIM CEREJEIRAS', 
		'JARDIM NOVA MICHIGAN', 'JARDIM PAINEIRAS I', 'JARDIM PAINEIRAS II', 
		'JARDIM SAN RAFAEL', 'PARQUE NOVA ESPERANÇA', 'PARQUE NOVO HORIZONTE', 
		'RESIDENCIAL DOM BOSCO', 'CAMPOS DE SÃO JOSÉ', 'JARDIM HELENA', 
		'JARDIM MARIANA', 'JARDIM MARIANA II', 'POUSADA DO VALE', 
		'VILA MONTERREY'
]

def register_user(mydb, nome, sobrenome, telefone, email, senha, bairro, provider='local'):
    if mydb:
        try:
            with mydb.cursor() as cursor:
                cursor.execute("USE surveydb")

                if provider == 'local' and senha:
                    hashed_password = bcrypt.hashpw(senha.encode('utf-8'), bcrypt.gensalt())
                else:
                    hashed_password = None 

                cursor.execute(
                    "INSERT INTO user_login (nome, sobrenome, telefone, email, password, bairro, provider) "
                    "VALUES (%s, %s, %s, %s, %s, %s, %s)", 
                    (nome, sobrenome, telefone, email, hashed_password, bairro, provider)
                )
                mydb.commit()
                user_id = cursor.lastrowid

                terms_accepted = session.get('terms_accepted')
                terms_version = terms_accepted.get('terms_version')
                privacy_version = terms_accepted.get('privacy_version')

                optional_version = terms_accepted.get('optional_version') if terms_accepted.get('optional') else None

                cursor.execute(
                    "INSERT INTO user_terms_and_privacy_acceptance (user_id, terms_version, privacy_version, optional_version, accepted_at) "
                    "VALUES (%s, %s, %s, %s, CURRENT_TIMESTAMP)",
                    (user_id, terms_version, privacy_version, optional_version)
                )

                mydb.commit()
                session['user_id'] = user_id

                log_event("Novo usuário adicionado", "user_login", user_id)
                terms_info = get_terms_and_privacy(mydb)
                if terms_info:
                    version_info = f"Versão dos Termos: {terms_info['terms_version']}, Versão da Privacidade: {terms_info['privacy_version']}"
                    log_event("Termos e Política de privacidade aceitos", "user_terms_and_privacy_acceptance", user_id, additional_info=version_info)

                return user_id

        except Exception as e:
            mydb.rollback()
            print("Erro ao cadastrar usuário:", e)
            return None

def login_user(mydb, form_data):
    email = form_data.get('email')
    senha = form_data.get('password')

    if mydb:
        with mydb.cursor(cursor=DictCursor) as cursor:
            cursor.execute("USE surveydb")
            cursor.execute("SELECT id, password, provider, role, is_default_admin FROM user_login WHERE email = %s", (email,))
            user = cursor.fetchone()

            if user:
                user_id = user['id']
                hashed_password = user['password']
                provider = user['provider']
                role = user['role']
                is_default_admin = user['is_default_admin']

                # Verifica a senha
                if bcrypt.checkpw(senha.encode('utf-8'), hashed_password.encode('utf-8')):
                    if role == 'admin':
                        # Login de admin
                        session['user_id'] = user_id
                        session['provider'] = provider
                        session['role'] = role
                        session['is_default_admin'] = is_default_admin
                        return {
                            "user_id": user_id,
                            "role": role,
                            "is_default_admin": is_default_admin,
                            "update_required": False
                        }

                    # Verifica termos para usuários comuns
                    cursor.execute(""" 
                        SELECT terms_version, privacy_version FROM user_terms_and_privacy_acceptance 
                        WHERE user_id = %s ORDER BY accepted_at DESC LIMIT 1
                    """, (user_id,))
                    user_terms = cursor.fetchone()

                    if user_terms:
                        terms_version = user_terms['terms_version']
                        privacy_version = user_terms['privacy_version']
                    else:
                        terms_version, privacy_version = None, None

                    terms_data = get_terms_and_privacy(mydb)

                    if terms_version != terms_data['terms_version'] or privacy_version != terms_data['privacy_version']:
                        return {
                            "user_id": user_id,
                            "terms_required": terms_data['terms'],
                            "privacy_required": terms_data['privacy'],
                            "update_required": True,
                            "role": role,
                            "is_default_admin": is_default_admin
                        }

                    # Se não há atualização de termos, armazena na sessão
                    session['user_id'] = user_id
                    session['provider'] = provider
                    session['role'] = role
                    session['is_default_admin'] = is_default_admin
                    return {
                        "user_id": user_id,
                        "role": role,
                        "is_default_admin": is_default_admin,
                        "update_required": False
                    }

            return None

def get_terms_and_privacy(mydb):
    if mydb:
        with mydb.cursor() as cursor:
            cursor.execute("USE surveydb")

            cursor.execute("SELECT version, content FROM terms_and_privacy_policy WHERE type = 'terms' ORDER BY created_at DESC LIMIT 1")
            terms = cursor.fetchone()

            cursor.execute("SELECT version, content FROM terms_and_privacy_policy WHERE type = 'optional' ORDER BY created_at DESC LIMIT 1")
            optional = cursor.fetchone()

            cursor.execute("SELECT version, content FROM terms_and_privacy_policy WHERE type = 'privacy' ORDER BY created_at DESC LIMIT 1")
            privacy = cursor.fetchone()

            return {
                "terms": terms['content'],
                "terms_version": terms['version'],
                "optional": optional['content'],
                "optional_version": optional['version'],
                "privacy": privacy['content'],
                "privacy_version": privacy['version'],
                "message": "Para cancelar o consentimento obrigatório, exclua sua conta ou solicite a exclusão em admin@system.com."
            }
    return None

def verify_terms_version(mydb, user_id):
    terms_and_privacy = get_terms_and_privacy(mydb)

    if terms_and_privacy is None:
        print("Erro ao obter termos e política de privacidade.")
        return None

    current_terms_version = terms_and_privacy['terms_version']
    current_privacy_version = terms_and_privacy['privacy_version']
    current_optional_version = terms_and_privacy['optional_version']

    with mydb.cursor(cursor=DictCursor) as cursor:
        cursor.execute(""" 
            SELECT terms_version, privacy_version, optional_version 
            FROM user_terms_and_privacy_acceptance 
            WHERE user_id = %s 
        """, (user_id,))
        user_terms = cursor.fetchone()

        print(f"ID do usuário: {user_id}")
        print(f"Versões atuais do banco:\nTermos: {current_terms_version}, "
              f"\nPolítica de Privacidade: {current_privacy_version}, "
              f"\nTermos Opcionais: {current_optional_version}")
        
        if user_terms:
            print(f"Versões aceitas pelo usuário:\nTermos: {user_terms['terms_version']}, "
                  f"\nPolítica de Privacidade: {user_terms['privacy_version']}, "
                  f"\nTermos Opcionais: {user_terms['optional_version']}")
        else:
            print(f"Usuário {user_id} ainda não aceitou os termos ou a política.")

        terms_ok = (user_terms and user_terms['terms_version'] == current_terms_version) if user_terms else False
        privacy_ok = (user_terms and user_terms['privacy_version'] == current_privacy_version) if user_terms else False
        optional_ok = (user_terms and user_terms['optional_version'] == current_optional_version) if user_terms else False

        return {
            'terms_ok': terms_ok,
            'privacy_ok': privacy_ok,
            'optional_ok': optional_ok,
            'current_terms_version': current_terms_version,
            'current_privacy_version': current_privacy_version,
            'current_optional_version': current_optional_version
        }

def update_user_terms_acceptance(mydb, user_id, terms_version, privacy_version):
    with mydb.cursor() as cursor:
        cursor.execute("USE surveydb")
        
        # Verifica se já existe um registro para o user_id
        cursor.execute("""
            SELECT user_id FROM user_terms_and_privacy_acceptance WHERE user_id = %s
        """, (user_id,))
        
        if cursor.fetchone():
            # Atualiza as versões se o registro já existir
            cursor.execute("""
                UPDATE user_terms_and_privacy_acceptance 
                SET terms_version = %s, privacy_version = %s, accepted_at = NOW()
                WHERE user_id = %s
            """, (terms_version, privacy_version, user_id))
        else:
            # Insere um novo registro se não existir
            cursor.execute("""
                INSERT INTO user_terms_and_privacy_acceptance (user_id, terms_version, privacy_version, accepted_at)
                VALUES (%s, %s, %s, NOW())
            """, (user_id, terms_version, privacy_version))
        
        mydb.commit()
        
        log_event(f"Aceitação dos Termos - Versão {terms_version}, Política de Privacidade - Versão {privacy_version}",
                  "user_terms_and_privacy_acceptance", user_id)

def get_user_optional_version(mydb):
    user_id = session.get('user_id')
    if user_id is None:
        raise ValueError("User ID not found in session.")

    with mydb.cursor() as cursor:
        cursor.execute("USE surveydb")
        cursor.execute("""
            SELECT optional_version 
            FROM user_terms_and_privacy_acceptance 
            WHERE user_id = %s
        """, (user_id,))

        result = cursor.fetchone()
        return result['optional_version'] if result else None
