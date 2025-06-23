# PETMATCH - Sistema de Adoção de Pets

PETMATCH é uma plataforma web desenvolvida em Flask para conectar pessoas que desejam adotar pets com animais disponíveis para adoção. O sistema oferece uma interface amigável e intuitiva, permitindo que usuários encontrem o pet ideal para adoção e que administradores gerenciem todo o processo.

## Funcionalidades

### Para Usuários
- **Cadastro e Login**: Crie sua conta e faça login para acessar todas as funcionalidades
- **Busca de Pets**: Filtre pets por espécie, porte, sexo e idade
- **Solicitação de Adoção**: Solicite a adoção de pets disponíveis
- **Cancelamento de Pedidos**: Cancele pedidos de adoção pendentes quando desejar
- **Painel do Usuário**: Acompanhe o status de suas solicitações de adoção
- **Perfil Personalizável**: Mantenha seus dados atualizados

### Para Administradores
- **Gerenciamento de Pets**: Adicione, edite e remova pets do sistema
- **Aprovação de Adoções**: Aprove ou rejeite solicitações de adoção
- **Dashboard Administrativo**: Visualize estatísticas e informações importantes
- **Histórico de Adoções**: Acompanhe todas as adoções realizadas com filtros por status

## Tecnologias Utilizadas

- **Backend**: Python 3.11 com Flask
- **Banco de Dados**: SQLite (via SQLAlchemy)
- **Frontend**: HTML5, CSS3, JavaScript
- **Autenticação**: Flask-Login
- **Formulários**: Flask-WTF
- **Validação**: JavaScript para validação em tempo real

## Requisitos

- Python 3.8 ou superior
- pip (gerenciador de pacotes Python)
- Navegador web moderno (Chrome, Firefox, Edge, Safari)

## Instalação

1. Clone o repositório ou extraia o arquivo zip:
   ```
   git clone https://github.com/seu-usuario/petmatch.git
   cd petmatch
   ```

2. Crie e ative um ambiente virtual:
   ```
   # Windows
   python -m venv venv
   venv\Scripts\activate

   # Linux/macOS
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Instale as dependências:
   ```
   pip install -r requirements.txt
   ```
   
4. Configure o flask:
   ```
   set FLASK_APP=src/main.py
   set FLASK_ENV=development
   set FLASK_DEBUG=1
   ```

5. Configure o banco de dados:
   ```
   python -m flask db init
   python -m flask db migrate -m "Estrutura inicial"
   python -m flask db upgrade
   ```

6. Popule o banco com dados iniciais:
   ```
   python -m flask seed
   ```

7. Execute a aplicação:
   ```
   python -m flask run
   ```

8. Acesse a aplicação em seu navegador:
   ```
   http://127.0.0.1:5000
   ```

## Credenciais de Administrador

Para acessar o painel administrativo, use as seguintes credenciais:

- **Email**: admin@petmatch.com
- **Senha**: admin123

## Estrutura do Projeto

```
petmatch/
├── src/
│   ├── app/
│   │   ├── admin/         # Rotas e templates administrativos
│   │   ├── adoptions/     # Lógica de adoções
│   │   ├── auth/          # Autenticação e registro
│   │   ├── main/          # Rotas principais
│   │   ├── pets/          # Gerenciamento de pets
│   │   ├── static/        # Arquivos estáticos (CSS, JS, imagens)
│   │   ├── templates/     # Templates HTML
│   │   ├── utils/         # Utilitários
│   │   ├── __init__.py    # Inicialização da aplicação
│   │   └── models.py      # Modelos de dados
│   ├── config.py          # Configurações
│   └── main.py            # Ponto de entrada
├── requirements.txt       # Dependências
└── README.md              # Este arquivo
```

## Fluxo de Adoção

1. Usuário se registra e faz login
2. Usuário navega pelos pets disponíveis
3. Usuário solicita a adoção de um pet
4. O pet passa para o status "em processo"
5. O usuário pode cancelar o pedido enquanto estiver pendente
6. Administrador recebe a solicitação
7. Administrador aprova ou rejeita a solicitação
8. Se aprovada, o pet passa para o status "adotado"
9. Se rejeitada ou cancelada, o pet volta para o status "disponível"
10. Usuário acompanha o status do pedido em seu painel

## CRUD Completo

### CRUD de Pets (Admin)
- **Create**: Adicionar novos pets ao sistema
- **Read**: Visualizar lista de pets e detalhes individuais
- **Update**: Editar informações de pets existentes
- **Delete**: Remover pets do sistema (apenas se não estiverem em processo de adoção)

### CRUD de Adoções (Cliente)
- **Create**: Solicitar adoção de pets disponíveis
- **Read**: Visualizar histórico e status de pedidos
- **Update**: Não aplicável
- **Delete**: Cancelar pedidos pendentes

### CRUD de Adoções (Admin)
- **Read**: Visualizar todos os pedidos pendentes e histórico completo
- **Update**: Aprovar ou rejeitar pedidos de adoção
- **Delete**: Não aplicável (histórico é preservado)

## Customização da Interface

O sistema utiliza uma paleta de cores em tons pastéis de azul, com a fonte "Sour Gummy" para títulos e "Nunito Sans" para textos. A interface é totalmente responsiva e adaptável a diferentes tamanhos de tela.

## Contribuição

Contribuições são bem-vindas! Sinta-se à vontade para abrir issues ou enviar pull requests.

## Licença

Este projeto é licenciado sob a licença MIT - veja o arquivo LICENSE para mais detalhes.

## Contato

Para mais informações, entre em contato através do email: contato@petmatch.com
