from flask.cli import FlaskGroup
from app import create_app, db
from flask_migrate import Migrate

app = create_app()
cli = FlaskGroup(app)

# Ativa comandos de migrate
Migrate(app, db)

if __name__ == "__main__":
    cli()
