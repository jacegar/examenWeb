from pymongo import MongoClient
from dotenv import load_dotenv
import os

# Cargar variables de entorno
load_dotenv()

class Database:
    def __init__(self):
        self.client = None
        self.db = None
        
    def connect(self):
        """Conectar a MongoDB Atlas"""
        if self.client is None:
            mongodb_uri = os.getenv('MONGODB_URI')
            self.client = MongoClient(mongodb_uri)
            # Obtener el nombre de la base de datos de la URI o usar uno por defecto
            self.db = self.client['cineweb']
            print("Conectado a MongoDB Atlas")
        return self.db
    
    def get_collection(self, collection_name):
        """Obtener una colección específica"""
        if self.db is None:
            self.connect()
        return self.db[collection_name]
    
    def close(self):
        """Cerrar la conexión"""
        if self.client:
            self.client.close()
            print("Conexión cerrada")

# Instancia global de la base de datos
db = Database()
