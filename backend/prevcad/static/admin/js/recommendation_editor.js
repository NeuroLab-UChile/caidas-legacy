document.addEventListener('DOMContentLoaded', function() {
    const recommendationText = document.getElementById('recommendation-text');
    const statusColor = document.getElementById('status-color');
    const isDraft = document.getElementById('is-draft');
    const signRecommendation = document.getElementById('sign-recommendation');

    function updateRecommendation() {
        const recommendationId = recommendationText.dataset.recommendationId;
        const data = {
            text: recommendationText.value,
            status_color: statusColor.value,
            is_draft: isDraft.checked,
            sign: signRecommendation.checked
        };

        fetch(`/admin/prevcad/healthcategory/${recommendationId}/update-recommendation/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify(data)
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                // Actualizar la UI si es necesario
            }
        })
        .catch(error => console.error('Error:', error));
    }

    // Función helper para obtener el CSRF token
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    // Event listeners
    recommendationText.addEventListener('change', updateRecommendation);
    statusColor.addEventListener('change', updateRecommendation);
    isDraft.addEventListener('change', updateRecommendation);
    signRecommendation.addEventListener('change', updateRecommendation);
}); 