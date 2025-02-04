from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def home():
    # Datos del inventario (traídos desde tu lógica actual)
    inventory = [
        {"item": "Café", "quantity": 20},
        {"item": "Azúcar", "quantity": 15},
    ]
    return render_template('home.html', inventory=inventory)

if __name__ == "__main__":
    app.run(debug=True)
