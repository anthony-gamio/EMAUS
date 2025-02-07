from flask import Flask, jsonify, request
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Configuración de la base de datos (usa tu URL de conexión de Render)
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://inventario_emaus_user:09YZExz3HHN8Ysq0S4JA6yzWL5vEXm2d@dpg-cuio2kd6l47c73ahk30g-a.oregon-postgres.render.com/inventario_emaus')
engine = create_engine(DATABASE_URL)
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

@app.route('/agregar_item', methods=['POST'])
def agregar_item():
    data = request.json
    nombre = data.get('nombre')
    cantidad = data.get('cantidad', 0)
    categoria = data.get('categoria')
    
    item = session.query(Item).filter_by(nombre=nombre).first()
    if item:
        item.cantidad += cantidad
    else:
        nuevo_item = Item(nombre=nombre, cantidad=cantidad, categoria=categoria)
        session.add(nuevo_item)
    session.commit()
    return jsonify({'mensaje': 'Item agregado exitosamente'})

@app.route('/mostrar_inventario', methods=['GET'])
def mostrar_inventario():
    inventario = session.query(Item).all()
    resultado = [{'nombre': item.nombre, 'cantidad': item.cantidad, 'categoria': item.categoria, 'consumo_estimado': item.consumo_estimado or 'N/A'} for item in inventario]
    return jsonify(resultado)

@app.route('/calcular_consumo_estimado', methods=['POST'])
def calcular_consumo_estimado():
    data = request.json
    nombre = data.get('nombre')
    consumo_estimado = data.get('consumo_estimado')
    
    item = session.query(Item).filter_by(nombre=nombre).first()
    if item:
        item.consumo_estimado = consumo_estimado
        session.commit()
        return jsonify({'mensaje': f"Consumo estimado actualizado para {nombre}"})
    return jsonify({'mensaje': f"El artículo {nombre} no existe en el inventario"})

@app.route('/actualizar_cantidad', methods=['POST'])
def actualizar_cantidad():
    data = request.json
    nombre = data.get('nombre')
    nueva_cantidad = data.get('nueva_cantidad')
    
    item = session.query(Item).filter_by(nombre=nombre).first()
    if item:
        item.cantidad = nueva_cantidad
        session.commit()
        return jsonify({'mensaje': f"Cantidad actualizada para {nombre}: {nueva_cantidad}"})
    return jsonify({'mensaje': f"El artículo {nombre} no existe en el inventario."})

@app.route('/reporte_bajo_stock', methods=['GET'])
def reporte_bajo_stock():
    umbral = int(request.args.get('umbral', 10))
    bajo_stock = session.query(Item).filter(Item.cantidad < umbral).all()
    resultado = [{'nombre': item.nombre, 'cantidad': item.cantidad, 'categoria': item.categoria} for item in bajo_stock]
    return jsonify(resultado)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))