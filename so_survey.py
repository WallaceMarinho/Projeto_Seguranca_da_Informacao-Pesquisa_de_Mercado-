from flask import render_template, request, redirect, session, url_for
from db_connection import mydb

questions = [
    "Quantos anos você tem?",
    "Com que frequência você faz compras em supermercados?",
    "Qual a distância do supermercado mais próximo?",
    "Quantas pessoas existem na família incluindo você?",
    "Quanto costuma ficar sua compra no supermercado?",
    "Quanto gasta por mês em mercearia, açougue e sacolão do seu bairro (fora supermercado)?"
]

response_options = {
    1: [],
    2: [
        "0 - Não compro",
        "1 - 1x/mês",
        "2 - 2x/mês",
        "3 - 3x/mês",
        "4 - 4 ou mais x/mês"
    ],
    3: [
        "0 - 0 a 5km",
        "1 - 6 a 10km",
        "2 - 11 a 15km",
        "3 - 16 a 20km",
        "4 - acima de 20km"
    ],
    4: [],
    5: [
        "0 - R$ 0 a R$ 100",
        "1 - R$ 101 a R$ 500",
        "2 - R$ 501 a R$ 1000",
        "3 - R$ 1001 a R$ 2000",
        "4 - acima de R$ 2000"
    ],
    6: [
        "0 - R$ 0 a R$ 100",
        "1 - R$ 101 a R$ 500",
        "2 - R$ 501 a R$ 1000",
        "3 - R$ 1001 a R$ 2000",
        "4 - acima de R$ 2000"
    ]
}

def survey(user_id):
    if has_saved_survey(user_id, mydb):
        return redirect(url_for('app_routes.user_menu_route'))
    else:
        return get_survey(user_id)

def get_survey(user_id):
    return render_template('questions.html', user_id=user_id, questions=questions, response_options=response_options)

def submit_survey(user_id):
    data = request.form
    create_survey_response(user_id, mydb, data)
    session.pop('registering', None)
    return redirect(url_for('app_routes.thank_you', user_id=user_id))

def create_survey_response(user_id, mydb, data):
    mycursor = mydb.cursor()
    mycursor.execute("USE surveydb")

    try:
        for i, question in enumerate(questions):
            answer = data.get(f'question{i+1}', '')

            if i == 0 or i == 3:
                try:
                    answer = int(answer)
                except ValueError:
                    answer = None
                    print(f"Resposta inválida para a pergunta {i+1}")

            if not answer:
                raise ValueError(f"Erro: todas as perguntas devem ser respondidas.")

            mycursor.execute("""
                INSERT INTO survey_responses (user_id, question, answer)
                VALUES (%s, %s, %s)
            """, (user_id, question, answer))

        mydb.commit()
        print("Respostas da pesquisa registradas com sucesso.")

    except Exception as e:
        print(f"Erro ao salvar as respostas: {e}")
        mydb.rollback()

    finally:
        mycursor.close()

def edit_survey_responses(user_id):
    user_responses = read_survey_responses(user_id, mydb)

    return render_template(
        'user_menu.html',
        user_id=user_id,
        questions=questions,
        response_options=response_options,
        user_responses=user_responses
    )

def update_survey_responses(user_id, mydb, data):
    cursor = mydb.cursor()
    cursor.execute("USE surveydb")

    try:
        for i, question in enumerate(questions):
            answer = data.get(f'question{i+1}')
            if i == 0 or i == 3:
                answer = int(answer) if answer else None

            cursor.execute(""" 
                UPDATE survey_responses 
                SET answer = %s 
                WHERE user_id = %s AND question = %s
            """, (answer, user_id, question))

        mydb.commit()
        print("Respostas do questionário atualizadas com sucesso.")

    except Exception as e:
        print(f"Erro ao atualizar as respostas: {e}")
        mydb.rollback()

    finally:
        cursor.close()

def read_survey_responses(user_id, mydb):
    cursor = mydb.cursor()
    cursor.execute("USE surveydb")
    query = "SELECT question, answer FROM survey_responses WHERE user_id = %s"
    cursor.execute(query, (user_id,))
    user_responses = cursor.fetchall()
    return user_responses

def has_saved_survey(user_id, mydb):
    cursor = mydb.cursor()
    query = "SELECT COUNT(*) as total FROM survey_responses WHERE user_id = %s"
    cursor.execute(query, (user_id,))
    
    try:
        result = cursor.fetchone()
        if result is None:
            return False
        count = result['total']
        return count > 0
    except Exception as e:
        print("Error fetching data:", e)
        return False
    finally:
        cursor.close()
