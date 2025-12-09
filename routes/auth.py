from flask import Blueprint, request, jsonify, redirect, session
from auth import verify_google_token, create_jwt_token
import os

auth_bp = Blueprint('auth', __name__)

# Endpoints de autenticación
@auth_bp.route('/google', methods=['POST'])
def google_login():
    """Endpoint para autenticación con Google"""
    try:
        data = request.get_json()
        google_token = data.get('token')
        
        if not google_token:
            return jsonify({'error': 'Token de Google no proporcionado'}), 400
        
        # Verificar el token de Google
        user_data = verify_google_token(google_token)
        
        if not user_data:
            return jsonify({'error': 'Token de Google inválido'}), 401
        
        # Crear nuestro propio JWT
        jwt_token = create_jwt_token(user_data)
        
        return jsonify({
            'token': jwt_token,
            'user': {
                'email': user_data['email'],
                'name': user_data['name'],
                'picture': user_data['picture']
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/verify', methods=['GET'])
def verify_token():
    """Verificar si un token JWT es válido"""
    from auth import verify_jwt_token
    
    token = None
    if 'Authorization' in request.headers:
        auth_header = request.headers['Authorization']
        try:
            token = auth_header.split(' ')[1]
        except IndexError:
            return jsonify({'error': 'Token inválido'}), 401
    
    if not token:
        return jsonify({'error': 'Token no proporcionado'}), 401
    
    user_data = verify_jwt_token(token)
    if not user_data:
        return jsonify({'error': 'Token inválido o expirado'}), 401
    
    return jsonify({
        'valid': True,
        'user': {
            'email': user_data['email'],
            'name': user_data.get('name', ''),
            'picture': user_data.get('picture', '')
        }
    }), 200
