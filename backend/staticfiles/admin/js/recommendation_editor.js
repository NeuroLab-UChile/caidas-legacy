document.addEventListener('DOMContentLoaded', function() {
    // Obtener las recomendaciones por defecto
    let defaultRecommendations = {};
    try {
        const defaultRecommendationsElement = document.getElementById('defaultRecommendations');
        if (defaultRecommendationsElement) {
            defaultRecommendations = JSON.parse(defaultRecommendationsElement.textContent);
            console.log('Default recommendations loaded:', defaultRecommendations);
        } else {
            console.error('Elemento defaultRecommendations no encontrado');
        }
    } catch (e) {
        console.error('Error parsing default recommendations:', e);
    }

    // Buscar el formulario principal de Django admin
    const form = document.querySelector('#healthcategory_form') || 
                document.querySelector('form[method="post"]') ||
                document.querySelector('form');

    // Verificar si tenemos un formulario válido
    if (!form) {
        console.error('No se encontró el formulario');
        return;
    }

    // Obtener elementos de forma segura
    const elements = {
        defaultRadio: document.getElementById('use-default'),
        customRadio: document.getElementById('use-custom'),
        recommendationText: document.getElementById('recommendation-text'),
        statusColor: document.getElementById('status-color'),
        isDraft: document.getElementById('is-draft'),
        videoInput: document.getElementById('video-input'),
        removeVideoBtn: document.getElementById('remove-video')
    };

    // Debug de elementos encontrados
    console.log('Elementos encontrados:', {
        form: !!form,
        defaultRadio: !!elements.defaultRadio,
        customRadio: !!elements.customRadio,
        recommendationText: !!elements.recommendationText,
        statusColor: !!elements.statusColor,
        isDraft: !!elements.isDraft,
        videoInput: !!elements.videoInput,
        removeVideoBtn: !!elements.removeVideoBtn
    });

    // Crear objeto para almacenar campos ocultos
    const hiddenFields = {};

    // Función para crear campos ocultos
    function createHiddenFields() {
        const fields = {
            'recommendation_text': elements.recommendationText?.value ?? '',
            'recommendation_status': elements.statusColor?.value ?? 'gris',
            'recommendation_is_draft': elements.isDraft?.checked ?? false,
            'recommendation_use_default': elements.defaultRadio?.checked ?? false,
            'video': elements.videoInput?.files[0]?.name ?? ''
        };

        Object.entries(fields).forEach(([name, value]) => {
            let input = form.querySelector(`input[name="${name}"]`);
            if (!input) {
                input = document.createElement('input');
                input.type = name === 'video' ? 'file' : 'hidden';
                input.name = name;
                
            }
            if (name !== 'video') {
                input.value = typeof value === 'boolean' ? String(value) : value;
            }
            hiddenFields[name] = input;
        });
    }

    // Función para actualizar campos ocultos
    function updateHiddenFields() {
        const updates = {
            'recommendation_text': elements.recommendationText?.value ?? '',
            'recommendation_status': elements.statusColor?.value ?? 'gris',
            'recommendation_is_draft': elements.isDraft?.checked ?? false,
            'recommendation_use_default': elements.defaultRadio?.checked ?? false,
            'video': elements.videoInput?.files[0]?.name ?? ''
        };

        Object.entries(updates).forEach(([name, value]) => {
            if (hiddenFields[name] && name !== 'video') {
                hiddenFields[name].value = typeof value === 'boolean' ? String(value) : value;
            }
        });

        console.log('Campos actualizados:', updates);
    }

    // Función para actualizar el texto de recomendación
    function updateRecommendationText() {
        const recommendationText = document.getElementById('recommendation-text');
        const statusColor = document.getElementById('status-color');
        const useDefault = document.getElementById('use-default');
        
        if (!recommendationText || !statusColor || !useDefault) {
            console.warn('Elementos no encontrados');
            return;
        }

        if (useDefault.checked) {
            const status = statusColor.value; // verde, amarillo, rojo, gris
            console.log('Current status:', status);
            console.log('Available recommendations:', defaultRecommendations);
            
            // Mapear el estado al nombre de la clave correcta
            const statusKeyMap = {
                'verde': 'no_risk',
                'amarillo': 'prev_risk',
                'rojo': 'risk',
                'gris': 'pending'
            };

            const key = statusKeyMap[status];
            const defaultText = defaultRecommendations[key] || '';
            console.log('Selected default text:', defaultText);
            
            if (defaultText) {
                recommendationText.value = defaultText;
                recommendationText.disabled = true;
            } else {
                console.warn(`No se encontró texto por defecto para el estado: ${status}`);
            }
        } else {
            recommendationText.disabled = false;
        }
        
        updateHiddenFields();
    }

    // Función segura para añadir event listeners
    function addSafeEventListener(element, event, handler) {
        if (element) {
            element.addEventListener(event, handler);
        } else {
            console.warn(`Elemento no encontrado para evento ${event}`);
        }
    }

    // Inicializar solo si tenemos los elementos necesarios
    if (elements.recommendationText && elements.statusColor) {
        // Event listeners para campos principales
        addSafeEventListener(elements.recommendationText, 'input', updateHiddenFields);
        addSafeEventListener(elements.statusColor, 'change', () => {
            updateHiddenFields();
            updateRecommendationText();
        });
        addSafeEventListener(elements.isDraft, 'change', updateHiddenFields);

        // Event listeners para radios
        if (elements.defaultRadio && elements.customRadio) {
            [elements.defaultRadio, elements.customRadio].forEach(radio => {
                addSafeEventListener(radio, 'change', () => {
                    updateHiddenFields();
                    updateRecommendationText();
                });
            });
        }

        // Event listener para el formulario
        addSafeEventListener(form, 'submit', function(e) {
            e.preventDefault();
            const formData = new FormData(form);

            // Añadir múltiples archivos de video al FormData
            if (elements.videoInput && elements.videoInput.files.length > 0) {
                Array.from(elements.videoInput.files).forEach((file, index) => {
                    formData.append(`videos`, file); // Usa el mismo nombre para múltiples videos
                });
            }

            // Obtener el CSRF token
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

            fetch(form.action || window.location.href, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': csrfToken,
                    'X-Requested-With': 'XMLHttpRequest'
                },
                credentials: 'same-origin'
            })
            .then(response => {
                if (!response.ok) {
                    return response.text().then(text => {
                        throw new Error(text);
                    });
                }
                return response.json();
            })
            .then(data => {
                if (data.success) {
                    console.log('Guardado exitoso');
                    window.location.reload();
                } else {
                    throw new Error(data.error || 'Error al guardar');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Ha ocurrido un error al guardar la recomendación: ' + error.message);
            });
        });

        // Inicializar
        createHiddenFields();
        updateHiddenFields();
        updateRecommendationText();
    } else {
        console.warn('No se encontraron todos los elementos necesarios para el editor de recomendaciones');
    }

    // Manejo de múltiples videos
    const videoInput = document.getElementById('video-input');

    if (videoInput) {
        videoInput.addEventListener('change', function() {
            const files = this.files;
            if (files.length > 0) {
                console.log('Videos seleccionados:');
                Array.from(files).forEach(file => {
                    console.log(file.name);
                    // Aquí puedes agregar cualquier lógica adicional que necesites para cada archivo
                });
            }
        });
    }

    const removeVideoBtn = document.getElementById('remove-video');

    if (removeVideoBtn) {
        removeVideoBtn.addEventListener('click', function() {
            if (confirm('¿Estás seguro de que deseas eliminar el video?')) {
                const input = document.createElement('input');
                input.type = 'hidden';
                input.name = 'remove_video';
                input.value = 'true';
                form.appendChild(input);
                form.submit();
            }
        });
    }

    const buttons = document.querySelectorAll('.save-recommendation');
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    
    // Obtener el ID de la categoría de la URL
    const path = window.location.pathname;
    const match = path.match(/\/healthcategory\/(\d+)/);
    const categoryId = match ? match[1] : null;
    
    if (!categoryId) {
        console.error('No se pudo extraer el ID de la categoría de la URL');
        return;
    }
    
    buttons.forEach(button => {
        button.addEventListener('click', async function(e) {
            e.preventDefault();
            const complete = this.dataset.complete === 'true';
            
            try {
                const url = `/admin/healthcategory/${categoryId}/update-recommendation/`;
                
                const requestData = {
                    text: document.getElementById('recommendation-text').value,
                    status_color: document.getElementById('status-color').value,
                    is_draft: !complete,
                    recommendation_use_default: document.getElementById('use-default').checked,
                    video: document.getElementById('video-input').files[0]
                };
                
                const response = await fetch(url, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrfToken
                    },
                    body: JSON.stringify(requestData)
                });

                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }

                const data = await response.json();
                
                if (data.success) {
                    console.log('Guardado exitoso');
                    window.location.reload();
                } else {
                    throw new Error(data.error || 'Error al guardar');
                }
            } catch (error) {
                console.error('Error:', error);
                alert('Ha ocurrido un error al guardar la recomendación: ' + error.message);
            }
        });
    });
}); 