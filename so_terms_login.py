from so_create_db import connect

tunnel, mydb = connect()

try:
    mycursor = mydb.cursor()
    mycursor.execute("CREATE DATABASE IF NOT EXISTS surveydb;")
    mycursor.execute("USE surveydb")

    # Tabela para Termos de Uso
    mycursor.execute("DROP TABLE IF EXISTS terms;")
    mycursor.execute("""
        CREATE TABLE terms (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            accept_mandatory BOOLEAN NOT NULL,
            accept_optional BOOLEAN NOT NULL
        );
    """)

    # Tabela para Respostas da Pesquisa
    mycursor.execute("DROP TABLE IF EXISTS survey_responses;")
    mycursor.execute("""
        CREATE TABLE survey_responses (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            question VARCHAR(255),
            answer VARCHAR(255)
        );
    """)

    print("Tabelas criadas com sucesso.")
    
    mydb.commit()
    mycursor.close()
    mydb.close()

finally:
    tunnel.stop()
