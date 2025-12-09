from flask import Flask, jsonify, request, send_from_directory
from dotenv import load_dotenv
import os
from database import db

# Cargar variables de entorno
load_dotenv()

app = Flask(__name__, static_folder='frontend', static_url_path='')

# Configuración
app.config['MONGODB_URI'] = os.getenv('MONGODB_URI')
app.config['SECRET_KEY'] = os.getenv('SESSION_SECRET')

# Rutas para servir el frontend
@app.route('/')
def index():
    return send_from_directory('frontend', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('frontend', path)

# Importar y registrar blueprints
from routes.auth import auth_bp
from routes.peliculas import peliculas_bp
from routes.upload import upload_bp

app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(peliculas_bp, url_prefix='/api/peliculas')
app.register_blueprint(upload_bp, url_prefix='/api/upload')

if __name__ == '__main__':
    app.run(debug=True, port=5000)
