// Variables globales
let token = null;
let map = null;
let markers = [];
let reviews = [];
let uploadedImages = []; // Array para guardar las URLs de imágenes subidas

// Inicialización
document.addEventListener('DOMContentLoaded', () => {
    // Verificar si hay token guardado
    token = localStorage.getItem('token');
    if (token) {
        // Ocultar pantalla de login inmediatamente
        document.getElementById('loginScreen').style.display = 'none';
        
        // Cancelar el prompt de One Tap de Google si se está mostrando
        if (window.google && google.accounts && google.accounts.id) {
            google.accounts.id.cancel();
        }
        
        verifyToken();
    }
});

// Callback de Google Sign-In
function handleCredentialResponse(response) {
    const googleToken = response.credential;
    
    // Enviar token a nuestro backend
    fetch('/api/auth/google', {
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
            localStorage.setItem('token', token);
            showApp(data.user);
        } else {
            alert('Error al iniciar sesión');
        }
    })
    .catch(err => {
        console.error('Error:', err);
        alert('Error al iniciar sesión');
    });
}

// Verificar token existente
function verifyToken() {
    fetch('/api/auth/verify', {
        headers: {
            'Authorization': `Bearer ${token}`
        }
    })
    .then(res => res.json())
    .then(data => {
        if (data.valid) {
            showApp(data.user);
        } else {
            localStorage.removeItem('token');
            token = null;
        }
    })
    .catch(err => {
        console.error('Error:', err);
        localStorage.removeItem('token');
        token = null;
    });
}

// Mostrar aplicación principal
function showApp(user) {
    document.getElementById('loginScreen').style.display = 'none';
    document.getElementById('mainApp').style.display = 'block';
    
    // Mostrar info del usuario
    document.getElementById('userName').textContent = user.name;
    document.getElementById('userAvatar').src = user.picture || 'https://via.placeholder.com/40';
    
    // Inicializar mapa
    initMap();
    
    // Cargar reseñas
    loadReviews();
    
    // Event listeners
    document.getElementById('logoutBtn').addEventListener('click', logout);
    document.getElementById('showFormBtn').addEventListener('click', showForm);
    document.getElementById('createReviewForm').addEventListener('submit', createReview);
    document.getElementById('imagenes').addEventListener('change', handleImageUpload);
}

// Cerrar sesión
function logout() {
    localStorage.removeItem('token');
    token = null;
    location.reload();
}

// Inicializar mapa
function initMap() {
    // Centrar en España por defecto
    map = L.map('map').setView([40.4168, -3.7038], 6);
    
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors'
    }).addTo(map);
}

// Cargar reseñas
function loadReviews() {
    fetch('/api/resenas', {
        headers: {
            'Authorization': `Bearer ${token}`
        }
    })
    .then(res => res.json())
    .then(data => {
        reviews = data;
        displayReviews();
        displayMarkersOnMap();
    })
    .catch(err => {
        console.error('Error cargando reseñas:', err);
        alert('Error al cargar las reseñas');
    });
}

// Mostrar reseñas en la lista
function displayReviews() {
    const container = document.getElementById('reviewsContainer');
    container.innerHTML = '';
    
    if (reviews.length === 0) {
        container.innerHTML = '<p class="no-reviews">No hay reseñas todavía. ¡Sé el primero en crear una!</p>';
        return;
    }
    
    reviews.forEach(review => {
        const card = document.createElement('div');
        card.className = 'review-card';
        card.innerHTML = `
            <h3>${review.nombre_establecimiento}</h3>
            <p class="address">📍 ${review.direccion}</p>
            <p class="coords">🌍 ${review.longitud.toFixed(6)}, ${review.latitud.toFixed(6)}</p>
            <div class="rating">${'⭐'.repeat(review.valoracion)}${'☆'.repeat(5 - review.valoracion)} (${review.valoracion}/5)</div>
            <button onclick="showReviewDetail('${review._id}')" class="btn-primary btn-small">Ver Detalles</button>
        `;
        container.appendChild(card);
    });
}

// Mostrar marcadores en el mapa
function displayMarkersOnMap() {
    // Limpiar marcadores anteriores
    markers.forEach(marker => map.removeLayer(marker));
    markers = [];
    
    if (reviews.length === 0) return;
    
    // Añadir nuevos marcadores
    reviews.forEach(review => {
        const marker = L.marker([review.latitud, review.longitud])
            .addTo(map)
            .bindPopup(`
                <strong>${review.nombre_establecimiento}</strong><br>
                ${review.direccion}<br>
                Valoración: ${'⭐'.repeat(review.valoracion)} (${review.valoracion}/5)<br>
                <button onclick="showReviewDetail('${review._id}')" class="btn-link">Ver detalles</button>
            `);
        markers.push(marker);
    });
    
    // Ajustar vista del mapa para mostrar todos los marcadores
    if (markers.length > 0) {
        const group = new L.featureGroup(markers);
        map.fitBounds(group.getBounds().pad(0.1));
    }
}

// Buscar dirección en el mapa
function searchAddress() {
    const address = document.getElementById('searchAddress').value;
    if (!address) return;
    
    fetch('/api/resenas/geocode', {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ direccion: address })
    })
    .then(res => res.json())
    .then(data => {
        if (data.latitud && data.longitud) {
            map.setView([data.latitud, data.longitud], 13);
            L.marker([data.latitud, data.longitud])
                .addTo(map)
                .bindPopup(`<strong>${address}</strong>`)
                .openPopup();
        } else {
            alert('No se pudo encontrar la dirección');
        }
    })
    .catch(err => {
        console.error('Error:', err);
        alert('Error al buscar la dirección');
    });
}

// Mostrar formulario de nueva reseña
function showForm() {
    document.getElementById('reviewForm').style.display = 'block';
    document.getElementById('reviewsList').style.display = 'none';
    document.getElementById('showFormBtn').style.display = 'none';
}

// Ocultar formulario
function hideForm() {
    document.getElementById('reviewForm').style.display = 'none';
    document.getElementById('reviewsList').style.display = 'block';
    document.getElementById('showFormBtn').style.display = 'block';
    document.getElementById('createReviewForm').reset();
    
    // Limpiar imágenes subidas
    uploadedImages = [];
    document.getElementById('imagePreviewContainer').innerHTML = '';
}

// Manejar subida de imagen individual
async function handleImageUpload(e) {
    const file = e.target.files[0];
    if (!file) return;
    
    // Validar tipo de archivo
    const allowedTypes = ['image/png', 'image/jpg', 'image/jpeg', 'image/gif', 'image/webp'];
    if (!allowedTypes.includes(file.type)) {
        alert('Tipo de archivo no permitido. Usa: PNG, JPG, JPEG, GIF o WEBP');
        e.target.value = '';
        return;
    }
    
    // Crear preview temporal
    const previewContainer = document.getElementById('imagePreviewContainer');
    const previewId = 'preview_' + Date.now();
    const previewDiv = document.createElement('div');
    previewDiv.className = 'image-preview-item';
    previewDiv.id = previewId;
    
    // Crear preview de la imagen
    const img = document.createElement('img');
    img.src = URL.createObjectURL(file);
    previewDiv.appendChild(img);
    
    // Mostrar indicador de carga
    const loadingDiv = document.createElement('div');
    loadingDiv.className = 'image-loading';
    loadingDiv.textContent = 'Subiendo...';
    previewDiv.appendChild(loadingDiv);
    
    previewContainer.appendChild(previewDiv);
    
    // Subir imagen a Cloudinary
    const formData = new FormData();
    formData.append('image', file);
    
    try {
        const response = await fetch('/api/upload/image?folder=reviews', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`
            },
            body: formData
        });
        
        const data = await response.json();
        
        if (data.url) {
            // Guardar URL de la imagen subida
            uploadedImages.push({
                url: data.url,
                public_id: data.public_id,
                previewId: previewId
            });
            
            // Remover indicador de carga
            loadingDiv.remove();
            
            // Agregar botón de eliminar
            const removeBtn = document.createElement('button');
            removeBtn.className = 'remove-image';
            removeBtn.innerHTML = '×';
            removeBtn.onclick = () => removeUploadedImage(previewId);
            previewDiv.appendChild(removeBtn);
            
        } else {
            throw new Error(data.error || 'Error al subir imagen');
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Error al subir la imagen: ' + error.message);
        previewDiv.remove();
    }
    
    // Limpiar input para permitir seleccionar otra imagen
    e.target.value = '';
}

// Eliminar imagen subida
function removeUploadedImage(previewId) {
    // Remover del array
    const index = uploadedImages.findIndex(img => img.previewId === previewId);
    if (index > -1) {
        uploadedImages.splice(index, 1);
    }
    
    // Remover del DOM
    const previewElement = document.getElementById(previewId);
    if (previewElement) {
        previewElement.remove();
    }
}

// Crear nueva reseña
function createReview(e) {
    e.preventDefault();
    
    const formData = new FormData();
    formData.append('nombre_establecimiento', document.getElementById('nombreEstablecimiento').value);
    formData.append('direccion', document.getElementById('direccion').value);
    formData.append('valoracion', document.getElementById('valoracion').value);
    
    // Agregar URLs de imágenes ya subidas
    uploadedImages.forEach(img => {
        formData.append('imagenes_urls[]', img.url);
    });
    
    // Mostrar indicador de carga
    const submitBtn = e.target.querySelector('button[type="submit"]');
    const originalText = submitBtn.textContent;
    submitBtn.textContent = 'Creando...';
    submitBtn.disabled = true;
    
    fetch('/api/resenas', {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${token}`
        },
        body: formData
    })
    .then(res => res.json())
    .then(data => {
        if (data._id) {
            alert('Reseña creada exitosamente');
            hideForm();
            loadReviews();
        } else {
            alert('Error: ' + (data.error || 'No se pudo crear la reseña'));
        }
    })
    .catch(err => {
        console.error('Error:', err);
        alert('Error al crear la reseña');
    })
    .finally(() => {
        submitBtn.textContent = originalText;
        submitBtn.disabled = false;
    });
}

// Mostrar detalle de reseña en modal
function showReviewDetail(reviewId) {
    fetch(`/api/resenas/${reviewId}`, {
        headers: {
            'Authorization': `Bearer ${token}`
        }
    })
    .then(res => res.json())
    .then(review => {
        const modalBody = document.getElementById('modalBody');
        
        let imagenesHtml = '';
        if (review.imagenes_uri && review.imagenes_uri.length > 0) {
            imagenesHtml = '<div class="review-images">';
            review.imagenes_uri.forEach(url => {
                imagenesHtml += `<img src="${url}" alt="Imagen del establecimiento">`;
            });
            imagenesHtml += '</div>';
        }
        
        modalBody.innerHTML = `
            <h2>${review.nombre_establecimiento}</h2>
            <div class="review-detail">
                <p><strong>Dirección:</strong> ${review.direccion}</p>
                <p><strong>Coordenadas GPS:</strong> ${review.longitud.toFixed(6)}, ${review.latitud.toFixed(6)}</p>
                <p><strong>Valoración:</strong> ${'⭐'.repeat(review.valoracion)}${'☆'.repeat(5 - review.valoracion)} <strong>(${review.valoracion} de 5 estrellas)</strong></p>
                
                <hr>
                
                <h3>Información del Autor</h3>
                <p><strong>Email:</strong> ${review.autor_email}</p>
                <p><strong>Nombre:</strong> ${review.autor_nombre}</p>
                
                <hr>
                
                <h3>Información del Token</h3>
                <p><strong>Token de identificación:</strong></p>
                <code class="token-display">${review.token}</code>
                <p><strong>Fecha de emisión:</strong> ${new Date(review.token_emision).toLocaleString('es-ES')}</p>
                <p><strong>Fecha de caducidad:</strong> ${new Date(review.token_caducidad).toLocaleString('es-ES')}</p>
                
                ${imagenesHtml}
            </div>
        `;
        
        document.getElementById('reviewModal').style.display = 'block';
    })
    .catch(err => {
        console.error('Error:', err);
        alert('Error al cargar los detalles de la reseña');
    });
}

// Cerrar modal
function closeModal() {
    document.getElementById('reviewModal').style.display = 'none';
}

// Cerrar modal al hacer clic fuera
window.onclick = function(event) {
    const modal = document.getElementById('reviewModal');
    if (event.target === modal) {
        modal.style.display = 'none';
    }
}
