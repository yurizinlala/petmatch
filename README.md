# PETMATCH - Plataforma de Adoção de Pets

[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-2.x-orange.svg)](https://flask.palletsprojects.com/)
[![SQLite](https://img.shields.io/badge/Database-SQLite-lightgrey.svg)](https://www.sqlite.org/)

## 🐾 Sobre o Projeto

PETMATCH é uma plataforma web desenvolvida como projeto para a disciplina de Práticas de Programação na Universidade do Estado do Rio Grande do Norte (UERN). O objetivo é conectar animais disponíveis para adoção (cães e gatos) com pessoas interessadas, facilitando o processo de encontrar um novo lar para os pets.

O sistema permite o cadastro de animais, a busca por filtros específicos, o registro de adotantes e um fluxo simplificado para solicitação e aprovação de adoções, além de um painel administrativo para gerenciamento.

**Status:** Em andamento.
**Link para o vídeo:** https://youtu.be/bIuTHvS6QOU

## ✨ Funcionalidades Principais

*   **Cadastro e Login de Usuários:** Adotantes podem criar contas e fazer login de forma segura.
*   **Gerenciamento de Pets (Admin):** Administradores podem adicionar, editar, visualizar e remover pets, incluindo upload de fotos.
*   **Listagem e Filtros:** Visualização pública de pets disponíveis com filtros por espécie, raça, idade, porte e sexo.
*   **Detalhes do Pet:** Página individual para cada pet com informações completas e botão para solicitar adoção.
*   **Fluxo de Adoção:**
    *   Adotantes logados podem solicitar a adoção.
    *   Administradores gerenciam os pedidos (aprovar/rejeitar).
    *   Adotantes acompanham o status dos seus pedidos.
*   **Painel do Administrador:** Área para gerenciar pets, pedidos de adoção e visualizar relatórios básicos.
*   **Relatórios:** Exportação de dados de adoções em formato CSV.
*   **Dados Iniciais:** O sistema inicia com alguns pets pré-cadastrados para demonstração.

## 🛠️ Tecnologias Utilizadas

*   **Backend:** Python 3.11, Flask
*   **Banco de Dados:** SQLite
*   **ORM / Migrations:** Flask-SQLAlchemy, Flask-Migrate
*   **Frontend:** HTML5, CSS3, Jinja2 (Template Engine)
*   **Formulários:** Flask-WTF
*   **Autenticação:** Werkzeug (Hashing), Flask-Login (Sessão)
*   **Design:** CSS customizado, Google Fonts ("Sour Gummy")

## 🚀 Como Executar Localmente

Siga os passos abaixo para configurar e rodar o projeto em sua máquina:

1.  **Clone o Repositório (ou extraia o ZIP):**
    ```bash
    # Se estiver usando Git
    git clone https://github.com/seu-usuario/petmatch.git
    cd petmatch
    ```
    *Se você baixou o ZIP, apenas extraia e navegue até a pasta `petmatch` pelo terminal.*

2.  **Crie e Ative um Ambiente Virtual (Recomendado):**
    ```bash
    # Criar ambiente virtual
    python -m venv venv

    # Ativar no Windows (cmd/powershell)
    .\venv\Scripts\activate

    # Ativar no Linux/macOS
    source venv/bin/activate
    ```

3.  **Instale as Dependências:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure as Variáveis de Ambiente do Flask:**
    *   **No Windows (cmd):**
        ```cmd
        set FLASK_APP=src/main.py
        set FLASK_ENV=development
        set FLASK_DEBUG=1
        ```
    *   **No Windows (PowerShell):**
        ```powershell
        $env:FLASK_APP = "src/main.py"
        $env:FLASK_ENV = "development"
        $env:FLASK_DEBUG = "1"
        ```
    *   **No Linux/macOS:**
        ```bash
        export FLASK_APP=src/main.py
        export FLASK_ENV=development
        export FLASK_DEBUG=1
        ```

5.  **Inicialize e Atualize o Banco de Dados:**
    *(Execute estes comandos apenas na primeira vez ou quando houver mudanças no modelo de dados)*
    ```bash
    flask db init
    flask db migrate -m "Initial migration"
    flask db upgrade
    ```
    *Isso criará o arquivo `app.db` dentro da pasta `src` e as tabelas necessárias.*

6.  **Execute a Aplicação:**
    ```bash
    flask run
    ```

7.  **Acesse no Navegador:**
    Abra seu navegador e acesse: `http://127.0.0.1:5000`

## 📖 Uso Básico

*   **Visitante:** Navegue pela lista de pets, use os filtros e veja os detalhes.
*   **Adotante:** Crie uma conta, faça login, navegue pelos pets, solicite adoção e veja o histórico de seus pedidos no painel.
*   **Administrador:** Faça login com uma conta admin (a primeira conta criada pode ser definida como admin manualmente no banco de dados ou via um script futuro), acesse o painel de administração para gerenciar pets, aprovar/rejeitar adoções e gerar relatórios.

## 👥 Equipe

*   Jefferson da Silva Melo
*   Yuri Dantas da Silva

---

*Este projeto foi desenvolvido com o auxílio da IA Manus.*
