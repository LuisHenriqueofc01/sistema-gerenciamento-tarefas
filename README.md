# 📋 Sistema de Gerenciamento de Tarefas

Sistema web desenvolvido em Flask com foco na criação e gerenciamento de processos e tarefas. A interface inclui um painel Kanban dinâmico, modelos de processos reutilizáveis, sistema de autenticação de usuários e funcionalidades administrativas para controle completo das tarefas da equipe.

---

## 🛠 Tecnologias Utilizadas

- Python 3.x  
- Flask  
- SQLite  
- SQLAlchemy  
- Flask-Login  
- Flask-Migrate  
- Flask-Mail  
- Bootstrap 5  
- JavaScript (Fetch API, DOM)  
- HTML5 e Jinja2  

---

## 📌 Funcionalidades

- ✅ **Autenticação de usuários** (login, logout, alteração de senha)  
- 🧑‍💼 **Painel administrativo** (criação de usuários e visualização global)  
- 📁 **Criação e edição de modelos de processo** com múltiplas tarefas  
- ⚙️ **Instanciação de processos reais** a partir de modelos  
- 📌 **Kanban dinâmico** com status: pendente, em andamento e concluído  
- 🗓 **Datas de início e fim** para tarefas e processos  
- 🔔 **Notificações automáticas** de tarefas vencidas por e-mail e popup  
- 📉 **Ocultação automática de tarefas concluídas após o mês vigente**  
- 🚨 **Destaque visual** para tarefas atrasadas  
- 🔐 **Controle de permissões** com diferenciação entre usuário comum e admin  

sistema-gerenciamento-tarefas/
├── app/
│   ├── static/
│   ├── templates/
│   ├── models/
│   ├── routes/
│   └── __init__.py
├── migrations/
├── instance/
│   └── app.db
├── agendador.py
├── config.py
├── requirements.txt
├── run.py
└── .env (não versionado)

Como executar localmente:

git clone https://github.com/LuisHenriqueofc01/sistema-gerenciamento-tarefas.git
cd sistema-gerenciamento-tarefas

python -m venv venv
venv\Scripts\activate  # Windows
# ou
source venv/bin/activate  # Linux/macOS

pip install -r requirements.txt

flask db init
flask db migrate
flask db upgrade

python run.py
Acesse: http://localhost:5000

👥 Equipe do Projeto:

Gabriel – Gerente Geral

Luis – Desenvolvedor Back-end

Eduardo – Desenvolvedor Front-end

