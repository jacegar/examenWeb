from flask import Blueprint, request, jsonify
from bson import ObjectId
from datetime import datetime
from database import db
from models.proyeccion import Proyeccion

proyecciones_bp = Blueprint('proyecciones', __name__)

# Obtener todas las proyecciones
@proyecciones_bp.route('', methods=['GET'])
def get_proyecciones():
    from auth import token_required
    
    @token_required
    def _get(user_data):
        try:
            collection = db.get_collection('proyecciones')
            proyecciones = list(collection.find())
            
            result = []
            for p in proyecciones:
                proyeccion = Proyeccion.from_dict(p)
                result.append(proyeccion.to_json())
            
            return jsonify(result), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    return _get()

# Obtener una proyección por ID
@proyecciones_bp.route('/<id>', methods=['GET'])
def get_proyeccion(id):
    from auth import token_required
    
    @token_required
    def _get(user_data, id):
        try:
            collection = db.get_collection('proyecciones')
            proyeccion_data = collection.find_one({'_id': ObjectId(id)})
            
            if not proyeccion_data:
                return jsonify({'error': 'Proyección no encontrada'}), 404
            
            proyeccion = Proyeccion.from_dict(proyeccion_data)
            return jsonify(proyeccion.to_json()), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    return _get(id)

# Crear una nueva proyección
@proyecciones_bp.route('', methods=['POST'])
def create_proyeccion():
    from auth import token_required
    
    @token_required
    def _create(user_data):
        try:
            data = request.get_json()
            
            # Validaciones
            if not data.get('nombre_sala'):
                return jsonify({'error': 'El nombre de la sala es requerido'}), 400
            if not data.get('titulo_pelicula'):
                return jsonify({'error': 'El título de la película es requerido'}), 400
            if not data.get('fecha_proyeccion'):
                return jsonify({'error': 'La fecha de proyección es requerida'}), 400
            
            # Parsear la fecha
            try:
                fecha_proyeccion = datetime.fromisoformat(data['fecha_proyeccion'].replace('Z', '+00:00'))
            except:
                return jsonify({'error': 'Formato de fecha inválido. Use ISO 8601 (ej: 2025-12-09T19:00:00)'}), 400
            
            proyeccion = Proyeccion(
                nombre_sala=data['nombre_sala'],
                titulo_pelicula=data['titulo_pelicula'],
                fecha_proyeccion=fecha_proyeccion
            )
            
            collection = db.get_collection('proyecciones')
            result = collection.insert_one(proyeccion.to_dict())
            
            proyeccion._id = result.inserted_id
            return jsonify(proyeccion.to_json()), 201
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    return _create()

# Actualizar una proyección
@proyecciones_bp.route('/<id>', methods=['PUT'])
def update_proyeccion(id):
    try:
        data = request.get_json()
        collection = db.get_collection('proyecciones')
        
        update_data = {}
        if 'nombre_sala' in data:
            update_data['nombre_sala'] = data['nombre_sala']
        if 'titulo_pelicula' in data:
            update_data['titulo_pelicula'] = data['titulo_pelicula']
        if 'fecha_proyeccion' in data:
            try:
                update_data['fecha_proyeccion'] = datetime.fromisoformat(data['fecha_proyeccion'].replace('Z', '+00:00'))
            except:
                return jsonify({'error': 'Formato de fecha inválido'}), 400
        
        if not update_data:
            return jsonify({'error': 'No hay datos para actualizar'}), 400
        
        result = collection.update_one(
            {'_id': ObjectId(id)},
            {'$set': update_data}
        )
        
        if result.matched_count == 0:
            return jsonify({'error': 'Proyección no encontrada'}), 404
        
        proyeccion_data = collection.find_one({'_id': ObjectId(id)})
        proyeccion = Proyeccion.from_dict(proyeccion_data)
        return jsonify(proyeccion.to_json()), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Eliminar una proyección
@proyecciones_bp.route('/<id>', methods=['DELETE'])
def delete_proyeccion(id):
    try:
        collection = db.get_collection('proyecciones')
        result = collection.delete_one({'_id': ObjectId(id)})
        
        if result.deleted_count == 0:
            return jsonify({'error': 'Proyección no encontrada'}), 404
        
        return jsonify({'message': 'Proyección eliminada correctamente'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Buscar proyecciones por sala
@proyecciones_bp.route('/sala/<nombre_sala>', methods=['GET'])
def get_proyecciones_by_sala(nombre_sala):
    try:
        collection = db.get_collection('proyecciones')
        proyecciones = list(collection.find({'nombre_sala': nombre_sala}))
        
        result = []
        for p in proyecciones:
            proyeccion = Proyeccion.from_dict(p)
            result.append(proyeccion.to_json())
        
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Buscar proyecciones por película
@proyecciones_bp.route('/pelicula/<titulo_pelicula>', methods=['GET'])
def get_proyecciones_by_pelicula(titulo_pelicula):
    try:
        collection = db.get_collection('proyecciones')
        proyecciones = list(collection.find({'titulo_pelicula': titulo_pelicula}))
        
        result = []
        for p in proyecciones:
            proyeccion = Proyeccion.from_dict(p)
            result.append(proyeccion.to_json())
        
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
