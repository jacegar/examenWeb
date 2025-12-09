from flask import Blueprint, request, jsonify
from bson import ObjectId
from database import db
from models.pelicula import Pelicula

peliculas_bp = Blueprint('peliculas', __name__)

# Obtener todas las películas
@peliculas_bp.route('', methods=['GET'])
def get_peliculas():
    from auth import token_required
    
    @token_required
    def _get(user_data):
        try:
            collection = db.get_collection('peliculas')
            peliculas = list(collection.find())
            
            result = []
            for p in peliculas:
                pelicula = Pelicula.from_dict(p)
                result.append(pelicula.to_json())
            
            return jsonify(result), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    return _get()

# Obtener una película por ID
@peliculas_bp.route('/<id>', methods=['GET'])
def get_pelicula(id):
    from auth import token_required
    
    @token_required
    def _get(user_data, id):
        try:
            collection = db.get_collection('peliculas')
            pelicula_data = collection.find_one({'_id': ObjectId(id)})
            
            if not pelicula_data:
                return jsonify({'error': 'Película no encontrada'}), 404
            
            pelicula = Pelicula.from_dict(pelicula_data)
            return jsonify(pelicula.to_json()), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    return _get(id)

# Crear una nueva película
@peliculas_bp.route('', methods=['POST'])
def create_pelicula():
    from auth import token_required
    
    @token_required
    def _create(user_data):
        try:
            data = request.get_json()
            
            if not data.get('titulo'):
                return jsonify({'error': 'Título es requerido'}), 400
            
            # imagen_uri es opcional por ahora (se añadirá con Cloudinary después)
            pelicula = Pelicula(
                titulo=data['titulo'],
                imagen_uri=data.get('imagen_uri', '')
            )
            
            collection = db.get_collection('peliculas')
            result = collection.insert_one(pelicula.to_dict())
            
            pelicula._id = result.inserted_id
            return jsonify(pelicula.to_json()), 201
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    return _create()

# Actualizar una película
@peliculas_bp.route('/<id>', methods=['PUT'])
def update_pelicula(id):
    try:
        data = request.get_json()
        collection = db.get_collection('peliculas')
        
        update_data = {}
        if 'titulo' in data:
            update_data['titulo'] = data['titulo']
        if 'imagen_uri' in data:
            update_data['imagen_uri'] = data['imagen_uri']
        
        if not update_data:
            return jsonify({'error': 'No hay datos para actualizar'}), 400
        
        result = collection.update_one(
            {'_id': ObjectId(id)},
            {'$set': update_data}
        )
        
        if result.matched_count == 0:
            return jsonify({'error': 'Película no encontrada'}), 404
        
        pelicula_data = collection.find_one({'_id': ObjectId(id)})
        pelicula = Pelicula.from_dict(pelicula_data)
        return jsonify(pelicula.to_json()), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Eliminar una película
@peliculas_bp.route('/<id>', methods=['DELETE'])
def delete_pelicula(id):
    try:
        collection = db.get_collection('peliculas')
        result = collection.delete_one({'_id': ObjectId(id)})
        
        if result.deleted_count == 0:
            return jsonify({'error': 'Película no encontrada'}), 404
        
        return jsonify({'message': 'Película eliminada exitosamente'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Buscar película por título y obtener sus proyecciones
@peliculas_bp.route('/buscar/<titulo>', methods=['GET'])
def buscar_pelicula(titulo):
    from auth import token_required
    
    @token_required
    def _buscar(user_data, titulo):
        try:
            # Buscar la película por título (case insensitive)
            peliculas_collection = db.get_collection('peliculas')
            pelicula_data = peliculas_collection.find_one(
                {'titulo': {'$regex': f'^{titulo}$', '$options': 'i'}}
            )
            
            if not pelicula_data:
                return jsonify({'error': 'Película no encontrada'}), 404
            
            pelicula = Pelicula.from_dict(pelicula_data)
            
            # Buscar las proyecciones de esta película
            proyecciones_collection = db.get_collection('proyecciones')
            proyecciones = list(proyecciones_collection.find(
                {'titulo_pelicula': {'$regex': f'^{titulo}$', '$options': 'i'}}
            ))
            
            # Obtener información de las salas
            salas_collection = db.get_collection('salas')
            proyecciones_con_sala = []
            
            for proy in proyecciones:
                sala_data = salas_collection.find_one(
                    {'nombre': {'$regex': f'^{proy["nombre_sala"]}$', '$options': 'i'}}
                )
                
                proyecciones_con_sala.append({
                    'fecha_proyeccion': proy['fecha_proyeccion'].isoformat(),
                    'sala': {
                        'nombre': sala_data['nombre'] if sala_data else proy['nombre_sala'],
                        'direccion': sala_data.get('direccion', '') if sala_data else '',
                        'email_propietario': sala_data.get('email_propietario', '') if sala_data else '',
                        'coordenadas': sala_data.get('coordenadas', {}) if sala_data else {}
                    }
                })
            
            return jsonify({
                'pelicula': pelicula.to_json(),
                'proyecciones': proyecciones_con_sala
            }), 200
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    return _buscar(titulo)
