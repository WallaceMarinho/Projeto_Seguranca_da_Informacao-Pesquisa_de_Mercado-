from so_survey import questions

def view_user_data(user_id, mydb):
    cursor = mydb.cursor()
    cursor.execute("USE surveydb")
    cursor.execute("SELECT nome, sobrenome, telefone, email, bairro FROM user_login WHERE id = %s", (user_id,))
    row = cursor.fetchone()

    if row:
        print("\n----- Seus Dados Pessoais -----")
        print(f"Nome: {row['nome']}")
        print(f"Sobrenome: {row['sobrenome']}")
        print(f"Telefone: {row['telefone']}")
        print(f"Email: {row['email']}")
        print(f"Bairro: {row['bairro']}")
    else:
        print("Usuário não encontrado.")

def edit_user_data(user_id, mydb):
    cursor = mydb.cursor()
    cursor.execute("USE surveydb")
    print("Edite seus dados pessoais (deixe em branco para manter):")
    nome = input("Nome: ").strip()
    sobrenome = input("Sobrenome: ").strip()
    telefone = input("Telefone: ").strip()
    senha = input("Nova Senha (6 dígitos): ").strip()

    if senha and (len(senha) != 6 or not senha.isdigit()):
        print("A senha deve ter exatamente 6 dígitos.")
        return

    if nome:
        cursor.execute("UPDATE user_login SET nome = %s WHERE id = %s", (nome, user_id))
    if sobrenome:
        cursor.execute("UPDATE user_login SET sobrenome = %s WHERE id = %s", (sobrenome, user_id))
    if telefone:
        cursor.execute("UPDATE user_login SET telefone = %s WHERE id = %s", (telefone, user_id))
    if senha:
        cursor.execute("UPDATE user_login SET password = %s WHERE id = %s", (senha, user_id))

    mydb.commit()
    print("Dados pessoais atualizados com sucesso.")

def read_survey_responses(user_id, mydb):
    cursor = mydb.cursor()
    cursor.execute("USE surveydb")

    cursor.execute("SELECT question, answer FROM survey_responses WHERE user_id = %s", (user_id,))
    responses = cursor.fetchall()

    if responses:
        print(f"Respostas do usuário {user_id}:")
        for response in responses:
            print(f"Pergunta: {response['question']} | Resposta: {response['answer']}")
    else:
        print(f"Sem respostas para o usuário {user_id}.")

def edit_survey_responses(user_id, mydb):
    cursor = mydb.cursor()
    cursor.execute("USE surveydb")

    for question in questions:
        answer = input(question + " (deixe em branco para manter resposta anterior): ")
        if answer:
            cursor.execute("UPDATE survey_responses SET answer = %s WHERE user_id = %s AND question = %s", (answer, user_id, question))

    mydb.commit()
    print("Respostas do questionário atualizadas com sucesso.")

def user_menu(user_id, mydb):
    while True:
        option = input("Deseja:\n[ver] dados pessoais\n[editar] dados pessoais\n[ler] questionario\n[editar_questionario]\n[voltar]?: ").strip().lower()
        if option == 'ver':
            view_user_data(user_id, mydb)
        elif option == 'editar':
            edit_user_data(user_id, mydb)
        elif option == 'ler':
            read_survey_responses(user_id, mydb)
        elif option == 'editar_questionario':
            edit_survey_responses(user_id, mydb)
        elif option == 'voltar':
            break
        else:
            print("Opção inválida. Tente novamente.")
