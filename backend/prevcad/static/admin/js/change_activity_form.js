document.addEventListener('DOMContentLoaded', function() {
    const useDefaultCheckbox = document.getElementById('id_use_default_recommendations');
    const recommendationsField = document.getElementById('id_default_text_recommendations').closest('.form-row');

    function toggleRecommendationsField() {
        if (useDefaultCheckbox.checked) {
            recommendationsField.style.display = 'none';
        } else {
            recommendationsField.style.display = 'block';
        }
        // También manejar el estado readonly del textarea
        const textarea = document.getElementById('id_default_text_recommendations');
        textarea.readOnly = useDefaultCheckbox.checked;
    }

    if (useDefaultCheckbox) {
        useDefaultCheckbox.addEventListener('change', toggleRecommendationsField);
        // Ejecutar inmediatamente para establecer el estado inicial
        toggleRecommendationsField();
    }
}); 