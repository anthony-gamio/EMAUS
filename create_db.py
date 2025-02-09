from flaskinventory import app, db

# Asegúrate de que las tablas se crean dentro del contexto de la aplicación
with app.app_context():
    db.create_all()
    print("Base de datos creada exitosamente.")