import cloudinary
import cloudinary.uploader
import os
from dotenv import load_dotenv

load_dotenv()

# Configurar Cloudinary
cloudinary.config(
    cloudinary_url=os.getenv('CLOUDINARY_URL')
)

def upload_image(file, folder="reviews"):
    """
    Subir una imagen a Cloudinary
    
    Args:
        file: Archivo de imagen (FileStorage de Flask)
        folder: Carpeta en Cloudinary donde guardar la imagen
        
    Returns:
        dict: Diccionario con 'url' y 'public_id' si éxito, None si falla
    """
    try:
        # Subir imagen a Cloudinary
        result = cloudinary.uploader.upload(
            file,
            folder=folder,
            resource_type="image",
            transformation=[
                {'width': 800, 'height': 600, 'crop': 'limit'},  # Limitar tamaño máximo
                {'quality': 'auto'}  # Optimización automática
            ]
        )
        
        return {
            'url': result.get('secure_url'),
            'public_id': result.get('public_id')
        }
    except Exception as e:
        print(f"Error subiendo imagen a Cloudinary: {e}")
        return None

def delete_image(public_id):
    """
    Eliminar una imagen de Cloudinary
    
    Args:
        public_id: ID público de la imagen en Cloudinary
        
    Returns:
        bool: True si se eliminó exitosamente, False si falló
    """
    try:
        result = cloudinary.uploader.destroy(public_id)
        return result.get('result') == 'ok'
    except Exception as e:
        print(f"Error eliminando imagen de Cloudinary: {e}")
        return False

def get_image_url(public_id, transformations=None):
    """
    Obtener URL de una imagen con transformaciones opcionales
    
    Args:
        public_id: ID público de la imagen
        transformations: Lista de transformaciones a aplicar
        
    Returns:
        str: URL de la imagen
    """
    try:
        if transformations:
            return cloudinary.CloudinaryImage(public_id).build_url(transformation=transformations)
        return cloudinary.CloudinaryImage(public_id).build_url()
    except Exception as e:
        print(f"Error obteniendo URL de imagen: {e}")
        return None
