from flask import Flask, render_template, request, redirect, url_for
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Configuración de la base de datos (usa tu URL de conexión de Render)
DATABASE_URL = os.getenv('DATABASE_URL', 'postgres://inventario_emaus_user:09YZExz3HHN8Ysq0S4JA6yzWL5vEXm2d@dpg-cuio2kd6l47c73ahk30g-a.oregon-postgres.render.com/inventario_emaus')

# Corrección para compatibilidad de URL con SQLAlchemy
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# Crear el motor de base de datos con SSL habilitado (requerido por Render)
engine = create_engine(DATABASE_URL, connect_args={"sslmode": "require"})
Base = declarative_base()

# Inicializar la aplicación Flask
app = Flask(__name__)

# Definición del modelo de Inventario
class Item(Base):
    __tablename__ = 'inventario'
    id = Column(Integer, primary_key=True)
    nombre = Column(String, unique=True, nullable=False)
    cantidad = Column(Integer, default=0)
    categoria = Column(String, nullable=False)
    consumo_estimado = Column(Integer, nullable=True)

# Crear las tablas en la base de datos
Base.metadata.create_all(engine)

# Crear una sesión para interactuar con la base de datos
Session = sessionmaker(bind=engine)
session = Session()

@app.route('/')
def index():
    inventario = session.query(Item).all()
    return render_template('index.html', inventario={item.nombre: {'cantidad': item.cantidad, 'categoria': item.categoria} for item in inventario})

@app.route('/agregar', methods=['POST'])
def agregar():
    nombre = request.form.get('nombre')
    cantidad = int(request.form.get('cantidad', 0))
    categoria = request.form.get('categoria')

    item = session.query(Item).filter_by(nombre=nombre).first()
    if item:
        item.cantidad += cantidad
    else:
        nuevo_item = Item(nombre=nombre, cantidad=cantidad, categoria=categoria)
        session.add(nuevo_item)
    session.commit()
    return redirect(url_for('index'))

@app.route('/consumo', methods=['POST'])
def consumo():
    nombre = request.form.get('nombre')
    consumo_estimado = int(request.form.get('consumo_estimado'))

    item = session.query(Item).filter_by(nombre=nombre).first()
    if item:
        item.consumo_estimado = consumo_estimado
        session.commit()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))