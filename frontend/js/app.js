// Variables globales
let token = null;
let userData = null;

// Configuración de la API
const API_URL = window.location.origin;

// Inicialización
document.addEventListener('DOMContentLoaded', () => {
    checkAuth();
    setupEventListeners();
});

// Verificar autenticación al cargar
function checkAuth() {
    token = localStorage.getItem('token');
    if (token) {
        verifyToken();
    } else {
        showLogin();
    }
}

// Verificar validez del token
async function verifyToken() {
    try {
        const response = await fetch(`${API_URL}/api/auth/verify`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (response.ok) {
            const data = await response.json();
            userData = data.user;
            showApp();
        } else {
            showLogin();
        }
    } catch (error) {
        console.error('Error verificando token:', error);
        showLogin();
    }
}

// Callback de Google Sign-In
function handleCredentialResponse(response) {
    const googleToken = response.credential;
    
    fetch(`${API_URL}/api/auth/google`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ token: googleToken })
    })
    .then(res => res.json())
    .then(data => {
        if (data.token) {
            token = data.token;
            userData = data.user;
            localStorage.setItem('token', token);
            showApp();
        } else {
            showNotification('Error al iniciar sesión', 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showNotification('Error al iniciar sesión', 'error');
    });
}

// Cerrar sesión
function logout() {
    token = null;
    userData = null;
    localStorage.removeItem('token');
    showLogin();
}

// Mostrar pantalla de login
function showLogin() {
    document.getElementById('login-screen').classList.add('active');
    document.getElementById('app-screen').classList.remove('active');
}

// Mostrar aplicación
function showApp() {
    document.getElementById('login-screen').classList.remove('active');
    document.getElementById('app-screen').classList.add('active');
    
    // Actualizar info del usuario
    document.getElementById('user-name').textContent = userData.name;
    document.getElementById('sala-email').value = userData.email;
    
    // Cargar datos iniciales
    loadPeliculas();
    loadSalas();
    loadProyecciones();
}

// Setup de event listeners
function setupEventListeners() {
    document.getElementById('form-pelicula').addEventListener('submit', createPelicula);
    document.getElementById('form-sala').addEventListener('submit', createSala);
    document.getElementById('form-proyeccion').addEventListener('submit', createProyeccion);
    document.getElementById('form-buscar').addEventListener('submit', buscarPelicula);
    
    // Preview de imagen al seleccionar archivo
    document.getElementById('pelicula-cartel').addEventListener('change', function(e) {
        const file = e.target.files[0];
        const preview = document.getElementById('preview-pelicula');
        
        if (file) {
            const reader = new FileReader();
            reader.onload = function(e) {
                preview.innerHTML = `<img src="${e.target.result}" alt="Preview">`;
                preview.classList.add('active');
            };
            reader.readAsDataURL(file);
        } else {
            preview.innerHTML = '';
            preview.classList.remove('active');
        }
    });
    
    // Autocompletado de direcciones
    setupAddressAutocomplete();
}

// Mostrar tab
function showTab(tabName) {
    // Ocultar todos los tabs
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.remove('active');
    });
    document.querySelectorAll('.tab').forEach(tab => {
        tab.classList.remove('active');
    });
    
    // Mostrar tab seleccionado
    document.getElementById(`tab-${tabName}`).classList.add('active');
    event.target.classList.add('active');
    
    // Recargar datos si es necesario
    if (tabName === 'proyecciones') {
        loadPeliculasForDatalist();
        loadSalasForDatalist();
    }
    if (tabName === 'buscar') {
        loadPeliculasForSearch();
    }
}

// ============ PELÍCULAS ============

async function loadPeliculas() {
    try {
        const response = await fetch(`${API_URL}/api/peliculas`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (!response.ok) {
            if (response.status === 401) {
                logout();
                return;
            }
            throw new Error('Error al cargar películas');
        }
        
        const peliculas = await response.json();
        displayPeliculas(peliculas);
    } catch (error) {
        console.error('Error:', error);
        showNotification('Error al cargar películas', 'error');
    }
}

function displayPeliculas(peliculas) {
    const container = document.getElementById('peliculas-list');
    
    if (peliculas.length === 0) {
        container.innerHTML = '<div class="empty-state"><h3>No hay películas</h3><p>Crea tu primera película usando el formulario de arriba</p></div>';
        return;
    }
    
    container.innerHTML = peliculas.map(pelicula => `
        <div class="item-card">
            ${pelicula.imagen_uri ? `<img src="${pelicula.imagen_uri}" alt="${pelicula.titulo}" class="poster">` : '<div class="poster" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); display: flex; align-items: center; justify-content: center; color: white; font-size: 3rem;">🎬</div>'}
            <h3>${pelicula.titulo}</h3>
            <p><small>Creada el ${new Date(pelicula.created_at).toLocaleDateString()}</small></p>
        </div>
    `).join('');
}

async function createPelicula(e) {
    e.preventDefault();
    
    const titulo = document.getElementById('pelicula-titulo').value;
    const fileInput = document.getElementById('pelicula-cartel');
    const file = fileInput.files[0];
    
    // Mostrar estado de carga
    const btnText = document.getElementById('btn-pelicula-text');
    const btnLoading = document.getElementById('btn-pelicula-loading');
    btnText.style.display = 'none';
    btnLoading.style.display = 'inline';
    
    try {
        let imagen_uri = '';
        
        // Si hay un archivo, subirlo a Cloudinary primero
        if (file) {
            const uploadResult = await uploadImageToCloudinary(file, 'peliculas');
            if (uploadResult) {
                imagen_uri = uploadResult.url;
            } else {
                throw new Error('Error al subir la imagen');
            }
        }
        
        // Crear la película con la URL de la imagen
        const response = await fetch(`${API_URL}/api/peliculas`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({
                titulo: titulo,
                imagen_uri: imagen_uri
            })
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Error al crear película');
        }
        
        showNotification('Película creada exitosamente', 'success');
        document.getElementById('form-pelicula').reset();
        document.getElementById('preview-pelicula').innerHTML = '';
        document.getElementById('preview-pelicula').classList.remove('active');
        loadPeliculas();
    } catch (error) {
        console.error('Error:', error);
        showNotification(error.message, 'error');
    } finally {
        // Restaurar botón
        btnText.style.display = 'inline';
        btnLoading.style.display = 'none';
    }
}

// ============ CLOUDINARY ============

async function uploadImageToCloudinary(file, folder = 'cineweb') {
    try {
        const formData = new FormData();
        formData.append('image', file);
        
        const response = await fetch(`${API_URL}/api/upload/image?folder=${folder}`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`
            },
            body: formData
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Error al subir imagen');
        }
        
        const data = await response.json();
        return {
            url: data.url,
            public_id: data.public_id
        };
    } catch (error) {
        console.error('Error subiendo imagen:', error);
        showNotification(error.message, 'error');
        return null;
    }
}

// ============ SALAS ============

async function loadSalas() {
    try {
        const response = await fetch(`${API_URL}/api/salas`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (!response.ok) {
            if (response.status === 401) {
                logout();
                return;
            }
            throw new Error('Error al cargar salas');
        }
        
        const salas = await response.json();
        displaySalas(salas);
    } catch (error) {
        console.error('Error:', error);
        showNotification('Error al cargar salas', 'error');
    }
}

function displaySalas(salas) {
    const container = document.getElementById('salas-list');
    
    if (salas.length === 0) {
        container.innerHTML = '<div class="empty-state"><h3>No hay salas</h3><p>Crea tu primera sala usando el formulario de arriba</p></div>';
        return;
    }
    
    container.innerHTML = salas.map(sala => `
        <div class="item-card">
            <h3>${sala.nombre}</h3>
            <p>📍 ${sala.direccion}</p>
            <p>👤 ${sala.email_propietario}</p>
            <p><small>Creada el ${new Date(sala.created_at).toLocaleDateString()}</small></p>
        </div>
    `).join('');
}

async function createSala(e) {
    e.preventDefault();
    
    const nombre = document.getElementById('sala-nombre').value;
    const direccion = document.getElementById('sala-direccion').value;
    const latitud = parseFloat(document.getElementById('sala-latitud').value);
    const longitud = parseFloat(document.getElementById('sala-longitud').value);
    
    // Validar que se hayan seleccionado coordenadas
    if (!latitud || !longitud) {
        showNotification('Por favor selecciona una dirección del mapa', 'error');
        return;
    }
    
    try {
        const response = await fetch(`${API_URL}/api/salas`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({
                nombre: nombre,
                direccion: direccion,
                coordenadas: {
                    latitud: latitud,
                    longitud: longitud
                }
            })
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Error al crear sala');
        }
        
        showNotification('Sala creada exitosamente', 'success');
        document.getElementById('form-sala').reset();
        document.getElementById('sala-email').value = userData.email;
        
        // Limpiar mapa
        if (window.mapaSala) {
            window.mapaSala.remove();
            window.mapaSala = null;
        }
        document.getElementById('mapa-sala-container').style.display = 'none';
        
        loadSalas();
    } catch (error) {
        console.error('Error:', error);
        showNotification(error.message, 'error');
    }
}

// ============ AUTOCOMPLETADO DE DIRECCIONES ============

let autocompleteTimeout = null;

function setupAddressAutocomplete() {
    const input = document.getElementById('sala-direccion');
    const suggestionsDiv = document.getElementById('direccion-suggestions');
    
    input.addEventListener('input', function() {
        const query = this.value.trim();
        
        // Limpiar timeout anterior
        if (autocompleteTimeout) {
            clearTimeout(autocompleteTimeout);
        }
        
        if (query.length < 3) {
            suggestionsDiv.classList.remove('active');
            return;
        }
        
        // Debounce: esperar 500ms después del último keystroke
        autocompleteTimeout = setTimeout(() => {
            searchAddresses(query);
        }, 500);
    });
    
    // Cerrar sugerencias al hacer clic fuera
    document.addEventListener('click', function(e) {
        if (!input.contains(e.target) && !suggestionsDiv.contains(e.target)) {
            suggestionsDiv.classList.remove('active');
        }
    });
}

async function searchAddresses(query) {
    try {
        const response = await fetch(
            `https://nominatim.openstreetmap.org/search?q=${encodeURIComponent(query)}&format=json&limit=5&addressdetails=1`,
            {
                headers: {
                    'User-Agent': 'CineWeb/1.0'
                }
            }
        );
        
        if (!response.ok) {
            throw new Error('Error en la búsqueda de direcciones');
        }
        
        const results = await response.json();
        displayAddressSuggestions(results);
    } catch (error) {
        console.error('Error buscando direcciones:', error);
    }
}

function displayAddressSuggestions(results) {
    const suggestionsDiv = document.getElementById('direccion-suggestions');
    
    if (results.length === 0) {
        suggestionsDiv.innerHTML = '<div class="suggestion-item"><small>No se encontraron resultados</small></div>';
        suggestionsDiv.classList.add('active');
        return;
    }
    
    suggestionsDiv.innerHTML = results.map(result => `
        <div class="suggestion-item" onclick="selectAddress('${result.lat}', '${result.lon}', '${result.display_name.replace(/'/g, "\\'")}')">
            <strong>${result.display_name.split(',')[0]}</strong>
            <small>${result.display_name}</small>
        </div>
    `).join('');
    
    suggestionsDiv.classList.add('active');
}

function selectAddress(lat, lon, displayName) {
    // Rellenar input con la dirección seleccionada
    document.getElementById('sala-direccion').value = displayName;
    
    // Guardar coordenadas
    document.getElementById('sala-latitud').value = lat;
    document.getElementById('sala-longitud').value = lon;
    
    // Ocultar sugerencias
    document.getElementById('direccion-suggestions').classList.remove('active');
    
    // Mostrar mapa para ajuste fino
    showLocationMap(parseFloat(lat), parseFloat(lon), displayName);
}

function showLocationMap(lat, lon, address) {
    const container = document.getElementById('mapa-sala-container');
    const mapDiv = document.getElementById('mapa-sala');
    
    // Mostrar contenedor
    container.style.display = 'block';
    
    // Limpiar mapa anterior si existe
    if (window.mapaSala) {
        window.mapaSala.remove();
    }
    
    // Crear nuevo mapa
    window.mapaSala = L.map('mapa-sala').setView([lat, lon], 16);
    
    // Añadir tiles de OpenStreetMap
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors',
        maxZoom: 19
    }).addTo(window.mapaSala);
    
    // Crear marcador arrastrable
    const marker = L.marker([lat, lon], {
        draggable: true,
        icon: L.icon({
            iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-red.png',
            shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',
            iconSize: [25, 41],
            iconAnchor: [12, 41],
            popupAnchor: [1, -34],
            shadowSize: [41, 41]
        })
    }).addTo(window.mapaSala);
    
    marker.bindPopup(`<strong>📍 ${address}</strong><br><small>Arrastra para ajustar</small>`).openPopup();
    
    // Actualizar coordenadas cuando se arrastra el marcador
    marker.on('dragend', function(e) {
        const position = marker.getLatLng();
        document.getElementById('sala-latitud').value = position.lat;
        document.getElementById('sala-longitud').value = position.lng;
        marker.setPopupContent(`<strong>📍 Ubicación ajustada</strong><br><small>Lat: ${position.lat.toFixed(6)}, Lng: ${position.lng.toFixed(6)}</small>`);
    });
    
    // Scroll suave al mapa
    container.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

// ============ PROYECCIONES ============

async function loadProyecciones() {
    try {
        const response = await fetch(`${API_URL}/api/proyecciones`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (!response.ok) {
            if (response.status === 401) {
                logout();
                return;
            }
            throw new Error('Error al cargar proyecciones');
        }
        
        const proyecciones = await response.json();
        displayProyecciones(proyecciones);
    } catch (error) {
        console.error('Error:', error);
        showNotification('Error al cargar proyecciones', 'error');
    }
}

function displayProyecciones(proyecciones) {
    const container = document.getElementById('proyecciones-list');
    
    if (proyecciones.length === 0) {
        container.innerHTML = '<div class="empty-state"><h3>No hay proyecciones</h3><p>Asigna tu primera proyección usando el formulario de arriba</p></div>';
        return;
    }
    
    container.innerHTML = proyecciones.map(proyeccion => `
        <div class="item-card">
            <h3>🎬 ${proyeccion.titulo_pelicula}</h3>
            <p>🏛️ ${proyeccion.nombre_sala}</p>
            <p>📅 ${new Date(proyeccion.fecha_proyeccion).toLocaleString('es-ES', {
                dateStyle: 'full',
                timeStyle: 'short'
            })}</p>
        </div>
    `).join('');
}

async function createProyeccion(e) {
    e.preventDefault();
    
    const pelicula = document.getElementById('proyeccion-pelicula').value;
    const sala = document.getElementById('proyeccion-sala').value;
    const fecha = document.getElementById('proyeccion-fecha').value;
    
    try {
        const response = await fetch(`${API_URL}/api/proyecciones`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({
                titulo_pelicula: pelicula,
                nombre_sala: sala,
                fecha_proyeccion: fecha
            })
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Error al crear proyección');
        }
        
        showNotification('Proyección asignada exitosamente', 'success');
        document.getElementById('form-proyeccion').reset();
        loadProyecciones();
    } catch (error) {
        console.error('Error:', error);
        showNotification(error.message, 'error');
    }
}

// Cargar películas para datalist
async function loadPeliculasForDatalist() {
    try {
        const response = await fetch(`${API_URL}/api/peliculas`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (response.ok) {
            const peliculas = await response.json();
            const datalist = document.getElementById('peliculas-datalist');
            datalist.innerHTML = peliculas.map(p => `<option value="${p.titulo}">`).join('');
        }
    } catch (error) {
        console.error('Error cargando películas:', error);
    }
}

// Cargar salas para datalist
async function loadSalasForDatalist() {
    try {
        const response = await fetch(`${API_URL}/api/salas`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (response.ok) {
            const salas = await response.json();
            const datalist = document.getElementById('salas-datalist');
            datalist.innerHTML = salas.map(s => `<option value="${s.nombre}">`).join('');
        }
    } catch (error) {
        console.error('Error cargando salas:', error);
    }
}

// ============ BÚSQUEDA ============

async function loadPeliculasForSearch() {
    try {
        const response = await fetch(`${API_URL}/api/peliculas`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (response.ok) {
            const peliculas = await response.json();
            const datalist = document.getElementById('peliculas-datalist-buscar');
            datalist.innerHTML = peliculas.map(p => `<option value="${p.titulo}">`).join('');
        }
    } catch (error) {
        console.error('Error cargando películas:', error);
    }
}

async function buscarPelicula(e) {
    e.preventDefault();
    
    const titulo = document.getElementById('buscar-titulo').value;
    const container = document.getElementById('resultado-busqueda');
    
    container.innerHTML = '<div class="loading">Buscando...</div>';
    
    try {
        const response = await fetch(`${API_URL}/api/peliculas/buscar/${encodeURIComponent(titulo)}`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Error al buscar película');
        }
        
        const data = await response.json();
        displaySearchResult(data);
    } catch (error) {
        console.error('Error:', error);
        container.innerHTML = `<div class="empty-state"><h3>No encontrada</h3><p>${error.message}</p></div>`;
    }
}

function displaySearchResult(data) {
    const container = document.getElementById('resultado-busqueda');
    const { pelicula, proyecciones } = data;
    
    let html = `
        <div class="movie-info">
            <h3>🎬 ${pelicula.titulo}</h3>
            ${pelicula.imagen_uri ? `<img src="${pelicula.imagen_uri}" alt="${pelicula.titulo}" style="max-width: 300px; border-radius: 10px; margin: 1rem 0;">` : ''}
        </div>
    `;
    
    if (proyecciones.length === 0) {
        html += '<div class="empty-state"><h3>Sin proyecciones</h3><p>Esta película no tiene proyecciones programadas</p></div>';
        document.getElementById('mapa-container').style.display = 'none';
    } else {
        html += '<h3>Proyecciones programadas:</h3><div class="projections-list">';
        
        proyecciones.forEach(proy => {
            html += `
                <div class="projection-item">
                    <h4>🏛️ ${proy.sala.nombre}</h4>
                    <div class="datetime">📅 ${new Date(proy.fecha_proyeccion).toLocaleString('es-ES', {
                        dateStyle: 'full',
                        timeStyle: 'short'
                    })}</div>
                    <p class="address">📍 ${proy.sala.direccion}</p>
                    <p><small>Propietario: ${proy.sala.email_propietario}</small></p>
                </div>
            `;
        });
        
        html += '</div>';
        
        // Mostrar mapa con las ubicaciones de las salas
        displayMap(proyecciones);
    }
    
    container.innerHTML = html;
}

// ============ MAPA ============

let map = null;
let markersLayer = null;

function displayMap(proyecciones) {
    const mapaContainer = document.getElementById('mapa-container');
    mapaContainer.style.display = 'block';
    
    // Limpiar mapa anterior si existe
    if (map) {
        map.remove();
        map = null;
    }
    
    // Filtrar solo salas con coordenadas válidas
    const salasConCoordenadas = proyecciones.filter(proy => 
        proy.sala.coordenadas && 
        proy.sala.coordenadas.latitud && 
        proy.sala.coordenadas.longitud
    );
    
    if (salasConCoordenadas.length === 0) {
        mapaContainer.innerHTML = '<div class="empty-state"><h3>Sin ubicaciones</h3><p>Las salas no tienen coordenadas GPS</p></div>';
        return;
    }
    
    // Crear el mapa centrado en la primera sala
    const primeraUbicacion = salasConCoordenadas[0].sala.coordenadas;
    map = L.map('mapa').setView([primeraUbicacion.latitud, primeraUbicacion.longitud], 12);
    
    // Añadir capa de OpenStreetMap
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
        maxZoom: 19
    }).addTo(map);
    
    // Crear un grupo de marcadores para ajustar el zoom automáticamente
    const bounds = [];
    
    // Añadir marcador para cada sala
    salasConCoordenadas.forEach(proy => {
        const { latitud, longitud } = proy.sala.coordenadas;
        
        // Crear marcador
        const marker = L.marker([latitud, longitud]).addTo(map);
        
        // Crear popup con información
        const popupContent = `
            <div>
                <h4>🏛️ ${proy.sala.nombre}</h4>
                <p><strong>📅 ${new Date(proy.fecha_proyeccion).toLocaleString('es-ES', {
                    dateStyle: 'short',
                    timeStyle: 'short'
                })}</strong></p>
                <p>📍 ${proy.sala.direccion}</p>
                <p><small>👤 ${proy.sala.email_propietario}</small></p>
            </div>
        `;
        
        marker.bindPopup(popupContent);
        
        // Añadir coordenadas al array de bounds
        bounds.push([latitud, longitud]);
    });
    
    // Ajustar el zoom para mostrar todos los marcadores
    if (bounds.length > 1) {
        map.fitBounds(bounds, { padding: [50, 50] });
    }
    
    // Scroll suave al mapa
    setTimeout(() => {
        mapaContainer.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }, 300);
}

// ============ NOTIFICACIONES ============

function showNotification(message, type = 'info') {
    const notification = document.getElementById('notification');
    notification.textContent = message;
    notification.className = `notification ${type} show`;
    
    setTimeout(() => {
        notification.classList.remove('show');
    }, 3000);
}
