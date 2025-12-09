from bson import ObjectId
from datetime import datetime

class Sala:
    """
    Modelo para representar una Sala de cine en MongoDB.
    
    Atributos:
    - _id: ObjectId generado automáticamente por MongoDB
    - nombre: String - Nombre de la sala
    - email_propietario: String - Email del propietario
    - direccion: String - Dirección postal de la sala
    - coordenadas: Dict - Coordenadas GPS {'latitud': float, 'longitud': float}
    - created_at: DateTime - Fecha de creación del registro
    """
    
    def __init__(self, nombre, email_propietario, direccion, coordenadas=None, _id=None, created_at=None):
        self._id = _id if _id else ObjectId()
        self.nombre = nombre
        self.email_propietario = email_propietario
        self.direccion = direccion
        self.coordenadas = coordenadas if coordenadas else {}
        self.created_at = created_at if created_at else datetime.utcnow()
    
    def to_dict(self):
        """Convertir el objeto a diccionario para MongoDB"""
        return {
            '_id': self._id,
            'nombre': self.nombre,
            'email_propietario': self.email_propietario,
            'direccion': self.direccion,
            'coordenadas': self.coordenadas,
            'created_at': self.created_at
        }
    @staticmethod
    def from_dict(data):
        """Crear un objeto Sala desde un diccionario"""
        if not data:
            return None
        return Sala(
            _id=data.get('_id'),
            nombre=data.get('nombre'),
            email_propietario=data.get('email_propietario'),
            direccion=data.get('direccion'),
            coordenadas=data.get('coordenadas', {}),
            created_at=data.get('created_at')
        )
    def to_json(self):
        """Convertir a formato JSON serializable"""
        return {
            '_id': str(self._id),
            'nombre': self.nombre,
            'email_propietario': self.email_propietario,
            'direccion': self.direccion,
            'coordenadas': self.coordenadas,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }