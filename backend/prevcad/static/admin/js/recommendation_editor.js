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

        try {
            // Mostrar estado de carga
            saveButton.disabled = true;
            saveButton.innerHTML = `
                <svg class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Guardando...
            `;

            const response = await fetch(`/admin/prevcad/healthcategory/${healthCategoryId}/update-recommendation/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken,
                },
                body: JSON.stringify({
                    use_default: defaultRadio.checked,
                    text: recommendationText.value,
                    status_color: statusColor.value,
                    is_draft: isDraft.checked,
                    sign: signRecommendation.checked
                })
            });

            const data = await response.json();

            if (response.ok && data.status === 'success') {
                showNotification('success', data.message || 'Cambios guardados correctamente');
                updateLastModifiedInfo(data.recommendation);
            } else {
                throw new Error(data.message || 'Error al guardar los cambios');
            }

        } catch (error) {
            console.error('Error:', error);
            showNotification('error', error.message || 'Error al guardar los cambios');
        } finally {
            // Restaurar botón
            saveButton.disabled = false;
            saveButton.innerHTML = `
                <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/>
                </svg>
                Guardar Cambios
            `;
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
}); 