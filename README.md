# CineWeb - Sistema de Gestión de Cines
## ✨ Características Implementadas

## 🚀 Instalación Local

1. **Activar el entorno virtual**
```bash
source .venv/bin/activate
```

2. **Instalar dependencias**
```bash
pip install -r requirements.txt
```

3. **Configurar variables de entorno**
El archivo `.env` ya está configurado con:
- MongoDB Atlas
- Cloudinary (para futuro uso)
- Google OAuth credentials
- Secrets JWT y sesión

4. **Ejecutar la aplicación**
```bash
python app.py
```

La aplicación estará disponible en `http://localhost:5000`
## 🌐 Despliegue en Vercel

1. **Instalar Vercel CLI**
```bash
npm i -g vercel
```

2. **Desplegar**
```bash
vercel
```

3. **Configurar variables de entorno en Vercel**
Añadir en la configuración del proyecto todas las variables del `.env`

4. **Actualizar Google OAuth Console**
Añadir el dominio de Vercel a las URIs autorizadas

## 🛠️ Tecnologías

- **Backend**: Flask (Python)
- **Base de datos**: MongoDB Atlas
- **Autenticación**: Google OAuth 2.0 + JWT
- **Imágenes**: Cloudinary (upload desacoplado)
- **Mapas**: Leaflet.js + OpenStreetMap
- **Geocoding**: Nominatim API (autocompletado de direcciones)
- **Frontend**: HTML5 + CSS3 + JavaScript (Vanilla)
- **Despliegue**: Vercel