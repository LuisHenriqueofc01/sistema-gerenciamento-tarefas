# 📋 Sistema de Gerenciamento de Tarefas

Sistema web desenvolvido em Flask com foco na criação e gerenciamento de processos e tarefas. A interface inclui um painel Kanban dinâmico, modelo de processos reutilizáveis, sistema de autenticação de usuários e funcionalidades administrativas.

## 🛠 Tecnologias Utilizadas

- Python 3.x  
- Flask  
- SQLite  
- SQLAlchemy  
- Flask-Login  
- Bootstrap 5  
- JavaScript (Fetch API, DOM)  
- HTML5 e Jinja2  

## 📌 Funcionalidades

- ✅ **Autenticação de usuários** (login, logout, alteração de senha)  
- 🧑‍💼 **Painel de administrador** (criação de usuários)  
- 📁 **Criação de modelos de processo** com múltiplas tarefas  
- ⚙️ **Instanciação de processos** a partir de modelos  
- 📌 **Kanban com tarefas em andamento, concluídas e pendentes**  
- 🔔 **Notificações automáticas de tarefas vencidas**  
- 🗓 **Datas de início e fim para tarefas e processos**  
- 📉 **Tarefas concluídas somem após o mês vigente**  
- 🚨 **Tarefas atrasadas em destaque**

## 📷 Interface

> Você pode inserir imagens da interface no diretório `static/assets/` e referenciar aqui com `![descrição](caminho)`.

## 🧭 Estrutura de Pastas

sistema-gerenciamento-tarefas/
├── app/
│ ├── static/
│ ├── templates/
│ ├── models/
│ ├── routes/
│ ├── init.py
│ └── ...
├── migrations/
├── venv/
├── config.py
├── requirements.txt
└── run.py

## ▶️ Como Executar Localmente
1. Clone o repositório:
git clone https://github.com/LuisHenriqueofc01/sistema-gerenciamento-tarefas.git
cd sistema-gerenciamento-tarefas

2. Crie e ative um ambiente virtual:
python -m venv venv
source venv/bin/activate  # ou venv\Scripts\activate no Windows

3. Instale as dependências:
pip install -r requirements.txt

4. Inicialize o banco de dados:
flask db init
flask db migrate
flask db upgrade

5. Execute a aplicação:
python run.py

Acesse: http://localhost:5000

👥 Equipe do Projeto

Gabriel – Gerente Geral
Luis – Desenvolvedor Back-end
Eduardo – Desenvolvedor Front-end
