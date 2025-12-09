from flask import Blueprint, request, jsonify
from bson import ObjectId
from database import db
from models.sala import Sala

salas_bp = Blueprint('salas', __name__)

# Obtener todas las salas
@salas_bp.route('', methods=['GET'])
def get_salas():
    from auth import token_required
    
    @token_required
    def _get(user_data):
        try:
            collection = db.get_collection('salas')
            salas = list(collection.find())
            
            result = []
            for s in salas:
                sala = Sala.from_dict(s)
                result.append(sala.to_json())
            
            return jsonify(result), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    return _get()

# Obtener una sala por ID
@salas_bp.route('/<id>', methods=['GET'])
def get_sala(id):
    from auth import token_required
    
    @token_required
    def _get(user_data, id):
        try:
            collection = db.get_collection('salas')
            sala_data = collection.find_one({'_id': ObjectId(id)})
            
            if not sala_data:
                return jsonify({'error': 'Sala no encontrada'}), 404
            
            sala = Sala.from_dict(sala_data)
            return jsonify(sala.to_json()), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    return _get(id)

# Crear una nueva sala
@salas_bp.route('', methods=['POST'])
def create_sala():
    from auth import token_required
    
    @token_required
    def _create(user_data):
        try:
            data = request.get_json()
            
            # Validaciones
            if not data.get('nombre'):
                return jsonify({'error': 'El nombre es requerido'}), 400
            if not data.get('direccion'):
                return jsonify({'error': 'La dirección es requerida'}), 400
            if not data.get('coordenadas'):
                return jsonify({'error': 'Las coordenadas son requeridas'}), 400
            if not data['coordenadas'].get('latitud') or not data['coordenadas'].get('longitud'):
                return jsonify({'error': 'Coordenadas incompletas'}), 400
            
            # Las coordenadas vienen del frontend (usuario las seleccionó en el mapa)
            coordenadas = {
                'latitud': float(data['coordenadas']['latitud']),
                'longitud': float(data['coordenadas']['longitud'])
            }
            
            # Usar el email del usuario autenticado
            sala = Sala(
                nombre=data['nombre'],
                email_propietario=user_data['email'],
                direccion=data['direccion'],
                coordenadas=coordenadas
            )
            
            collection = db.get_collection('salas')
            result = collection.insert_one(sala.to_dict())
            
            sala._id = result.inserted_id
            return jsonify(sala.to_json()), 201
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    return _create()

# Actualizar una sala
@salas_bp.route('/<id>', methods=['PUT'])
def update_sala(id):
    try:
        data = request.get_json()
        collection = db.get_collection('salas')
        
        update_data = {}
        if 'nombre' in data:
            update_data['nombre'] = data['nombre']
        if 'email_propietario' in data:
            update_data['email_propietario'] = data['email_propietario']
        if 'direccion' in data:
            update_data['direccion'] = data['direccion']
        
        if not update_data:
            return jsonify({'error': 'No hay datos para actualizar'}), 400
        
        result = collection.update_one(
            {'_id': ObjectId(id)},
            {'$set': update_data}
        )
        
        if result.matched_count == 0:
            return jsonify({'error': 'Sala no encontrada'}), 404
        
        sala_data = collection.find_one({'_id': ObjectId(id)})
        sala = Sala.from_dict(sala_data)
        return jsonify(sala.to_json()), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Eliminar una sala
@salas_bp.route('/<id>', methods=['DELETE'])
def delete_sala(id):
    try:
        collection = db.get_collection('salas')
        result = collection.delete_one({'_id': ObjectId(id)})
        
        if result.deleted_count == 0:
            return jsonify({'error': 'Sala no encontrada'}), 404
        
        return jsonify({'message': 'Sala eliminada correctamente'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
