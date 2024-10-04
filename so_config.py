config = {
    'ssh': {
        'host': 'xxx.xxx.xxx.xxx',  # Seu host VM aqui
        'port': 0000,               # Sua porta VM aqui
        'username': 'xxxxxx',       # Seu usuário VM padrão
        'password': 'xxxxx',        # Senha
        'remote_bind_address': ('xxx.x.x.x', 0000) # Host e Porta Mysql no VM
    },
    'mysql': {
        'host': 'xxx.x.x.x',        # Host do usuário local VM
        'user': 'xxxxxx',           # Usuário do Banco de Dados
        'password': 'xxxx',         # Senha do Usuário no BD
        'port': None                # Vamos adicionar a porta depois de estabelecermos a conexão SSH no arquivo "so_create_db.py"
    }
}