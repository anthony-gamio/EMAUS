from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os



app = Flask(__name__)
app.config['SECRET_KEY'] = '323b22caac41acbf'
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL') 
db = SQLAlchemy(app)

from flaskinventory import routes

with app.app_context():
    db.create_all()
    # Si tienes datos de ejemplo para insertar:
    # nuevo_dato = ModeloEjemplo(campo='valor')
    # db.session.add(nuevo_dato)
    db.session.commit()
