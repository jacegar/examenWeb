from bson import ObjectId
from datetime import datetime

class Resena:
    """
    Modelo para representar una Reseña en MongoDB.
    
    Atributos:
    - _id: ObjectId generado automáticamente por MongoDB
    - nombre_establecimiento: String - Nombre del establecimiento
    - direccion: String - Dirección postal del establecimiento
    - latitud: Float - Coordenada GPS latitud
    - longitud: Float - Coordenada GPS longitud
    - valoracion: Int - Valoración de 1 a 5 estrellas
    - imagenes_uri: List[String] - Lista de URIs de imágenes
    - autor_email: String - Email del autor
    - autor_nombre: String - Nombre del autor
    - token: String - Token OAuth usado para crear la reseña
    - token_emision: DateTime - Timestamp de emisión del token
    - token_caducidad: DateTime - Timestamp de caducidad del token
    - created_at: DateTime - Fecha de creación del registro
    """
    
    def __init__(self, nombre_establecimiento, direccion, latitud, longitud, 
                 valoracion, imagenes_uri, autor_email, autor_nombre, token, 
                 token_emision, token_caducidad, _id=None, created_at=None):
        self._id = _id if _id else ObjectId()
        self.nombre_establecimiento = nombre_establecimiento
        self.direccion = direccion
        self.latitud = latitud
        self.longitud = longitud
        self.valoracion = valoracion
        self.imagenes_uri = imagenes_uri if imagenes_uri else []
        self.autor_email = autor_email
        self.autor_nombre = autor_nombre
        self.token = token
        self.token_emision = token_emision
        self.token_caducidad = token_caducidad
        self.created_at = created_at if created_at else datetime.utcnow()
    
    def to_dict(self):
        """Convertir el objeto a diccionario para MongoDB"""
        return {
            '_id': self._id,
            'nombre_establecimiento': self.nombre_establecimiento,
            'direccion': self.direccion,
            'latitud': self.latitud,
            'longitud': self.longitud,
            'valoracion': self.valoracion,
            'imagenes_uri': self.imagenes_uri,
            'autor_email': self.autor_email,
            'autor_nombre': self.autor_nombre,
            'token': self.token,
            'token_emision': self.token_emision,
            'token_caducidad': self.token_caducidad,
            'created_at': self.created_at
        }
    
    @staticmethod
    def from_dict(data):
        """Crear un objeto Resena desde un diccionario"""
        if not data:
            return None
        return Resena(
            _id=data.get('_id'),
            nombre_establecimiento=data.get('nombre_establecimiento'),
            direccion=data.get('direccion'),
            latitud=data.get('latitud'),
            longitud=data.get('longitud'),
            valoracion=data.get('valoracion'),
            imagenes_uri=data.get('imagenes_uri', []),
            autor_email=data.get('autor_email'),
            autor_nombre=data.get('autor_nombre'),
            token=data.get('token'),
            token_emision=data.get('token_emision'),
            token_caducidad=data.get('token_caducidad'),
            created_at=data.get('created_at')
        )
    
    def to_json(self):
        """Convertir a formato JSON serializable"""
        return {
            '_id': str(self._id),
            'nombre_establecimiento': self.nombre_establecimiento,
            'direccion': self.direccion,
            'latitud': self.latitud,
            'longitud': self.longitud,
            'valoracion': self.valoracion,
            'imagenes_uri': self.imagenes_uri,
            'autor_email': self.autor_email,
            'autor_nombre': self.autor_nombre,
            'token': self.token,
            'token_emision': self.token_emision.isoformat() if self.token_emision else None,
            'token_caducidad': self.token_caducidad.isoformat() if self.token_caducidad else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
