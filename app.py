from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import os
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from urllib.parse import quote_plus

app = Flask(__name__)

# Configuración de la base de datos
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("La variable de entorno DATABASE_URL no está configurada.")

if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# Crear el motor y la sesión de SQLAlchemy
engine = create_engine(DATABASE_URL, pool_pre_ping=True, pool_size=10, max_overflow=20)
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


# Función para vaciar la tabla inicial
def reiniciar_tabla():
    session.query(Item).delete()
    session.commit()
    print("La tabla 'inventario' ha sido vaciada.")

reiniciar_tabla()


# Cargar CSV solo si la tabla está vacía
def cargar_csv_inicial():
    if session.query(Item).count() == 0:
        # Asegúrate de que el archivo CSV esté en la misma carpeta o ajusta la ruta
        csv_path = 'inventario.csv'  
        if os.path.exists(csv_path):
            df = pd.read_csv(csv_path)
            for _, row in df.iterrows():
                item = Item(
                    nombre=row['nombre'],
                    cantidad=row['cantidad'],
                    categoria=row['categoria'],
                    consumo_estimado=row.get('consumo_estimado', 0)  # Valor predeterminado si falta
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
    inventario = session.query(Item).all()
    return render_template('index.html', inventario=inventario)

@app.route('/agregar', methods=['POST'])
def agregar():
    nombre = request.form['nombre']
    cantidad = int(request.form['cantidad'])
    categoria = request.form['categoria']

    item_existente = session.query(Item).filter_by(nombre=nombre, categoria=categoria).first()

    if item_existente:
        item_existente.cantidad += cantidad
        session.commit()
            
    else:
        nuevo_item = Item(nombre=nombre, cantidad=cantidad, categoria=categoria)
        session.add(nuevo_item)
        session.commit()

    return redirect(url_for('index'))

@app.route('/checklist')
def checklist():
    # Cargar el CSV de actividades
    checklist_path = 'checklist.csv'
    if os.path.exists(checklist_path):
        df = pd.read_csv(checklist_path)
        # Convertir la columna 'completado' a booleano para los checkboxes
        df['completado'] = df['completado'].astype(bool)
        actividades = df.to_dict(orient='records')
    else:
        actividades = []
    
    return render_template('checklist.html', checklist=actividades)

@app.route('/logout')
def logout():
    # Cargar el CSV de actividades
    checklist_path = 'checklist.csv'
    if os.path.exists(checklist_path):
        df = pd.read_csv(checklist_path)
        # Convertir la columna 'completado' a booleano para los checkboxes
        df['completado'] = df['completado'].astype(bool)
        actividades = df.to_dict(orient='records')
    else:
        actividades = []
    
    return render_template('checklist.html', checklist=actividades)

if __name__ == '__main__':
    app.run(debug=True)