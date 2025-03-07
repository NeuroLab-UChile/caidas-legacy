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
                form.appendChild(input);
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
            console.log('Formulario enviado');

            const submitButton = form.querySelector('[type="submit"]');
            if (submitButton) {
                submitButton.disabled = true;
                submitButton.textContent = 'Guardando...';
            }

            const formData = new FormData(form);
            
            // Agregar campos manualmente
            formData.append('text', document.getElementById('recommendation-text')?.value || '');
            formData.append('status_color', document.getElementById('status-color')?.value || 'gris');
            formData.append('is_draft', document.getElementById('is-draft')?.checked || false);
            formData.append('recommendation_use_default', document.getElementById('use-default')?.checked || false);

            // Agregar el video si existe
            const videoInput = document.getElementById('video-input');
            if (videoInput && videoInput.files[0]) {
                formData.append('video', videoInput.files[0]);
            }

            // Obtener el CSRF token
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value;
            if (!csrfToken) {
                console.error('CSRF token no encontrado');
                alert('Error: CSRF token no encontrado');
                return;
            }

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
                console.log('Respuesta recibida:', {
                    status: response.status,
                    statusText: response.statusText,
                    headers: Object.fromEntries(response.headers.entries())
                });
                
                return response.text().then(text => {
                    if (!response.ok) {
                        console.error('Error en respuesta:', text);
                        try {
                            const errorData = JSON.parse(text);
                            throw new Error(errorData.message || errorData.error || `Error ${response.status}`);
                        } catch (e) {
                            throw new Error(`Error ${response.status}: ${text}`);
                        }
                    }
                    return text;
                });
            })
            .then(text => {
                console.log('Texto de respuesta completo:', text);
                try {
                    // Intentar parsear como JSON
                    const data = JSON.parse(text);
                    console.log('Datos JSON parseados:', data);
                    
                    // Verificar si tenemos una URL de video en la respuesta
                    if (data.video_url) {
                        console.log('Video subido exitosamente:', data.video_url);
                    }
                    
                    if (data.success || data.status === 'success' || data.video_url) {
                        console.log('Guardado exitoso, recargando página...');
                        // Esperar un momento antes de recargar para asegurar que el servidor procesó todo
                        setTimeout(() => {
                            window.location.reload();
                        }, 1000);
                    } else {
                        throw new Error(data.message || 'Error desconocido');
                    }
                } catch (e) {
                    console.log('Error al parsear JSON, verificando si es HTML...');
                    // Si la respuesta contiene una ruta de video, considerarla exitosa
                    if (text.includes('/media/recommendations/videos/')) {
                        console.log('Video subido exitosamente, recargando página...');
                        setTimeout(() => {
                            window.location.reload();
                        }, 1000);
                        return;
                    }
                    
                    if (text.includes('<html') || text.includes('<!DOCTYPE html>')) {
                        if (text.includes('error') || text.includes('Error')) {
                            console.error('Respuesta HTML contiene error:', text);
                            throw new Error('Error en la respuesta del servidor');
                        }
                        console.log('Respuesta HTML detectada, recargando página...');
                        setTimeout(() => {
                            window.location.reload();
                        }, 1000);
                    } else {
                        console.error('Respuesta no válida:', text);
                        throw new Error('Respuesta inválida del servidor');
                    }
                }
            })
            .catch(error => {
                console.error('Error completo:', error);
                console.error('Stack trace:', error.stack);
                alert('Error al guardar los cambios: ' + error.message);
            })
            .finally(() => {
                console.log('Finalizando proceso de envío...');
                if (submitButton) {
                    submitButton.disabled = false;
                    submitButton.textContent = 'Guardar cambios';
                }
            });
        });

        // Inicializar
        createHiddenFields();
        updateHiddenFields();
        updateRecommendationText();
    } else {
        console.warn('No se encontraron todos los elementos necesarios para el editor de recomendaciones');
    }

    // Agregar al inicio del archivo, dentro del DOMContentLoaded
    const videoInput = document.getElementById('video-input');
    const removeVideoBtn = document.getElementById('remove-video');

    if (videoInput) {
        videoInput.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                if (file.size > 100 * 1024 * 1024) {
                    alert('El archivo es demasiado grande. Máximo 100MB.');
                    this.value = '';
                } else {
                    console.log('Video seleccionado:', file.name);
                    updateHiddenFields();
                }
            }
        });
    }

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
}); 