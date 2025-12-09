from functools import wraps
from flask import request, jsonify
import jwt
import os
from datetime import datetime, timedelta, timezone
from google.oauth2 import id_token
from google.auth.transport import requests
import requests as http_requests

#Logica de autenticación y autorización
JWT_SECRET = os.getenv('JWT_SECRET')
GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')

def create_jwt_token(user_data):
    """Crear un token JWT para el usuario autenticado"""
    payload = {
        'email': user_data['email'],
        'name': user_data.get('name', ''),
        'picture': user_data.get('picture', ''),
        'exp': datetime.now(timezone.utc) + timedelta(days=7),  # Expira en 7 días
        'iat': datetime.now(timezone.utc)
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm='HS256')
    return token

def verify_jwt_token(token):
    """Verificar y decodificar un token JWT"""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def verify_google_token(token):
    """Verificar un token de Google OAuth"""
    try:
        idinfo = id_token.verify_oauth2_token(
            token, 
            requests.Request(), 
            GOOGLE_CLIENT_ID
        )
        
        if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
            raise ValueError('Wrong issuer.')
        
        return {
            'email': idinfo['email'],
            'name': idinfo.get('name', ''),
            'picture': idinfo.get('picture', ''),
            'sub': idinfo['sub']
        }
    except Exception as e:
        print(f"Error verificando token de Google: {e}")
        return None

def token_required(f):
    """Decorador para proteger rutas que requieren autenticación"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Obtener el token del header Authorization
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(' ')[1]  # "Bearer TOKEN"
            except IndexError:
                return jsonify({'error': 'Token inválido'}), 401
        
        if not token:
            return jsonify({'error': 'Token no proporcionado'}), 401
        
        # Verificar el token
        user_data = verify_jwt_token(token)
        if not user_data:
            return jsonify({'error': 'Token inválido o expirado'}), 401
        
        # Pasar los datos del usuario a la función
        return f(user_data, *args, **kwargs)
    
    return decorated
