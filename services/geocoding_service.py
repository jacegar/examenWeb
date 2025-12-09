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