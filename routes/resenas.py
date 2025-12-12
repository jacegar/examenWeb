from flask import Blueprint, request, jsonify
from bson import ObjectId
from database import db
from models.resena import Resena
from services.geocoding_service import geocode_address
from services.cloudinary_service import upload_image
from datetime import datetime
from auth import token_required

resenas_bp = Blueprint('resenas', __name__)

# Obtener todas las reseñas
@resenas_bp.route('', methods=['GET'])
@token_required
def get_resenas(user_data):
    try:
        collection = db.get_collection('resenas')
        resenas = list(collection.find())
        
        result = []
        for r in resenas:
            resena = Resena.from_dict(r)
            result.append(resena.to_json())
        
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Obtener una reseña por ID
@resenas_bp.route('/<id>', methods=['GET'])
@token_required
def get_resena(user_data, id):
    try:
        collection = db.get_collection('resenas')
        resena_data = collection.find_one({'_id': ObjectId(id)})
        
        if not resena_data:
            return jsonify({'error': 'Reseña no encontrada'}), 404
        
        resena = Resena.from_dict(resena_data)
        return jsonify(resena.to_json()), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Crear una nueva reseña con imágenes
@resenas_bp.route('', methods=['POST'])
@token_required
def create_resena(user_data):
    try:
        # Obtener datos del formulario
        nombre_establecimiento = request.form.get('nombre_establecimiento')
        direccion = request.form.get('direccion')
        valoracion = request.form.get('valoracion')
        
        # Validación básica
        if not nombre_establecimiento or not direccion or not valoracion:
            return jsonify({'error': 'Nombre, dirección y valoración son requeridos'}), 400
        
        try:
            valoracion = int(valoracion)
            if valoracion < 1 or valoracion > 5:
                return jsonify({'error': 'Valoración debe estar entre 1 y 5 estrellas'}), 400
        except ValueError:
            return jsonify({'error': 'Valoración debe ser un número entero'}), 400
        
        # Obtener coordenadas mediante geocoding
        coords = geocode_address(direccion)
        if not coords:
            return jsonify({'error': 'No se pudo geocodificar la dirección proporcionada'}), 400
        
        # Obtener URLs de imágenes ya subidas (si las hay)
        imagenes_uri = request.form.getlist('imagenes_urls[]')
        
        # Procesar imágenes nuevas si existen (backward compatibility)
        if 'imagenes' in request.files:
            files = request.files.getlist('imagenes')
            for file in files:
                if file and file.filename:
                    # Validar tipo de archivo
                    allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
                    file_extension = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
                    
                    if file_extension in allowed_extensions:
                        result = upload_image(file, folder='reviews')
                        if result:
                            imagenes_uri.append(result['url'])
        
        # Extraer información del token del usuario autenticado
        token = None
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            token = auth_header.split(' ')[1]
        
        # Crear objeto Resena
        resena = Resena(
            nombre_establecimiento=nombre_establecimiento,
            direccion=direccion,
            latitud=coords['latitud'],
            longitud=coords['longitud'],
            valoracion=valoracion,
            imagenes_uri=imagenes_uri,
            autor_email=user_data['email'],
            autor_nombre=user_data.get('name', ''),
            token=token,
            token_emision=datetime.fromtimestamp(user_data['iat']),
            token_caducidad=datetime.fromtimestamp(user_data['exp'])
        )
        
        collection = db.get_collection('resenas')
        result = collection.insert_one(resena.to_dict())
        
        resena._id = result.inserted_id
        return jsonify(resena.to_json()), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Eliminar una reseña
@resenas_bp.route('/<id>', methods=['DELETE'])
@token_required
def delete_resena(user_data, id):
    try:
        collection = db.get_collection('resenas')
        
        # Verificar que la reseña existe
        resena_data = collection.find_one({'_id': ObjectId(id)})
        if not resena_data:
            return jsonify({'error': 'Reseña no encontrada'}), 404
        
        # Opcional: verificar que el usuario es el autor
        # if resena_data['autor_email'] != user_data['email']:
        #     return jsonify({'error': 'No autorizado para eliminar esta reseña'}), 403
        
        result = collection.delete_one({'_id': ObjectId(id)})
        
        if result.deleted_count == 0:
            return jsonify({'error': 'No se pudo eliminar la reseña'}), 500
        
        return jsonify({'message': 'Reseña eliminada exitosamente'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Endpoint para geocoding de direcciones (útil para el frontend)
@resenas_bp.route('/geocode', methods=['POST'])
@token_required
def geocode_endpoint(user_data):
    try:
        data = request.get_json()
        direccion = data.get('direccion')
        
        if not direccion:
            return jsonify({'error': 'Dirección es requerida'}), 400
        
        coords = geocode_address(direccion)
        
        if not coords:
            return jsonify({'error': 'No se pudo geocodificar la dirección'}), 404
        
        return jsonify(coords), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
