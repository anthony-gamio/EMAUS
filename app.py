from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from urllib.parse import quote_plus

app = Flask(__name__)

# Configuración de la base de datos
DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# Añadir opciones SSL si es necesario
DATABASE_URL += "?sslmode=disable"

# Crear el motor y la sesión de SQLAlchemy
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()

# Definición del modelo
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String

Base = declarative_base()

class Item(Base):
    __tablename__ = 'inventario'
    id = Column(Integer, primary_key=True)
    nombre = Column(String)
    cantidad = Column(Integer)
    categoria = Column(String)
    consumo_estimado = Column(Integer)

# Crear tablas si no existen
Base.metadata.create_all(engine)

@app.route('/')
def index():
    inventario = session.query(Item).all()
    return render_template('index.html', inventario=inventario)

@app.route('/agregar', methods=['POST'])
def agregar():
    nombre = request.form['nombre']
    cantidad = request.form['cantidad']
    categoria = request.form['categoria']
    consumo_estimado = request.form['consumo_estimado']

    nuevo_item = Item(nombre=nombre, cantidad=cantidad, categoria=categoria, consumo_estimado=consumo_estimado)
    session.add(nuevo_item)
    session.commit()

    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)