from pymysql.cursors import DictCursor

def is_admin(user_id, mydb):
    if mydb:
        with mydb.cursor() as cursor:
            cursor.execute("USE surveydb")
            cursor.execute("SELECT role FROM user_login WHERE id = %s", (user_id))
            user = cursor.fetchone()
        return user and user['role'] == 'admin'
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

def update_terms_policy(mydb, type, content):
    if mydb:
        try:
            with mydb.cursor() as cursor:
                cursor.execute("USE surveydb")
                if type == 'terms':
                    cursor.execute("UPDATE policies SET terms_content = %s, terms_version = terms_version + 1", (content,))
                elif type == 'privacy':
                    cursor.execute("UPDATE policies SET privacy_content = %s, privacy_version = privacy_version + 1", (content,))
                else:
                    print("Tipo inválido. Escolha 'terms' ou 'privacy'.")
                    return
                mydb.commit()
                print("Política/Termo atualizado com sucesso.")
        except Exception as e:
            print(f"Erro ao atualizar política/termos: {e}")

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
                cursor.execute(f"SELECT * FROM user_login WHERE {role_condition} ORDER BY id")
                users = cursor.fetchall() or []

                if users:
                    for user in users:
                        print(f"ID: {user['id']}, Email: {user['email']}, Nome: {user['nome']}, "
                              f"Sobrenome: {user['sobrenome']}, Data de Cadastro: {user['data_cadastro']}")

                        cursor.execute("SELECT resposta FROM survey_responses WHERE user_id = %s", (user['id'],))
                        respostas = cursor.fetchall() or []
                        if respostas:
                            print("Respostas do questionário:")
                            for resposta in respostas:
                                print(f"- {resposta['resposta']}")
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

def update_user(email, mydb):
    if mydb:
        try:
            with mydb.cursor() as cursor:
                cursor.execute("SELECT * FROM user_login WHERE email = %s", (email,))
                user = cursor.fetchone()

                if user:
                    print("Dados do usuário:")
                    print(f"ID: {user['id']}, Email: {user['email']}, Nome: {user['nome']}, "
                          f"Sobrenome: {user['sobrenome']}, Telefone: {user['telefone']}")
                    
                    nome = input("Novo Nome (deixe em branco para não alterar): ") or user['nome']
                    sobrenome = input("Novo Sobrenome (deixe em branco para não alterar): ") or user['sobrenome']
                    telefone = input("Novo Telefone (deixe em branco para não alterar): ") or user['telefone']
                    password = input("Nova Senha (deixe em branco para não alterar): ")

                    if password:
                        while len(password) != 6 or not password.isdigit():
                            print("A senha deve ter exatamente 6 dígitos.")
                            password = input("Nova Senha (6 dígitos): ")

                    update_query = """
                        UPDATE user_login 
                        SET nome = %s, sobrenome = %s, telefone = %s, 
                        password = %s WHERE email = %s
                    """
                    cursor.execute(update_query, (nome, sobrenome, telefone, password if password else user['password'], email))
                    mydb.commit()
                    print("Dados do usuário atualizados com sucesso.")
                else:
                    print("Nenhum usuário encontrado com o e-mail fornecido.")
        except Exception as e:
            print(f"Erro ao atualizar dados do usuário: {e}")
    else:
        print("Erro ao conectar ao banco de dados.")

def remove_user_by_id(user_id, admin_email, mydb):
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
                    
                    print("Dados do usuário a ser removido:")
                    print(f"ID: {user_to_remove['id']}, Email: {user_to_remove['email']}, Nome: {user_to_remove['nome']}, "
                          f"Sobrenome: {user_to_remove['sobrenome']}, Data de Cadastro: {user_to_remove['data_cadastro']}")
                    
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
