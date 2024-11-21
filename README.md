# Tecnologias Utilizadas

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![Nginx](https://img.shields.io/badge/Nginx-269539?style=for-the-badge&logo=nginx&logoColor=white)
![Redis](https://img.shields.io/badge/Redis-DC382D?style=for-the-badge&logo=redis&logoColor=white)
![AWS](https://img.shields.io/badge/AWS-232F3E?style=for-the-badge&logo=amazon-aws&logoColor=white)
![MariaDB](https://img.shields.io/badge/MariaDB-003545?style=for-the-badge&logo=mariadb&logoColor=white)
![VirtualBox](https://img.shields.io/badge/VirtualBox-183A61?style=for-the-badge&logo=virtualbox&logoColor=white)
![OpenVPN](https://img.shields.io/badge/OpenVPN-EA7E20?style=for-the-badge&logo=openvpn&logoColor=white)

---

## Introdução

Este projeto foi desenvolvido utilizando **Python** com o framework **Flask** e aborda a simulação de uma pesquisa de mercado para avaliar a viabilidade da abertura de um novo comércio em uma cidade. A aplicação permite que usuários criem uma conta, realizem login e respondam a um questionário com perguntas como: faixa salarial, quantidade de moradores no domicílio, frequência de compras no supermercado, valor médio das compras mensais, entre outras. O objetivo é coletar dados que auxiliem na análise de perfil dos consumidores da região.

Além da aplicação em si, o projeto também explora conceitos de **infraestrutura de redes** e **orquestração de serviços**. O código-fonte é executado em três máquinas virtuais locais, criadas no **VirtualBox**, que se comunicam com o banco de dados hospedado em uma instância **AWS EC2**. O banco de dados utiliza **MariaDB**, e a comunicação entre as instâncias é feita via **SSH**.

### A arquitetura do projeto inclui:

- **Balanceamento de carga:** Uma das VMs locais utiliza o **Nginx** para distribuir as requisições HTTP entre os servidores de aplicação nas outras duas VMs. Esse balanceamento é implementado por meio de containers gerenciados com **Docker**, onde o Nginx opera como um microserviço.
  
- **Segurança:** A VM responsável pelo balanceamento de carga estabelece um túnel VPN usando **OpenVPN**, garantindo uma camada adicional de segurança na comunicação entre as VMs locais e o banco de dados remoto.

Essa estrutura não apenas ilustra os conceitos de desenvolvimento de aplicações web, mas também foca em práticas modernas de **deploy**, **segurança** e **escalabilidade**, utilizando ferramentas como **Redis**, **Nginx**, **Docker** e **AWS**. Logo abaixo, é apresentado  a topologia da infraesturura do projeto para um melhor entendimento:

![Topologia_redes](docs_img/topologia_redes.PNG)


# Rodando o Projeto

## Passo 1: Configurações da Instância na AWS

Para começar, acesse o serviço **EC2** da AWS com sua conta. Em seguida, crie uma nova instância do tipo **Ubuntu**, que será o ambiente onde seu banco de dados estará hospedado.

- **Gerando o Par de Chaves RSA:** Durante a criação da instância, será solicitado que você crie um par de chaves RSA. Esse par de chaves é essencial para realizar a conexão via **SSH** com a instância. Guarde o arquivo gerado em um diretório seguro na sua máquina local e **renomeie a extensão do arquivo para `.pem`** para garantir que ele esteja no formato correto para a autenticação.

- **Fixando o IP Público com IP Elástico:** Após criar a instância, vá até a seção **IP Elásticos**, localizada na área de **Redes e Segurança** no menu à esquerda. Crie um novo IP elástico e associe-o à sua instância. Isso é muito importante, pois, sem o IP elástico, o IP público da sua instância mudaria toda vez que a máquina fosse reiniciada, o que poderia gerar problemas no código e na configuração de rede.

- **Configurando os Grupos de Segurança:** Agora, acesse a seção **Security Groups** e edite o grupo de segurança associado à sua instância. Libere a **porta 22** para permitir a conexão SSH, o que será necessário para acessar a instância via terminal **CMD** do Windows ou para estabelecer a comunicação entre as suas VMs locais e a instância na AWS. Além da porta 22, também será necessário liberar outras portas que são essenciais para o funcionamento do projeto, conforme a imagem abaixo:

![Portas AWS](docs_img/portas_aws.PNG)

### 1.2 - Instalação do MariaDB e Redis

Após as configurações iniciais, abra o terminal no Windows, entre no diretório onde a sua chave `.pem` está armazenada e acesse a sua instância AWS via SSH com o seguinte comando:

```bash
ssh -i <chave.pem> ubuntu@<ip público da vm>
```

Agora que você está dentro da VM, vamos realizar algumas configurações e instalar os serviços necessários. Para garantir que o usuário ubuntu tenha permissões para executar comandos administrativos dentro da VM, será necessário adicioná-lo ao grupo de sudoers. Execute o seguinte comando no terminal da sua VM:

```bash
sudo usermod -aG sudo ubuntu
```

Esse comando adiciona o usuário ubuntu ao grupo sudo, permitindo-lhe usar comandos com permissões de superusuário.

Agora, vamos instalar o banco de dados MariaDB. No terminal da sua VM, execute os seguintes comandos:

#### Atualize a lista de pacotes
```bash
sudo apt-get update
```

#### Instale o MariaDB
```bash
sudo apt-get install mariadb-server -y
```

#### Após a instalação, inicie o serviço do MariaDB:
```bash
sudo systemctl start mariadb
```

#### Verifique se o MariaDB está em execução com o comando:
```bash
sudo systemctl status mariadb
```

Após instalar o MariaDB, vamos acessar o banco de dados e criar um usuário padrão com todos os privilégios. Execute os seguintes comandos:
```bash
sudo mysql
```

##### Crie um novo usuário e conceda privilégios
```bash
CREATE USER 'usuario_padrão'@'localhost' IDENTIFIED BY 'senha_do_usuario';
GRANT ALL PRIVILEGES ON *.* TO 'usuario_padrão'@'localhost' WITH GRANT OPTION;
```

#### Saia do MariaDB
```bash
EXIT;
```

Esses comandos criam um usuário usuario_padrão com a senha senha_do_usuario e concedem a ele todos os privilégios no banco de dados.

Por fim, vamos instalar o Redis, que será utilizado para armazenar dados temporários, como informações de login dos usuários. Execute os seguintes comandos:
#### Instale o Redis
```bash
sudo apt-get install redis-server -y
```

#### Inicie o Redis
```bash
sudo systemctl start redis
```
#### Verifique se o Redis está em execução
```bash
sudo systemctl status redis
```

Com esses comandos, o servidor Redis será instalado e iniciado. Você pode verificar o status para garantir que está funcionando corretamente.


