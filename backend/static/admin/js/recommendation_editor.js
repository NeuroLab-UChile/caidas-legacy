document.addEventListener('DOMContentLoaded', function() {
    console.log('Iniciando editor de recomendaciones');
    
    // Obtener las recomendaciones por defecto
    const defaultRecommendations = JSON.parse(
        document.getElementById('defaultRecommendations')?.textContent || '{}'
    );
    
    console.log('Recomendaciones por defecto:', defaultRecommendations);

    // Verificar permisos de edición
    const canEditElement = document.getElementById('can-edit-recommendation');
    const canEdit = canEditElement?.value === 'true';
    const userRole = canEditElement?.dataset.userRole;
    const isReadonly = canEditElement?.dataset.isReadonly === 'true';

    // Buscar el formulario principal
    const form = document.querySelector('#healthcategory_form') || 
                document.querySelector('form[method="post"]') ||
                document.querySelector('form');

    // Obtener elementos
    const elements = {
        defaultRadio: document.getElementById('use-default'),
        customRadio: document.getElementById('use-custom'),
        recommendationText: document.getElementById('recommendation-text'),
        statusColor: document.getElementById('status-color'),
        isDraft: document.getElementById('is-draft')
    };

    function updateHiddenFields() {
        const fields = {
            'recommendation_text': elements.recommendationText?.value || '',
            'recommendation_status': elements.statusColor?.value || 'gris',
            'recommendation_is_draft': elements.isDraft?.checked || false,
            'recommendation_use_default': elements.defaultRadio?.checked || false
        };

        Object.entries(fields).forEach(([name, value]) => {
            let input = form.querySelector(`input[name="${name}"]`);
            if (!input) {
                input = document.createElement('input');
                input.type = 'hidden';
                input.name = name;
                form.appendChild(input);
            }
            input.value = typeof value === 'boolean' ? String(value) : value;
            console.log(`Campo oculto ${name}:`, input.value);
        });
    }

    function updateRecommendationText() {
        if (!elements.recommendationText || !elements.defaultRadio) return;

        const useDefault = elements.defaultRadio.checked;
        const currentStatus = elements.statusColor?.value || 'gris';
        
        console.log('Actualizando texto:', {
            useDefault,
            currentStatus,
            availableRecommendations: defaultRecommendations
        });

        if (useDefault) {
            const defaultText = defaultRecommendations[currentStatus] || '';
            console.log('Usando texto por defecto:', defaultText);
            elements.recommendationText.value = defaultText;
        }
        
        elements.recommendationText.readOnly = useDefault;
        elements.recommendationText.classList.toggle('bg-gray-50', useDefault);
        updateHiddenFields();
    }

    // Solo inicializar si tenemos permisos y elementos necesarios
    if (canEdit && form && elements.recommendationText) {
        console.log('Inicializando funcionalidad del editor');

        // Event listeners para campos principales
        elements.recommendationText.addEventListener('input', updateHiddenFields);
        elements.statusColor.addEventListener('change', () => {
            updateHiddenFields();
            updateRecommendationText();
        });
        elements.isDraft.addEventListener('change', updateHiddenFields);

        // Event listeners para radios
        [elements.defaultRadio, elements.customRadio].forEach(radio => {
            radio.addEventListener('change', () => {
                updateHiddenFields();
                updateRecommendationText();
            });
        });

        // Event listener para el formulario
        form.addEventListener('submit', (e) => {
            updateHiddenFields();
            const formData = new FormData(form);
            console.log('Enviando formulario:', Object.fromEntries(formData));
        });

        // Inicializar
        createHiddenFields();
        updateHiddenFields();
        updateRecommendationText();
    } else {
        console.log('No se inicializó el editor:', {
            canEdit,
            hasForm: !!form,
            hasRecommendationText: !!elements.recommendationText
        });
    }
}); 