from flask import Blueprint, request, jsonify
from services.cloudinary_service import upload_image, delete_image
from auth import token_required

upload_bp = Blueprint('upload', __name__)

@upload_bp.route('/image', methods=['POST'])
def upload_image_endpoint():
    """
    Endpoint genérico para subir imágenes a Cloudinary
    Puede ser usado para películas, salas, o cualquier otra entidad
    """
    from auth import token_required
    
    @token_required
    def _upload(user_data):
        try:
            # Verificar que se envió un archivo
            if 'image' not in request.files:
                return jsonify({'error': 'No se proporcionó ninguna imagen'}), 400
            
            file = request.files['image']
            
            # Verificar que el archivo no esté vacío
            if file.filename == '':
                return jsonify({'error': 'No se seleccionó ningún archivo'}), 400
            
            # Verificar el tipo de archivo
            allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
            file_extension = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
            
            if file_extension not in allowed_extensions:
                return jsonify({'error': f'Tipo de archivo no permitido. Use: {", ".join(allowed_extensions)}'}), 400
            
            # Obtener carpeta opcional del query string
            folder = request.args.get('folder', 'cineweb')
            
            # Subir imagen a Cloudinary
            result = upload_image(file, folder=folder)
            
            if not result:
                return jsonify({'error': 'Error al subir la imagen a Cloudinary'}), 500
            
            return jsonify({
                'message': 'Imagen subida exitosamente',
                'url': result['url'],
                'public_id': result['public_id']
            }), 200
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    return _upload()

@upload_bp.route('/image/<path:public_id>', methods=['DELETE'])
def delete_image_endpoint(public_id):
    """
    Endpoint para eliminar imágenes de Cloudinary
    """
    from auth import token_required
    
    @token_required
    def _delete(user_data, public_id):
        try:
            # Eliminar imagen
            success = delete_image(public_id)
            
            if not success:
                return jsonify({'error': 'Error al eliminar la imagen'}), 500
            
            return jsonify({'message': 'Imagen eliminada exitosamente'}), 200
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    return _delete(public_id)
