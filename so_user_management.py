from so_create_db import connect

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

def list_users(mydb):
    if mydb:
        try:
            role = input("Deseja listar (1) Administradores ou (2) Usuários? (digite 1 ou 2): ").strip()
            role_condition = "role = 'admin'" if role == '1' else "role = 'user'" if role == '2' else None
            
            if role_condition is None:
                print("Opção inválida. Por favor, escolha 1 para Administradores ou 2 para Usuários.")
                return
            
            with mydb.cursor() as cursor:
                cursor.execute(f"SELECT * FROM user_login WHERE {role_condition} ORDER BY id")
                users = cursor.fetchall()
                
                if users:
                    for user in users:
                        print(f"ID: {user['id']}, Email: {user['email']}, Nome: {user['nome']}, "
                              f"Sobrenome: {user['sobrenome']}, Data de Cadastro: {user['data_cadastro']}")
                        cursor.execute("SELECT resposta FROM survey_responses WHERE user_id = %s", (user['id'],))
                        respostas = cursor.fetchall()
                        if respostas:
                            print("Respostas do questionário:")
                            for resposta in respostas:
                                print(f"- {resposta['resposta']}")
                        else:
                            print("Nenhuma resposta do questionário encontrada.")
                        print("---")
                else:
                    print("Nenhum usuário encontrado.")
        except Exception as e:
            print(f"Erro ao listar usuários: {e}")
    else:
        print("Erro ao conectar ao banco de dados.")

def remove_user(email, admin_email, mydb):
    if mydb:
        try:
            with mydb.cursor() as cursor:
                cursor.execute("SELECT * FROM user_login WHERE email = %s", (email,))
                user_to_remove = cursor.fetchone()
                cursor.execute("SELECT * FROM user_login WHERE email = %s", (admin_email,))
                admin_user = cursor.fetchone()

                if user_to_remove:
                    if user_to_remove['role'] == 'admin' and admin_user['is_default_admin'] != True:
                        print("Você não tem permissão para remover um usuário admin.")
                        return
                    
                    print("Dados do usuário a ser removido:")
                    print(f"ID: {user_to_remove['id']}, Email: {user_to_remove['email']}, Nome: {user_to_remove['nome']}, "
                          f"Sobrenome: {user_to_remove['sobrenome']}, Data de Cadastro: {user_to_remove['data_cadastro']}")
                    confirm = input("Tem certeza que deseja remover este usuário? (s/n): ").strip().lower()
                    
                    if confirm == 's':
                        cursor.execute("DELETE FROM user_login WHERE email = %s", (email,))
                        mydb.commit()
                        print("Usuário removido com sucesso.")
                    else:
                        print("Operação cancelada.")
                else:
                    print("Nenhum usuário encontrado com o e-mail fornecido.")
        except Exception as e:
            print(f"Erro ao remover o usuário: {e}")
    else:
        print("Erro ao conectar ao banco de dados.")

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
                        # Validação da senha
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

def main():
    while True:
        print("\nMenu Principal")
        print("1. Criar novo usuário admin")
        print("2. Excluir usuário")
        print("3. Listar usuários")
        print("4. Alterar dados do usuário")
        print("5. Sair")
        choice = input("Escolha uma opção: ")

        if choice == '1':
            nome = input("Nome: ")
            sobrenome = input("Sobrenome: ")
            telefone = input("Telefone (com DDD): ")
            email = input("Email: ")
            password = input("Senha (6 dígitos): ")

            while len(password) != 6 or not password.isdigit():
                print("A senha deve ter exatamente 6 dígitos.")
                password = input("Senha (6 dígitos): ")
            
            create_admin(nome, sobrenome, telefone, email, password)

        elif choice == '2':
            email = input("Digite o email do usuário a ser excluído: ")
            admin_email = input("Digite seu email (admin) para confirmação: ")
            remove_user(email, admin_email)

        elif choice == '3':
            list_users() 

        elif choice == '4':
            email = input("Digite o email do usuário para alterar dados: ")
            update_user(email)

        elif choice == '5':
            print("Saindo...")
            break

        else:
            print("Opção inválida.")

if __name__ == "__main__":
    main()
