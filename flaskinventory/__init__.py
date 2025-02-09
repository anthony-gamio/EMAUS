from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    # La SECRET_KEY se usa para proteger sesiones, formularios (CSRF), etc.
    SECRET_KEY = os.environ.get('SECRET_KEY') or '323b22caac41acbf'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

  # Obtener la URL de la base de datos desde la variable de entorno DATABASE_URL
    db_url = os.environ.get('DATABASE_URL')
    if db_url:
        # Si la URL usa el prefijo "postgres://", reemplázalo por "postgresql://"
        if db_url.startswith("postgres://"):
            db_url = db_url.replace("postgres://", "postgresql://", 1)
        # Forzar el uso de SSL para todas las conexiones, solo si no se ha especificado ya
        if "sslmode" not in db_url:
            if '?' in db_url:
                db_url += "&sslmode=require"
            else:
                db_url += "?sslmode=require"
        SQLALCHEMY_DATABASE_URI = db_url
    else:
        SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')

db = SQLAlchemy(app)

from flaskinventory import routes

with app.app_context():
    db.create_all()
    db.session.commit()
