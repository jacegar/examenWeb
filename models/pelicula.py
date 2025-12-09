from bson import ObjectId
from datetime import datetime

class Pelicula:
    """
    Modelo para representar una Película en MongoDB.
    
    Atributos:
    - _id: ObjectId generado automáticamente por MongoDB
    - titulo: String - Título de la película
    - imagen_uri: String - URI de la imagen del cartel
    - created_at: DateTime - Fecha de creación del registro
    """
    
    def __init__(self, titulo, imagen_uri, _id=None, created_at=None):
        self._id = _id if _id else ObjectId()
        self.titulo = titulo
        self.imagen_uri = imagen_uri
        self.created_at = created_at if created_at else datetime.utcnow()
    
    def to_dict(self):
        """Convertir el objeto a diccionario para MongoDB"""
        return {
            '_id': self._id,
            'titulo': self.titulo,
            'imagen_uri': self.imagen_uri,
            'created_at': self.created_at
        }
    
    @staticmethod
    def from_dict(data):
        """Crear un objeto Pelicula desde un diccionario"""
        if not data:
            return None
        return Pelicula(
            _id=data.get('_id'),
            titulo=data.get('titulo'),
            imagen_uri=data.get('imagen_uri'),
            created_at=data.get('created_at')
        )
    
    def to_json(self):
        """Convertir a formato JSON serializable"""
        return {
            '_id': str(self._id),
            'titulo': self.titulo,
            'imagen_uri': self.imagen_uri,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
