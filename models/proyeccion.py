from bson import ObjectId
from datetime import datetime

class Proyeccion:
    """
    Modelo para representar una Proyección en MongoDB.
    
    Atributos:
    - _id: ObjectId generado automáticamente por MongoDB
    - nombre_sala: String - Nombre de la sala donde se proyecta
    - titulo_pelicula: String - Título de la película proyectada
    - fecha_proyeccion: DateTime - Fecha y hora de la proyección
    - created_at: DateTime - Fecha de creación del registro

    """
    
    def __init__(self, nombre_sala, titulo_pelicula, fecha_proyeccion, _id=None, created_at=None):
        self._id = _id if _id else ObjectId()
        self.nombre_sala = nombre_sala
        self.titulo_pelicula = titulo_pelicula
        self.fecha_proyeccion = fecha_proyeccion
        self.created_at = created_at if created_at else datetime.utcnow()
    
    def to_dict(self):
        """Convertir el objeto a diccionario para MongoDB"""
        return {
            '_id': self._id,
            'nombre_sala': self.nombre_sala,
            'titulo_pelicula': self.titulo_pelicula,
            'fecha_proyeccion': self.fecha_proyeccion,
            'created_at': self.created_at
        }
    
    @staticmethod
    def from_dict(data):
        """Crear un objeto Proyeccion desde un diccionario"""
        if not data:
            return None
        return Proyeccion(
            _id=data.get('_id'),
            nombre_sala=data.get('nombre_sala'),
            titulo_pelicula=data.get('titulo_pelicula'),
            fecha_proyeccion=data.get('fecha_proyeccion'),
            created_at=data.get('created_at')
        )
    
    def to_json(self):
        """Convertir a formato JSON serializable"""
        return {
            '_id': str(self._id),
            'nombre_sala': self.nombre_sala,
            'titulo_pelicula': self.titulo_pelicula,
            'fecha_proyeccion': self.fecha_proyeccion.isoformat() if isinstance(self.fecha_proyeccion, datetime) else self.fecha_proyeccion,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
