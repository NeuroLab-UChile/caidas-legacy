document.addEventListener('DOMContentLoaded', function() {
    // Obtener las recomendaciones por defecto del script JSON
    const defaultRecommendations = JSON.parse(
        document.getElementById('defaultRecommendations')?.textContent || '{}'
    );

    console.log('Default recommendations:', defaultRecommendations);

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
        isDraft: document.getElementById('is-draft')
    };

    // Debug de elementos encontrados
    console.log('Elementos encontrados:', {
        form: !!form,
        defaultRadio: !!elements.defaultRadio,
        customRadio: !!elements.customRadio,
        recommendationText: !!elements.recommendationText,
        statusColor: !!elements.statusColor,
        isDraft: !!elements.isDraft
    });

    // Crear objeto para almacenar campos ocultos
    const hiddenFields = {};

    // Función para crear campos ocultos
    function createHiddenFields() {
        const fields = {
            'recommendation_text': elements.recommendationText?.value ?? '',
            'recommendation_status': elements.statusColor?.value ?? 'gris',
            'recommendation_is_draft': elements.isDraft?.checked ?? false,
            'recommendation_use_default': elements.defaultRadio?.checked ?? false
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
            hiddenFields[name] = input;
        });
    }

    // Función para actualizar campos ocultos
    function updateHiddenFields() {
        const updates = {
            'recommendation_text': elements.recommendationText?.value ?? '',
            'recommendation_status': elements.statusColor?.value ?? 'gris',
            'recommendation_is_draft': elements.isDraft?.checked ?? false,
            'recommendation_use_default': elements.defaultRadio?.checked ?? false
        };

        Object.entries(updates).forEach(([name, value]) => {
            if (hiddenFields[name]) {
                hiddenFields[name].value = typeof value === 'boolean' ? String(value) : value;
            }
        });

        console.log('Campos actualizados:', updates);
    }

    // Función para actualizar el texto de recomendación
    function updateRecommendationText() {
        if (!elements.recommendationText || !elements.statusColor) return;

        if (elements.defaultRadio?.checked) {
            const status = elements.statusColor.value;
            const defaultText = defaultRecommendations[status] || '';
            elements.recommendationText.value = defaultText;
            elements.recommendationText.disabled = true;
        } else {
            elements.recommendationText.disabled = false;
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
        addSafeEventListener(form, 'submit', (e) => {
            updateHiddenFields();
            const formData = new FormData(form);
            console.log('Enviando formulario:', Object.fromEntries(formData));
        });

        // Inicializar
        createHiddenFields();
        updateHiddenFields();
        updateRecommendationText();
    } else {
        console.warn('No se encontraron todos los elementos necesarios para el editor de recomendaciones');
    }
}); 