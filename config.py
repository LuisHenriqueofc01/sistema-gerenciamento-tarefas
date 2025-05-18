import os

class Config:
    SECRET_KEY = "super-secret-key"
    SQLALCHEMY_DATABASE_URI = "postgresql://postgres:12345@localhost:5432/meu_banco"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
