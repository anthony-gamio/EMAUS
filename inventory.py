import pandas as pd

# Cargar el archivo CSV con tus columnas actuales
inventory = pd.read_csv('inventario.csv')

# Asegúrate de que las columnas están correctamente definidas
print(inventory.head())  # Esto te permitirá verificar si los datos se cargan correctamente

# inventory.py

# Inventario inicial
inventario = {}

def agregar_item(nombre, cantidad, categoria):
    if nombre in inventario:
        inventario[nombre]['cantidad'] += cantidad
    else:
        inventario[nombre] = {'cantidad': cantidad, 'categoria': categoria}

def mostrar_inventario():
    return inventario

def calcular_consumo_estimado(nombre, consumo_estimado):
    if nombre in inventario:
        inventario[nombre]['consumo_estimado'] = consumo_estimado
        return f"Consumo estimado actualizado para {nombre}"
    return f"El artículo {nombre} no existe en el inventario"
