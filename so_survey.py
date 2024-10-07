questions = [
    "Quantos anos você tem?",
    "Com que frequência você faz compras em supermercados? (0 - Não compro, 1 - 1x/mês, 2 - 2x/mês, 3 - 3x/mês, 4 - 4 ou mais x/mês)",
    "Qual a distância do supermercado mais próximo? (0 - 0 a 5km, 1 - 6 a 10km, 2 - 11 a 15km, 3 - 16 a 20km, 4 - acima de 20km)",
    "Quantas pessoas existem na família incluindo você?",
    "Quanto costuma ficar sua compra no supermercado? (0 - R$ 0 a R$ 100, 1 - R$ 101 a R$ 500, 2 - R$ 501 a R$ 1000, 3 - R$ 1001 a R$ 2000, 4 - acima de R$ 2000)",
    "Quanto gasta por mês em mercearia, açougue e sacolão do seu bairro (fora supermercado)? (0 - R$ 0 a R$ 100, 1 - R$ 101 a R$ 500, 2 - R$ 501 a R$ 1000, 3 - R$ 1001 a R$ 2000, 4 - acima de R$ 2000)"
]

def create_survey_response(user_id, mydb):
    mycursor = mydb.cursor()
    mycursor.execute("USE surveydb")

    for question in questions:
        answer = input(question + " ")
        mycursor.execute("""
            INSERT INTO survey_responses (user_id, question, answer)
            VALUES (%s, %s, %s)
        """, (user_id, question, answer))

    mydb.commit()
    print("Respostas da pesquisa registradas com sucesso.")
