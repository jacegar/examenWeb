import requests
from typing import Optional, Dict

def geocode_address(address: str) -> Optional[Dict[str, float]]:
    """
    Convertir una dirección postal en coordenadas GPS usando Nominatim (OpenStreetMap)
    
    Args:
        address: Dirección postal a geocodificar
        
    Returns:
        dict: {'latitud': float, 'longitud': float} o None si falla
    """
    try:
        # API de Nominatim (OpenStreetMap)
        base_url = "https://nominatim.openstreetmap.org/search"
        
        params = {
            'q': address,
            'format': 'json',
            'limit': 1,
            'addressdetails': 1
        }
        
        headers = {
            'User-Agent': 'CineWeb/1.0 (Educational Project)'  # Requerido por Nominatim
        }
        
        response = requests.get(base_url, params=params, headers=headers, timeout=5)
        response.raise_for_status()
        
        results = response.json()
        
        if results and len(results) > 0:
            location = results[0]
            return {
                'latitud': float(location['lat']),
                'longitud': float(location['lon'])
            }
        
        return None
        
    except Exception as e:
        print(f"Error en geocoding: {e}")
        return None

def reverse_geocode(latitud: float, longitud: float) -> Optional[str]:
    """
    Convertir coordenadas GPS en dirección postal (geocoding inverso)
    
    Args:
        latitud: Latitud
        longitud: Longitud
        
    Returns:
        str: Dirección formateada o None si falla
    """
    try:
        base_url = "https://nominatim.openstreetmap.org/reverse"
        
        params = {
            'lat': latitud,
            'lon': longitud,
            'format': 'json',
            'addressdetails': 1
        }
        
        headers = {
            'User-Agent': 'CineWeb/1.0 (Educational Project)'
        }
        
        response = requests.get(base_url, params=params, headers=headers, timeout=5)
        response.raise_for_status()
        
        result = response.json()
        
        return result.get('display_name')
        
    except Exception as e:
        print(f"Error en reverse geocoding: {e}")
        return None

def get_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calcular distancia entre dos puntos GPS (en kilómetros)
    Fórmula de Haversine
    
    Args:
        lat1, lon1: Coordenadas del primer punto
        lat2, lon2: Coordenadas del segundo punto
        
    Returns:
        float: Distancia en kilómetros
    """
    from math import radians, sin, cos, sqrt, atan2
    
    R = 6371  # Radio de la Tierra en km
    
    lat1_rad = radians(lat1)
    lat2_rad = radians(lat2)
    delta_lat = radians(lat2 - lat1)
    delta_lon = radians(lon2 - lon1)
    
    a = sin(delta_lat/2)**2 + cos(lat1_rad) * cos(lat2_rad) * sin(delta_lon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    
    distance = R * c
    return distance
