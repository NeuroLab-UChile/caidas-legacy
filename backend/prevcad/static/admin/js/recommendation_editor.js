document.addEventListener('DOMContentLoaded', function() {
    const useDefault = document.getElementById('use-default');
    const editor = document.getElementById('recommendation-editor');
    const recommendationText = document.getElementById('recommendation-text');
    const statusColor = document.getElementById('status-color');
    const isDraft = document.getElementById('is-draft');
    const signRecommendation = document.getElementById('sign-recommendation');
    const saveButton = document.getElementById('save-recommendation');
    const lastUpdatedElement = document.querySelector('.p-4.bg-gray-50');

    console.log('Elemento textarea:', recommendationText);
    if (recommendationText) {
        console.log('Health Category ID:', recommendationText.dataset.healthCategoryId);
    }

    function updateRecommendation() {
        const healthCategoryId = recommendationText.dataset.healthCategoryId;
        
        if (!healthCategoryId) {
            console.error('No se encontró el ID de la categoría de salud');
            return;
        }

        const data = {
            text: recommendationText.value || '',
            status_color: statusColor.value || 'gris',
            is_draft: Boolean(isDraft.checked),
            sign: Boolean(signRecommendation.checked),
            use_default: Boolean(useDefault.checked)
        };

        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

        fetch(`/admin/prevcad/healthcategory/${healthCategoryId}/update-recommendation/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify(data)
        })
        .then(response => {
            if (!response.ok) {
                return response.json().then(data => {
                    throw new Error(data.message || 'Error en la actualización');
                });
            }
            return response.json();
        })
        .then(data => {
            if (data.status === 'success') {
                // Actualizar la interfaz
                recommendationText.value = data.recommendation.text;
                statusColor.value = data.recommendation.status_color;
                isDraft.checked = data.recommendation.is_draft;
                useDefault.checked = data.recommendation.use_default;
                
                // Actualizar la información de última actualización
                const updatedAt = new Date(data.recommendation.updated_at).toLocaleString();
                let updateText = `Última actualización: ${updatedAt}`;
                if (data.recommendation.is_signed) {
                    updateText += ` • Firmado por ${data.recommendation.signed_by}`;
                }
                lastUpdatedElement.textContent = updateText;

                alert('Recomendación actualizada con éxito');
            } else {
                throw new Error(data.message || 'Error desconocido');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Error al actualizar la recomendación: ' + error.message);
        });
    }

    // Event listeners
    saveButton.addEventListener('click', updateRecommendation);

    // Toggle editor visibility
    useDefault.addEventListener('change', function() {
        editor.classList.toggle('hidden', this.checked);
    });
}); 