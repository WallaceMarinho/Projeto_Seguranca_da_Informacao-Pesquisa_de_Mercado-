from so_create_db import connect

def accept_terms(user_id):
    tunnel, mydb = connect()
    try:
        mycursor = mydb.cursor()
        mycursor.execute("USE surveydb")

        # Aceitação de termos obrigatórios e opcionais
        accept_mandatory = input("Aceita os termos obrigatórios? (sim/nao): ").lower() == 'sim'
        accept_optional = input("Aceita os termos opcionais? (sim/nao): ").lower() == 'sim'

        mycursor.execute("""
            INSERT INTO terms (user_id, accept_mandatory, accept_optional)
            VALUES (%s, %s, %s)
        """, (user_id, accept_mandatory, accept_optional))

        mydb.commit()
        print("Termos de uso aceitos com sucesso.")
    
    finally:
        mycursor.close()
        mydb.close()
        tunnel.stop()

def create_survey_response(user_id):
    tunnel, mydb = connect()
    try:
        mycursor = mydb.cursor()
        mycursor.execute("USE surveydb")

        # Perguntas de Pesquisa de Mercado
        questions = [
            "Qual a sua faixa etária?",
            "Com que frequência você faz compras em supermercados?",
            "Qual a distância do supermercado mais próximo?",
            "Quanto você gasta mensalmente com supermercado?",
            "Quais produtos você mais compra?"
        ]

        for question in questions:
            answer = input(question + " ")
            mycursor.execute("""
                INSERT INTO survey_responses (user_id, question, answer)
                VALUES (%s, %s, %s)
            """, (user_id, question, answer))

        mydb.commit()
        print("Respostas da pesquisa registradas com sucesso.")
    
    finally:
        mycursor.close()
        mydb.close()
        tunnel.stop()

def read_survey_responses(user_id):
    tunnel, mydb = connect()
    try:
        mycursor = mydb.cursor()
        mycursor.execute("USE surveydb")

        mycursor.execute("SELECT question, answer FROM survey_responses WHERE user_id = %s", (user_id,))
        responses = mycursor.fetchall()
        print("Respostas do usuário %s:" % user_id)
        for question, answer in responses:
            print("Pergunta: %s | Resposta: %s" % (question, answer))
    
    finally:
        mycursor.close()
        mydb.close()
        tunnel.stop()

def update_survey_response(user_id):
    tunnel, mydb = connect()
    try:
        mycursor = mydb.cursor()
        mycursor.execute("USE surveydb")

        question = input("Qual pergunta você deseja alterar a resposta? ")
        new_answer = input("Nova resposta: ")

        mycursor.execute("""
            UPDATE survey_responses 
            SET answer = %s 
            WHERE user_id = %s AND question = %s
        """, (new_answer, user_id, question))

        mydb.commit()
        print("Resposta atualizada com sucesso.")
    
    finally:
        mycursor.close()
        mydb.close()
        tunnel.stop()

def delete_survey_response(user_id):
    tunnel, mydb = connect()
    try:
        mycursor = mydb.cursor()
        mycursor.execute("USE surveydb")

        question = input("Qual pergunta você deseja deletar a resposta? ")

        mycursor.execute("""
            DELETE FROM survey_responses 
            WHERE user_id = %s AND question = %s
        """, (user_id, question))

        mydb.commit()
        print("Resposta deletada com sucesso.")
    
    finally:
        mycursor.close()
        mydb.close()
        tunnel.stop()

# Exemplo de uso
if __name__ == "__main__":
    user_id = int(input("Insira seu ID de usuário: "))

    # Aceitar termos
    accept_terms(user_id)

    # Responder pesquisa
    create_survey_response(user_id)

    # Operações CRUD
    opcao = input("Deseja [ler] suas respostas, [atualizar], ou [deletar]? ").lower()

    if opcao == 'ler':
        read_survey_responses(user_id)
    elif opcao == 'atualizar':
        update_survey_response(user_id)
    elif opcao == 'deletar':
        delete_survey_response(user_id)
