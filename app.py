from flask import Flask, render_template, request, redirect, url_for, jsonify
import os
import pandas as pd
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from urllib.parse import quote_plus

app = Flask(__name__)

# Configuración de la base de datos
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("La variable de entorno DATABASE_URL no está configurada.")

if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

DATABASE_URL += "?sslmode=require"

engine = create_engine(DATABASE_URL, pool_pre_ping=True, pool_size=10, max_overflow=20)
Session = sessionmaker(bind=engine)
session = Session()

# Definición del modelo
Base = declarative_base()

class Inventario(Base):
    __tablename__ = 'inventario'
    id = Column(Integer, primary_key=True)
    nombre = Column(String, nullable=False)
    cantidad = Column(Integer, nullable=False)
    categoria = Column(String, nullable=False)
    consumo_estimado = Column(Integer, default=0)

class AsignacionItem(Base):
    __tablename__ = 'asignacion_items'
    id = Column(Integer, primary_key=True)
    material_id = Column(Integer, ForeignKey('materiales.id'), nullable=False)
    item_id = Column(Integer, ForeignKey('inventario.id'), nullable=False)
    cantidad_asignada = Column(Integer, nullable=False)
    item = relationship('Inventario', backref='asignaciones')

# Crear tablas si no existen
Base.metadata.create_all(engine)

# Función para vaciar la tabla inicial
def reiniciar_tabla():
    if os.getenv('FLASK_ENV') == 'development':
        session.query(AsignacionItem).delete()
        session.query(Inventario).delete()
        session.commit()
        print("Las tablas 'inventario' y 'asignacion_items' han sido vaciadas en el entorno local.")
    else:
        print("No se vacía la tabla en producción.")

# Cargar CSV solo si la tabla está vacía
def cargar_csv_inicial():
    if session.query(Inventario).count() == 0:
        csv_path = 'inventario.csv'
        if os.path.exists(csv_path):
            df = pd.read_csv(csv_path)
            for _, row in df.iterrows():
                item = Inventario(
                    nombre=row['nombre'],
                    cantidad=row['cantidad'],
                    categoria=row['categoria'],
                    consumo_estimado=row.get('consumo_estimado', 0)
                )
                session.add(item)
            session.commit()
            print("Datos cargados exitosamente desde el CSV.")
        else:
            print(f"El archivo {csv_path} no existe.")
    else:
        print("La tabla ya contiene datos. No se cargará el CSV.")

# Llamar a la función al iniciar la aplicación
cargar_csv_inicial()

@app.route('/')
def index():
    session = Session()  # Crear una nueva sesión
    try:
        inventario = session.query(Inventario).all()
        return render_template('index.html', inventario=inventario)
    finally:
        session.close()  # Cerrar la sesión después de usarla

@app.route('/agregar', methods=['POST'])
def agregar():
    nombre = request.form['nombre']
    cantidad = int(request.form['cantidad'])
    categoria = request.form['categoria']

    item_existente = session.query(Inventario).filter_by(nombre=nombre, categoria=categoria).first()

    if item_existente:
        item_existente.cantidad += cantidad
        session.commit()
    else:
        nuevo_item = Inventario(nombre=nombre, cantidad=cantidad, categoria=categoria)
        session.add(nuevo_item)
        session.commit()

    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
