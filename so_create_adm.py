import os

def create_default_admin(mydb):
    if mydb:
        try:
            with mydb.cursor() as cursor:
                cursor.execute("USE surveydb")
                cursor.execute("""
                    SELECT * FROM user_login 
                    WHERE email = %s AND role = 'admin' AND is_default_admin = TRUE
                """, (os.getenv("ADMIN_EMAIL"),))
                existing_admin = cursor.fetchone()

                if not existing_admin:
                    cursor.execute("""
                        INSERT INTO user_login (
                                   nome,
                                   sobrenome,
                                   telefone,
                                   email,
                                   password,
                                   bairro,
                                   role,
                                   is_default_admin,
                                   terms_mandatory_accepted,
                                   terms_optional_accepted)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (
                        os.getenv("ADMIN_NAME"),
                        os.getenv("ADMIN_LAST_NAME"),
                        os.getenv("ADMIN_PHONE"),
                        os.getenv("ADMIN_EMAIL"),
                        os.getenv("ADMIN_PASSWORD"),
                        os.getenv("ADMIN_BAIRRO"),
                        os.getenv("ADMIN_ROLE"),
                        True,
                        True,
                        True
                    ))
                    mydb.commit()
                    print("Admin padrão criado com sucesso.")
                else:
                    print("O admin padrão já existe.")
        except Exception as e:
            print(f"Erro ao criar admin padrão: {e}")
    else:
        print("Erro ao conectar ao banco de dados.")
