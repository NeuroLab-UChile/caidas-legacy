document.addEventListener('DOMContentLoaded', function() {
    const defaultRadio = document.getElementById('use-default');
    const customRadio = document.getElementById('use-custom');
    const recommendationText = document.getElementById('recommendation-text');
    const statusColor = document.getElementById('status-color');
    const isDraft = document.getElementById('is-draft');
    const signRecommendation = document.getElementById('sign-recommendation');
    const saveButton = document.getElementById('save-recommendation');
    
    // Obtener las recomendaciones por defecto del elemento script
    const defaultRecommendations = JSON.parse(
        document.getElementById('defaultRecommendations').textContent
    );

    function updateRecommendationText() {
        if (defaultRadio.checked) {
            const status = statusColor.value;
            const statusMap = {
                'verde': 'no_risk',
                'amarillo': 'prev_risk',
                'rojo': 'risk',
                'gris': 'default'
            };
            
            const defaultText = defaultRecommendations[statusMap[status]] || defaultRecommendations['default'] || '';
            recommendationText.value = defaultText;
            recommendationText.readOnly = true;
            recommendationText.classList.add('bg-gray-50');
        } else {
            recommendationText.readOnly = false;
            recommendationText.classList.remove('bg-gray-50');
        }
    }

    // Event listeners para cambios
    defaultRadio.addEventListener('change', updateRecommendationText);
    customRadio.addEventListener('change', updateRecommendationText);
    statusColor.addEventListener('change', updateRecommendationText);

    // Inicializar el estado
    updateRecommendationText();

    async function saveChanges() {
        const healthCategoryId = recommendationText.dataset.healthCategoryId;
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        const saveButton = document.getElementById('save-recommendation');
        if (saveButton) {
            saveButton.addEventListener('click', async function() {
                const textarea = document.getElementById('recommendation-text');
                const categoryId = textarea.dataset.healthCategoryId;
                
                console.log('Intentando guardar con:', {
                    text: textarea.value,
                    status_color: statusColor.value,
                    categoryId: categoryId
                });
    
                try {
                    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
                    
                    const response = await fetch(`/admin/prevcad/healthcategory/${categoryId}/update-recommendation/`, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-CSRFToken': csrfToken,
                        },
                        body: JSON.stringify({
                            recommendation_text: textarea.value,
                            status_color: statusColor.value,
                            is_draft: isDraft.checked,
                            
                            debug_info: {
                                timestamp: new Date().toISOString(),
                                textLength: textarea.value.length
                            }
                        })
                    });
    
                    const data = await response.json();
                    
                    if (response.ok && data.status === 'success') {
                        window.location.reload();
                    } else {
                        throw new Error(data.message || 'Error al guardar los cambios');
                    }
                } catch (error) {
                    console.error('Error al guardar:', error);
                    alert('Error: ' + error.message);
                }
            });
        }

      
    }

    function showNotification(type, message) {
        // Remover notificaciones anteriores
        const existingNotifications = document.querySelectorAll('.notification');
        existingNotifications.forEach(notification => notification.remove());

        const notification = document.createElement('div');
        notification.className = `notification fixed top-4 right-4 max-w-md bg-white rounded-lg shadow-xl border-l-4 ${
            type === 'success' ? 'border-green-500' : 'border-red-500'
        } p-4`;

        notification.innerHTML = `
            <div class="flex items-start">
                <div class="flex-shrink-0">
                    ${type === 'success' 
                        ? '<svg class="h-6 w-6 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>'
                        : '<svg class="h-6 w-6 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>'
                    }
                </div>
                <div class="ml-3">
                    <h3 class="text-sm font-medium ${type === 'success' ? 'text-green-800' : 'text-red-800'}">
                        ${type === 'success' ? '¡Éxito!' : '¡Error!'}
                    </h3>
                    <div class="mt-1 text-sm ${type === 'success' ? 'text-green-700' : 'text-red-700'}">
                        ${message}
                    </div>
                </div>
            </div>
        `;

        document.body.appendChild(notification);

        // Animar entrada
        notification.style.opacity = '0';
        notification.style.transform = 'translateY(-1rem)';
        setTimeout(() => {
            notification.style.transition = 'all 0.3s ease-out';
            notification.style.opacity = '1';
            notification.style.transform = 'translateY(0)';
        }, 10);

        // Auto-cerrar después de 5 segundos
        setTimeout(() => {
            notification.style.opacity = '0';
            notification.style.transform = 'translateY(-1rem)';
            setTimeout(() => notification.remove(), 300);
        }, 5000);
    }

    function updateLastModifiedInfo(recommendation) {
        const updateInfo = document.querySelector('.text-gray-600');
        if (updateInfo) {
            const date = new Date(recommendation.updated_at).toLocaleString();
            let html = `Última actualización: ${date}`;
            
            if (recommendation.is_signed) {
                html += ` • Firmado por ${recommendation.signed_by}`;
            }
            
            updateInfo.innerHTML = html;
        }
    }

    // Event listeners
    saveButton.addEventListener('click', saveChanges);

    async function updateRecommendation(categoryId) {
        console.group('DEBUG: Actualización de Recomendación');
        
        // 1. Obtener el texto
        const textarea = document.getElementById('recommendation_text');
        console.log('Textarea encontrado:', textarea);
        
        if (!textarea) {
            console.error('No se encontró el textarea');
            alert('Error: No se encontró el campo de texto');
            console.groupEnd();
            return;
        }
        
        const recommendationText = textarea.value;
        console.log('Texto de recomendación:', {
            value: recommendationText,
            length: recommendationText?.length,
            preview: recommendationText?.substring(0, 100)
        });

        if (!recommendationText?.trim()) {
            console.warn('Texto vacío');
            alert('Por favor, ingrese una recomendación');
            console.groupEnd();
            return;
        }

        // 2. CSRF Token
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value;
        if (!csrfToken) {
            console.error('No CSRF token');
            alert('Error de seguridad: No se encontró el token CSRF');
            console.groupEnd();
            return;
        }

        // 3. Enviar request
        try {
            const payload = {
                recommendation_text: recommendationText,
                status_color: statusColor,
                debug_info: {
                    timestamp: new Date().toISOString(),
                    textLength: recommendationText.length
                }
            };
            
            console.log('Enviando payload:', payload);

            const response = await fetch(`${categoryId}/update-recommendation/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken,
                },
                body: JSON.stringify(payload),
                credentials: 'same-origin'
            });

            console.log('Response status:', response.status);
            const responseData = await response.text();
            console.log('Response data:', responseData);

            if (response.ok) {
                try {
                    const jsonData = JSON.parse(responseData);
                    if (jsonData.status === 'success') {
                        window.location.reload();
                    } else {
                        throw new Error(jsonData.message || 'Error desconocido');
                    }
                } catch (e) {
                    console.error('Error parsing response:', e);
                    throw new Error('Error procesando la respuesta del servidor');
                }
            } else {
                throw new Error(`Error ${response.status}: ${responseData}`);
            }
        } catch (error) {
            console.error('Error completo:', error);
            alert('Error: ' + error.message);
        }

        console.groupEnd();
    }
}); 