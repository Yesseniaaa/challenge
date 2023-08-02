import tkinter as tk
from tkinter import messagebox
import requests
from pymongo import MongoClient
from flask import Flask, request, jsonify
from functools import wraps

# Establecer la conexión con MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['challenge']

# Definir el esquema de datos para los usuarios
usuarios_collection = db['usuarios']
esquema_usuario = {
    "nombre": str,
    "edad": int,
    "email": str,
    "telefono": str,
    "direccion": str,
    "fec_alta": int,
    "user_name": str,
    "codigo_zip": int,
    "credit_card_num": int,
    "credit_card_ccv": int,
    "cuenta_numero": int,
    "direccion": str,
    "geo_latitud": int,
    "geo_longitud": int,
    "color_favorito": str,
    "foto_dni": str,
    "ip": str,
    "auto": str,
    "auto_modelo": str,
    "auto_tipo": str,
    "auto_color": str,
    "cantidad_compras_realizadas": int,
    "avatar": str,
    "fec_birthday": str,
    "id": int
}

# Asegurarse de que el campo "nombre" sea único para cada usuario
usuarios_collection.create_index("nombre", unique=True)

# Función para realizar la solicitud al proveedor externo
def fetch_data():
    # Obtener las credenciales ingresadas por el usuario
    username = entry_username.get()
    password = entry_password.get()

    # Realizar la autenticación
    if not verificar_credenciales(username, password):
        messagebox.showerror("Error", "Credenciales inválidas.")
        return

    try:
        response = requests.get("https://62433a7fd126926d0c5d296b.mockapi.io/api/v1/usuarios")
        data = response.json()
        insertar_datos_en_mongodb(data)
        messagebox.showinfo("Éxito", "Datos obtenidos y almacenados en MongoDB.")
    except requests.exceptions.RequestException as e:
        messagebox.showerror("Error", "No se pudo obtener los datos del proveedor externo.")

# Función para insertar los datos en MongoDB
def insertar_datos_en_mongodb(data):
    result = usuarios_collection.insert_many(data)
    return len(result.inserted_ids)

# Función para verificar la autenticación
def verificar_credenciales(username, password):
    return username == "usuario_autorizado" and password == "contraseña_segura"

# Función para mostrar la lista de usuarios almacenados
def mostrar_usuarios_almacenados():
    # Simulación de consulta de usuarios almacenados
    # Aquí deberías implementar la lógica real para obtener los usuarios desde MongoDB
    usuarios = usuarios_collection.find({}, {'_id': 0})
    lista_usuarios = "\n".join([str(usuario) for usuario in usuarios])
    messagebox.showinfo("Usuarios Almacenados", lista_usuarios)

# Crear la interfaz
root = tk.Tk()
root.title("Interfaz de Consumo de Datos y API")

# Campos para ingresar credenciales de autenticación
label_username = tk.Label(root, text="Nombre de Usuario:")
label_username.pack()
entry_username = tk.Entry(root)
entry_username.pack(pady=5)

label_password = tk.Label(root, text="Contraseña:")
label_password.pack()
entry_password = tk.Entry(root, show="*")
entry_password.pack(pady=10)

# Botón para obtener y almacenar datos
btn_fetch_data = tk.Button(root, text="Obtener y Almacenar Datos", command=fetch_data)
btn_fetch_data.pack()

# Botón para mostrar la lista de usuarios almacenados
btn_show_users = tk.Button(root, text="Mostrar Usuarios Almacenados", command=mostrar_usuarios_almacenados)
btn_show_users.pack(pady=10)

# Ejecutar la interfaz
root.mainloop()

# App de Flask
app = Flask(__name__)

# Decorador para requerir autenticación en los endpoints de la API
def requerir_autenticacion(f):
    @wraps(f)
    def decorador(*args, **kwargs):
        auth = request.authorization
        if not auth or not verificar_credenciales(auth.username, auth.password):
            return jsonify({'mensaje': 'Autenticación requerida'}), 401
        return f(*args, **kwargs)
    return decorador

# Ruta para la página principal
@app.route('http://127.0.0.1:5000/')
def home():
    return "¡Bienvenido a la aplicación de consumo de datos y API!"

# Endpoint para obtener todos los usuarios (requiere autenticación)
@app.route('/api/usuarios', methods=['GET'])
@requerir_autenticacion
def obtener_usuarios():
    usuarios = usuarios_collection.find({}, {'_id': 0})
    return jsonify(list(usuarios))

# Endpoint para obtener un usuario específico por su ID (requiere autenticación)
@app.route('/api/usuarios/<id_usuario>', methods=['GET'])
@requerir_autenticacion
def obtener_usuario_por_id(id_usuario):
    usuario = usuarios_collection.find_one({'id': id_usuario}, {'_id': 0})
    if usuario:
        return jsonify(usuario)
    else:
        return jsonify({'mensaje': 'Usuario no encontrado'}), 404

if __name__ == '__main__':
    app.run(debug=True)