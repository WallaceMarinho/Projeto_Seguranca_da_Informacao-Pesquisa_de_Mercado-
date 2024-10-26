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
                                   is_default_admin)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """, (
                        os.getenv("ADMIN_NAME"),
                        os.getenv("ADMIN_LAST_NAME"),
                        os.getenv("ADMIN_PHONE"),
                        os.getenv("ADMIN_EMAIL"),
                        os.getenv("ADMIN_PASSWORD"),
                        os.getenv("ADMIN_BAIRRO"),
                        'admin',
                        True
                    ))
                    mydb.commit()

                    admin_id = cursor.lastrowid

                    cursor.execute(""" 
                        SELECT version FROM terms_and_privacy_policy 
                        WHERE version = '0000'
                    """)
                    existing_terms = cursor.fetchone()

                    if not existing_terms:
                        version = '0000'
                    else:
                        cursor.execute(""" 
                            UPDATE terms_and_privacy_policy SET is_current = FALSE 
                            WHERE is_current = TRUE
                        """)
                        mydb.commit()

                        cursor.execute(""" 
                            SELECT MAX(CAST(version AS UNSIGNED)) FROM terms_and_privacy_policy
                        """)
                        max_version = cursor.fetchone()[0]
                        version = str(int(max_version) + 1).zfill(4)

                    terms_content = "Você ainda não possui uma versão de termo obrigatório no banco de dados."
                    optional_content = "Você ainda não possui uma versão de termo opcional no banco de dados."
                    privacy_content = "Você ainda não possui uma versão de política de privacidade no banco de dados."

                    cursor.execute(""" 
                        INSERT INTO terms_and_privacy_policy (version, content, type, is_current) 
                        VALUES (%s, %s, 'terms', TRUE), 
                               (%s, %s, 'optional', TRUE), 
                               (%s, %s, 'privacy', TRUE)
                    """, (version, terms_content, version, optional_content, version, privacy_content))
                    mydb.commit()

                    cursor.execute(""" 
                        INSERT INTO user_terms_and_privacy_acceptance (
                                   user_id,
                                   terms_version,
                                   privacy_version,
                                   optional_version)
                        VALUES (%s, %s, %s, %s)
                    """, (admin_id, version, version, version))
                    mydb.commit()

                    print(f"Admin padrão criado e termos/políticas (versão {version}) criados com sucesso.")
                else:
                    print("O admin padrão já existe.")
        except Exception as e:
            print(f"Erro ao criar admin padrão: {e}")
    else:
        print("Erro ao conectar ao banco de dados.")
