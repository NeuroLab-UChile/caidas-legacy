(function() {
    'use strict';
    
    // Esperar a que el documento esté listo
    django.jQuery(document).ready(function($) {
        var evaluationTypeSelect = $('#id_evaluation_type');
        var selfFormFieldset = $('.field-self_evaluation_form').closest('fieldset');
        var professionalFormFieldset = $('.field-professional_evaluation_form').closest('fieldset');

        function updateFormFields() {
            var selectedType = evaluationTypeSelect.val();
            console.log('Selected type:', selectedType); // Debug
            
            if (selectedType === 'SELF') {
                selfFormFieldset.show();
                professionalFormFieldset.hide();
            } else if (selectedType === 'PROFESSIONAL') {
                selfFormFieldset.hide();
                professionalFormFieldset.show();
            }
        }

        // Actualizar campos cuando cambia el tipo de evaluación
        evaluationTypeSelect.on('change', function() {
            console.log('Evaluation type changed'); // Debug
            if (confirm('¿Está seguro de cambiar el tipo de evaluación? Se borrarán los datos del formulario anterior.')) {
                // Enviar el formulario para actualizar
                var continueButton = $(this).closest('form').find('input[name="_continue"]');
                console.log('Continue button found:', continueButton.length > 0); // Debug
                continueButton.click();
            } else {
                // Revertir el cambio
                $(this).val($(this).data('previous-value'));
            }
        });

        // Guardar el valor anterior para poder revertir
        var currentValue = evaluationTypeSelect.val();
        console.log('Initial value:', currentValue); // Debug
        evaluationTypeSelect.data('previous-value', currentValue);

        // Ejecutar al cargar la página
        updateFormFields();
        
        // Debug: Verificar que los fieldsets se encontraron
        console.log('Self fieldset found:', selfFormFieldset.length > 0);
        console.log('Professional fieldset found:', professionalFormFieldset.length > 0);
    });
})();