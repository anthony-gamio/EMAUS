from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Configuración de la base de datos (usa tu URL de conexión de Render)
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://inventario_emaus_user:09YZExz3HHN8Ysq0S4JA6yzWL5vEXm2d@dpg-cuio2kd6l47c73ahk30g-a.oregon-postgres.render.com/inventario_emaus')
engine = create_engine(DATABASE_URL)
Base = declarative_base()

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

def agregar_item(nombre, cantidad, categoria):
    item = session.query(Item).filter_by(nombre=nombre).first()
    if item:
        item.cantidad += cantidad
    else:
        nuevo_item = Item(nombre=nombre, cantidad=cantidad, categoria=categoria)
        session.add(nuevo_item)
    session.commit()

def mostrar_inventario():
    inventario = session.query(Item).all()
    return [{'nombre': item.nombre, 'cantidad': item.cantidad, 'categoria': item.categoria, 'consumo_estimado': item.consumo_estimado or 'N/A'} for item in inventario]

def calcular_consumo_estimado(nombre, consumo_estimado):
    item = session.query(Item).filter_by(nombre=nombre).first()
    if item:
        item.consumo_estimado = consumo_estimado
        session.commit()
        return f"Consumo estimado actualizado para {nombre}"
    return f"El artículo {nombre} no existe en el inventario"

# Función para actualizar la cantidad disponible de un producto
def actualizar_cantidad(nombre, nueva_cantidad):
    item = session.query(Item).filter_by(nombre=nombre).first()
    if item:
        item.cantidad = nueva_cantidad
        session.commit()
        print(f"Cantidad actualizada para {nombre}: {nueva_cantidad}")
    else:
        print(f"El artículo {nombre} no existe en el inventario.")

# Generar reporte de bajo stock (cantidad disponible menor a un umbral)
def reporte_bajo_stock(umbral):
    bajo_stock = session.query(Item).filter(Item.cantidad < umbral).all()
    return [{'nombre': item.nombre, 'cantidad': item.cantidad, 'categoria': item.categoria} for item in bajo_stock]

# Ejemplo de actualización
actualizar_cantidad('A001', 80)

print("\nReporte de productos con bajo stock (umbral: 10):")
print(reporte_bajo_stock(10))