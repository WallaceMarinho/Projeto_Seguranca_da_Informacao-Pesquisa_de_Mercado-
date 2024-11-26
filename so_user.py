import bcrypt
from flask import jsonify, request
from pymysql.cursors import DictCursor

from excluded_users import add_to_excluded_users
from so_terms_login import format_optional_code, get_terms_and_privacy, get_user_optional_version, log_event

def view_user_data(user_id, mydb):
    with mydb.cursor(cursor=DictCursor) as cursor:
        cursor.execute("USE surveydb")
        cursor.execute("SELECT nome, sobrenome, telefone, bairro, email, role, provider FROM user_login WHERE id = %s", (user_id,))
        row = cursor.fetchone()

        if row:
            return {
                'nome': row['nome'],
                'sobrenome': row['sobrenome'],
                'telefone': row['telefone'],
                'bairro': row['bairro'],
                'email': row['email'],
                'role': row['role'],
                'provider': row['provider']
            }
        return None

def edit_user_data(user_id, mydb):
    cursor = mydb.cursor()
    cursor.execute("USE surveydb")
    
    nome = request.form.get('nome', '').strip()
    sobrenome = request.form.get('sobrenome', '').strip()
    telefone = request.form.get('telefone', '').strip()
    senha = request.form.get('senha', '').strip()
    bairro = request.form.get('bairro', '').strip()

    if senha and (len(senha) != 6 or not senha.isdigit()):
        return jsonify({"success": False, "message": "A senha deve ter exatamente 6 dígitos."})

    if nome:
        cursor.execute("UPDATE user_login SET nome = %s WHERE id = %s", (nome, user_id))
    if sobrenome:
        cursor.execute("UPDATE user_login SET sobrenome = %s WHERE id = %s", (sobrenome, user_id))
    if telefone:
        cursor.execute("UPDATE user_login SET telefone = %s WHERE id = %s", (telefone, user_id))
    if senha:
        cursor.execute("UPDATE user_login SET password = %s WHERE id = %s", (senha, user_id))
    if bairro:
        cursor.execute("UPDATE user_login SET bairro = %s WHERE id = %s", (bairro, user_id))

    mydb.commit()
    return jsonify({"success": True, "message": "Dados pessoais atualizados com sucesso."})

def get_user_terms_status(user_id, mydb):
    try:
        # Obter os termos obrigatórios, privacidade e versão opcional do usuário
        cursor = mydb.cursor(DictCursor)
        cursor.execute("USE surveydb")

        # Obter os termos obrigatórios, política de privacidade e versão opcional do usuário
        cursor.execute("""
            SELECT 
                terms_version, 
                privacy_version, 
                optional_version
            FROM user_terms_and_privacy_acceptance
            WHERE user_id = %s
        """, (user_id,))
        result = cursor.fetchone()

        # Verificar o consentimento do termo "Recebimento de emails"
        cursor.execute("""
            SELECT 
                CASE WHEN optional_version IS NOT NULL THEN TRUE ELSE FALSE END AS consented
            FROM user_terms_and_privacy_acceptance
            WHERE user_id = %s
            AND optional_version IS NOT NULL
        """, (user_id,))
        email_term_result = cursor.fetchone()

        # Obter todos os termos opcionais relacionados ao usuário
        cursor.execute("""
            SELECT 
                ot.id, 
                ot.optional_code, 
                ot.version, 
                ot.content, 
                CASE WHEN uota.optional_term_id IS NOT NULL THEN TRUE ELSE FALSE END AS consented
            FROM optional_terms ot
            LEFT JOIN user_optional_terms_acceptance uota 
            ON ot.id = uota.optional_term_id AND uota.user_id = %s
            WHERE ot.is_current = TRUE
        """, (user_id,))
        optional_terms = cursor.fetchall()

        # Verificar se o usuário tem os termos obrigatórios e de privacidade aceitos
        terms_status = {
            'mandatory_terms': result['terms_version'] if result else None,
            'privacy_version': result['privacy_version'] if result else None,
            'optional_version': result['optional_version'] if result else None,
            'optional_email_consented': email_term_result['consented'] if email_term_result else False
        }

        # Adicionar os termos opcionais ao retorno
        optional_terms_status = [
            {
                'id': term['id'],
                'optional_code': term['optional_code'],
                'version': term['version'],
                'content': term['content'],
                'consented': term['consented']  # Indica se o usuário aceitou o termo
            }
            for term in optional_terms
        ]

        # Adicionar os termos opcionais ao dicionário de status
        terms_status['optional_terms'] = optional_terms_status

        return terms_status

    except Exception as e:
        print(f"Erro ao buscar status dos termos: {e}")
        return {
            'error': True,
            'message': "Erro ao acessar o banco de dados."
        }

def update_user_optional_terms(user_id, optional_terms_accepted, mydb):
    try:
        cursor = mydb.cursor()
        cursor.execute("USE surveydb")

        # Recuperar a versão mais recente dos termos opcionais
        terms_and_privacy = get_terms_and_privacy(mydb)
        optional_version = terms_and_privacy.get("optional_version")

        # Verificar a versão atual aceita pelo usuário
        current_optional_version = get_user_optional_version(mydb)

        # Obter termos opcionais já aceitos pelo usuário (somente os que estão com is_current = TRUE)
        cursor.execute("""
            SELECT u.optional_term_id
            FROM user_optional_terms_acceptance u
            JOIN optional_terms o ON u.optional_term_id = o.id
            WHERE u.user_id = %s AND o.is_current = TRUE
        """, (user_id,))
        result = cursor.fetchall()

        # Guardar os termos que o usuário já aceitou
        existing_terms = set(int(row['optional_term_id']) for row in result)

        # Filtrar os termos para excluir o 'optional_email' da lógica de comparação de termos
        filtered_optional_terms = [term for term in optional_terms_accepted if term != 'optional_email']

        # Converter os termos do frontend para inteiros para comparação
        new_terms_set = set(int(term) for term in filtered_optional_terms)

        # Determinar os termos que foram marcados e desmarcados
        terms_to_add = new_terms_set - existing_terms  # Termos que o usuário agora quer adicionar
        terms_to_remove = existing_terms - new_terms_set  # Termos que o usuário desmarcou

        print("Existing terms:", existing_terms)
        print("New terms set:", new_terms_set)
        print("Terms to add:", terms_to_add)
        print("Terms to remove:", terms_to_remove)

        # Flag para verificar se houve mudanças
        changes_made = False

        # Determinar o novo valor de optional_version
        if 'optional_email' in optional_terms_accepted:
            new_version = optional_version
            action = "Aceitou optional_email"
            additional_info = f"optional_version atualizado para: {optional_version}"
        else:
            new_version = None
            action = "Removeu optional_email"
            additional_info = "optional_version removido (NULL)"

        # Atualizar a versão dos termos, se necessário
        if current_optional_version != new_version:
            cursor.execute(""" 
                UPDATE user_terms_and_privacy_acceptance
                SET optional_version = %s, accepted_at = CURRENT_TIMESTAMP
                WHERE user_id = %s
            """, (new_version, user_id))
            changes_made = True

            # Registrar log da alteração
            log_event(action, "user_terms_and_privacy_acceptance", user_id, additional_info=additional_info)

        # Adicionar os novos termos aceitos (se houver)
        if terms_to_add:
            for term_id in terms_to_add:
                cursor.execute("""
                    INSERT IGNORE INTO user_optional_terms_acceptance (user_id, optional_term_id, accepted_at)
                    VALUES (%s, %s, CURRENT_TIMESTAMP)
                """, (user_id, term_id))
            changes_made = True

        # Remover os termos desmarcados (se houver)
        if terms_to_remove:
            for term_id in terms_to_remove:
                cursor.execute("""
                    DELETE FROM user_optional_terms_acceptance
                    WHERE user_id = %s AND optional_term_id = %s
                """, (user_id, term_id))
            changes_made = True

        # Registrar evento de log apenas se houver alterações em termos opcionais
        if terms_to_add or terms_to_remove:
            log_event(
                "Atualização de termos",
                "user_optional_terms_acceptance",
                user_id,
                additional_info=f"Termos adicionados: {terms_to_add}, Termos removidos: {terms_to_remove}"
            )

        # Commit das mudanças, somente se houve alterações
        if changes_made:
            mydb.commit()
        return changes_made
    except Exception as e:
        print(f"Erro ao atualizar termos opcionais: {e}")
        mydb.rollback()
        return False

def get_current_optional_terms_ids(mydb):
    """
    Retorna os IDs dos termos opcionais atuais (`is_current = TRUE`).
    """
    try:
        with mydb.cursor(DictCursor) as cursor:
            cursor.execute("USE surveydb")
            cursor.execute("""
                SELECT id
                FROM optional_terms
                WHERE is_current = TRUE
            """)
            return [row['id'] for row in cursor.fetchall()]
    except Exception as e:
        print(f"Erro ao buscar IDs dos termos atuais: {e}")
        return []


def get_user_accepted_optional_terms_ids(mydb, user_id):
    """
    Retorna os IDs dos termos opcionais aceitos pelo usuário.
    """
    try:
        with mydb.cursor(DictCursor) as cursor:
            cursor.execute("USE surveydb")
            cursor.execute("""
                SELECT optional_term_id
                FROM user_optional_terms_acceptance
                WHERE user_id = %s
            """, (user_id,))
            return [row['optional_term_id'] for row in cursor.fetchall()]
    except Exception as e:
        print(f"Erro ao buscar IDs dos termos aceitos pelo usuário: {e}")
        return []

def verify_optional_terms_update(mydb, user_id):
    """
    Verifica se os termos opcionais aceitos pelo usuário estão atualizados.
    Remove os consentimentos de termos que não estão mais em `is_current = TRUE`.
    """
    try:
        # Obter IDs dos termos opcionais atuais
        current_terms_ids = get_current_optional_terms_ids(mydb)
        print(f"IDs dos termos atuais: {current_terms_ids}")

        # Obter IDs dos termos aceitos pelo usuário
        user_accepted_ids = get_user_accepted_optional_terms_ids(mydb, user_id)
        print(f"IDs dos termos aceitos pelo usuário: {user_accepted_ids}")

        updated = False
        was_accepted = bool(user_accepted_ids)

        # Identificar IDs aceitos pelo usuário que não estão mais em `is_current = TRUE`
        outdated_ids = [term_id for term_id in user_accepted_ids if term_id not in current_terms_ids]
        print(f"IDs desatualizados a remover: {outdated_ids}")

        # Resetar consentimentos para termos desatualizados
        if outdated_ids:
            reset_result = reset_user_terms_by_ids(user_id, outdated_ids, mydb)
            updated = reset_result

        return {
            'updated': updated,
            'was_accepted': was_accepted
        }
    except Exception as e:
        print(f"Erro ao verificar termos opcionais: {e}")
        return {
            'updated': False,
            'was_accepted': False
        }

def reset_user_terms_by_ids(user_id, outdated_ids, mydb, reset_global_version=False):
    """
    Remove consentimentos para os termos opcionais desatualizados e,
    opcionalmente, atualiza o campo optional_version na tabela global.
    """
    try:
        with mydb.cursor() as cursor:
            cursor.execute("USE surveydb")

            # Remover consentimentos da tabela user_optional_terms_acceptance
            if outdated_ids:
                cursor.execute("""
                    DELETE FROM user_optional_terms_acceptance
                    WHERE user_id = %s AND optional_term_id IN %s
                """, (user_id, tuple(outdated_ids)))
                log_event(
                    event="Remover consentimento",
                    table="user_optional_terms_acceptance",
                    record_id=user_id,
                    additional_info=f"IDs removidos: {outdated_ids}"
                )
                print(f"Consentimentos removidos para os IDs desatualizados: {outdated_ids}")

            # Atualizar optional_version na tabela user_terms_and_privacy_acceptance, se aplicável
            if reset_global_version:
                cursor.execute("""
                    UPDATE user_terms_and_privacy_acceptance
                    SET optional_version = NULL
                    WHERE user_id = %s
                """, (user_id,))
                log_event(
                    event="Resetar optional_version",
                    table="user_terms_and_privacy_acceptance",
                    record_id=user_id,
                    additional_info="Versão opcional resetada para NULL"
                )
                print("Versão global de optional_version resetada.")

            mydb.commit()
            return True

    except Exception as e:
        print(f"Erro ao redefinir termos opcionais: {e}")
        return False

def remove_local_user_account(user_id, password, mydb):
    with mydb.cursor(cursor=DictCursor) as cursor:
        cursor.execute("USE surveydb")
        cursor.execute("SELECT password FROM user_login WHERE id = %s", (user_id,))
        stored_password = cursor.fetchone()
        
        if stored_password and bcrypt.checkpw(password.encode('utf-8'), stored_password['password'].encode('utf-8')):
            cursor.execute("DELETE FROM user_login WHERE id = %s", (user_id,))
            mydb.commit()
            log_event("Conta de usuário removida", "user_login", user_id)
            add_to_excluded_users(user_id)  # Adiciona o ID à lista de excluídos
            return True
        return False

def remove_google_user_account(user_id, mydb):
    with mydb.cursor(cursor=DictCursor) as cursor:
        cursor.execute("USE surveydb")
        cursor.execute("DELETE FROM user_login WHERE id = %s", (user_id,))
        mydb.commit()
        log_event("Conta de usuário Google removida", "user_login", user_id)
        add_to_excluded_users(user_id)  # Adiciona o ID à lista de excluídos
        return True

def validate_user_password(user_id, password, mydb):
    # Aqui você deve implementar a lógica para verificar a senha do usuário
    with mydb.cursor() as cursor:
        cursor.execute("SELECT password FROM user_login WHERE id = %s", (user_id,))
        user = cursor.fetchone()
        if user and user['password'] == password:
            return True
        return False
