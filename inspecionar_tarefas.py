from app import create_app, db
from app.models.models import Task

app = create_app()
app.app_context().push()

# Imprimir os nomes das colunas da tabela Task
print("Campos do modelo Task:")
for column in Task.__table__.columns:
    print(f"- {column.name}")
