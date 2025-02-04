from flask import Flask, render_template, request, redirect
import pandas as pd

app = Flask(__name__)

# Cargar el archivo CSV
def cargar_inventario():
    try:
        df = pd.read_csv('inventario.csv', encoding='utf-8', errors='replace')
        df['cantidad'] = df['cantidad'].astype(int)
        return df.set_index('nombre').to_dict(orient='index')
    except FileNotFoundError:
        return {}

# Guardar el inventario en el CSV
def guardar_inventario():
    df = pd.DataFrame.from_dict(inventario, orient='index')
    df.reset_index(inplace=True)
    df.rename(columns={'index': 'nombre'}, inplace=True)
    df.to_csv('inventario.csv', index=False)

inventario = cargar_inventario()

@app.route('/')
def index():
    return render_template('index.html', inventario=inventario)

@app.route('/agregar', methods=['POST'])
def agregar():
    nombre = request.form['nombre']
    cantidad = int(request.form['cantidad'])
    categoria = request.form['categoria']
    
    if nombre in inventario:
        inventario[nombre]['cantidad'] += cantidad
    else:
        inventario[nombre] = {'cantidad': cantidad, 'categoria': categoria}
    
    guardar_inventario()
    return redirect('/')

@app.route('/consumo', methods=['POST'])
def consumo():
    nombre = request.form['nombre']
    consumo_estimado = int(request.form['consumo_estimado'])
    
    if nombre in inventario:
        inventario[nombre]['consumo_estimado'] = consumo_estimado
    
    guardar_inventario()
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)