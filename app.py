from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
import os
import pandas as pd
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship
from urllib.parse import quote_plus

app = Flask(__name__)

# Configuración de la base de datos
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("La variable de entorno DATABASE_URL no está configurada.")

if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

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

class Area(db.Model):
    __tablename__ = 'areas'
    id = Column(Integer, primary_key=True)
    nombre = Column(String, nullable=False, unique=True)
    materiales = relationship('Material', backref='area', cascade="all, delete-orphan")

class Material(db.Model):
    __tablename__ = 'materiales'
    id = Column(Integer, primary_key=True)
    nombre = Column(String, nullable=False)
    area_id = Column(Integer, ForeignKey('areas.id'), nullable=False)
    asignaciones = relationship('AsignacionItem', backref='material', cascade="all, delete-orphan")

class Inventario(db.Model):
    __tablename__ = 'inventario'
    id = Column(Integer, primary_key=True)
    nombre = Column(String, nullable=False)
    cantidad = Column(Integer, nullable=False)
    categoria = Column(String, nullable=False)
    consumo_estimado = Column(Integer, default=0)

class AsignacionItem(db.Model):
    __tablename__ = 'asignacion_items'
    id = Column(Integer, primary_key=True)
    material_id = Column(Integer, ForeignKey('materiales.id'), nullable=False)
    item_id = Column(Integer, ForeignKey('inventario.id'), nullable=False)
    cantidad_asignada = Column(Integer, nullable=False)
    
    item = relationship('Inventario', backref='asignaciones')

# Crear tablas si no existen
Base.metadata.create_all(engine)
with app.app_context():
    db.create_all()

# Función para vaciar la tabla inicial
def reiniciar_tabla():
    if os.getenv('FLASK_ENV') == 'development':
        session.query(AsignacionItem).delete()
        session.query(Inventario).delete()
        session.commit()
        print("La tabla 'inventario' y 'asignacion_items' han sido vaciadas en el entorno local.")
    else:
        print("No se vacía la tabla en producción.")


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

@app.route('/actividades')
def actividades():
    actividades_path = 'actividades.csv'
    
    if os.path.exists(actividades_path):
        try:
            # Intentar leer el CSV con codificación UTF-8
            df = pd.read_csv(actividades_path, encoding='utf-8')

            # Asegurarse de que la columna 'Estado' es booleana
            df['Estado'] = df['Estado'].astype(bool)
            dias_ordenados = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
            df['Día'] = df['Día'].str.capitalize()
            df['Día'] = pd.Categorical(df['Día'], categories=dias_ordenados, ordered=True)
            df = df.sort_values('Día')

            actividades = df.to_dict(orient='records')

        except pd.errors.ParserError as e:
            # Si hay un error al leer el CSV, mostrar un mensaje claro en la página
            return f"<h2>Error al leer el CSV de actividades:</h2><p>{e}</p>", 500

        except Exception as e:
            # Capturar cualquier otro error inesperado
            return f"<h2>Ocurrió un error inesperado:</h2><p>{e}</p>", 500

    else:
        actividades = []

    return render_template('actividades.html', actividades=actividades)

@app.route('/actualizar_actividades', methods=['POST'])
def actualizar_actividades():
    actividades_path = ('actividades.csv')
    df = pd.read_csv(actividades_path, encoding='utf-8')

    # Actualizar el estado de 'Estado' según los checkboxes enviados
    for i in range(len(df)):
        checkbox_name = f'completado_{i}'
        df.at[i, 'Estado'] = checkbox_name in request.form  # True si está marcado, False si no

    # Guardar los cambios en el CSV
    df.to_csv(actividades_path, index=False)

    return redirect(url_for('actividades'))

@app.route('/areas')
def areas():
    todas_areas = Area.query.all()
    return render_template('gestionar_areas.html', areas=todas_areas)

@app.route('/areas/agregar', methods=['POST'])
def agregar_area():
    nombre_area = request.form.get('nombre_area')
    if nombre_area:
        nueva_area = Area(nombre=nombre_area)
        db.session.add(nueva_area)
        db.session.commit()
    return redirect(url_for('areas'))

@app.route('/areas/eliminar/<int:area_id>', methods=['POST'])
def eliminar_area(area_id):
    area = Area.query.get_or_404(area_id)
    db.session.delete(area)
    db.session.commit()
    return redirect(url_for('areas'))

@app.route('/areas/<int:area_id>/materiales')
def ver_materiales(area_id):
    area = Area.query.get_or_404(area_id)
    materiales = Material.query.filter_by(area_id=area.id).all()
    return render_template('materiales_partial.html', materiales=materiales, area=area)

@app.route('/materiales/agregar/<int:area_id>', methods=['POST'])
def agregar_material(area_id):
    nombre_material = request.form.get('nombre_material')
    if nombre_material:
        nuevo_material = Material(nombre=nombre_material, area_id=area_id)
        db.session.add(nuevo_material)
        db.session.commit()
    return redirect(url_for('ver_materiales', area_id=area_id))

@app.route('/materiales/eliminar/<int:material_id>', methods=['POST'])
def eliminar_material(material_id):
    material = Material.query.get_or_404(material_id)
    area_id = material.area_id
    db.session.delete(material)
    db.session.commit()
    return redirect(url_for('ver_materiales', area_id=area_id))

@app.route('/asignar_items/<int:material_id>')
def ver_asignacion_items(material_id):
    material = Material.query.get_or_404(material_id)
    inventario = Inventario.query.all()  # Obtener todos los ítems del inventario
    asignaciones = AsignacionItem.query.filter_by(material_id=material_id).all()
    return render_template('asignar_items_partial.html', material=material, inventario=inventario, asignaciones=asignaciones)

@app.route('/asignar_items/<int:material_id>', methods=['POST'])
def asignar_items(material_id):
    item_id = int(request.form.get('item_id'))
    cantidad_asignada = int(request.form.get('cantidad_asignada'))
    
    # Verificar si ya existe una asignación previa para el mismo ítem y material
    asignacion_existente = AsignacionItem.query.filter_by(material_id=material_id, item_id=item_id).first()

    if asignacion_existente:
        asignacion_existente.cantidad_asignada += cantidad_asignada  # Sumar la cantidad si ya existe
    else:
        nueva_asignacion = AsignacionItem(material_id=material_id, item_id=item_id, cantidad_asignada=cantidad_asignada)
        db.session.add(nueva_asignacion)

    # Actualizar el consumo estimado en el inventario
    item_inventario = Inventario.query.get(item_id)
    item_inventario.consumo_estimado += cantidad_asignada

    db.session.commit()
    return redirect(url_for('ver_asignacion_items', material_id=material_id))

@app.route('/asignar_items/eliminar/<int:asignacion_id>', methods=['POST'])
def eliminar_asignacion(asignacion_id):
    asignacion = AsignacionItem.query.get_or_404(asignacion_id)

    # Actualizar el consumo estimado en el inventario
    item_inventario = Inventario.query.get(asignacion.item_id)
    item_inventario.consumo_estimado -= asignacion.cantidad_asignada

    db.session.delete(asignacion)
    db.session.commit()
    return redirect(url_for('ver_asignacion_items', material_id=asignacion.material_id))


if __name__ == '__main__':
    app.run(debug=True)