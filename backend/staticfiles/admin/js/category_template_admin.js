(function() {
    'use strict';
    
    django.jQuery(document).ready(function($) {
        var evaluationTypeSelect = $('#id_evaluation_type');
        var selfFormSection = $('.field-self_evaluation_form').closest('.form-section');
        var professionalFormSection = $('.field-professional_evaluation_results').closest('.form-section');
        
        // Almacenar los valores de los formularios
        var formData = {
            SELF: $('#id_self_evaluation_form').val(),
            PROFESSIONAL: $('#id_professional_evaluation_results').val(),
            TRAINING: $('#id_training_form').val()
        };

        // Función para actualizar la UI según el tipo de evaluación
        function updateFormUI(animate = true) {
            var selectedType = evaluationTypeSelect.val();
            var typeIndicator = $('.evaluation-type-indicator');
            
            // Actualizar indicador visual
            typeIndicator
                .removeClass('evaluation-type-self evaluation-type-professional')
                .addClass('evaluation-type-' + selectedType.toLowerCase())
                .text(selectedType === 'SELF' ? 'Autoevaluación' : 'Evaluación Profesional');
            
            // Mostrar/ocultar secciones correspondientes
            if (selectedType === 'SELF') {
                if (animate) {
                    professionalFormSection.slideUp();
                    selfFormSection.slideDown();
                } else {
                    professionalFormSection.hide();
                    selfFormSection.show();
                }
            } else {
                if (animate) {
                    selfFormSection.slideUp();
                    professionalFormSection.slideDown();
                } else {
                    selfFormSection.hide();
                    professionalFormSection.show();
                }
            }
        }

        // Manejar cambio de tipo de evaluación
        evaluationTypeSelect.on('change', function() {
            var newType = $(this).val();
            var oldType = $(this).data('previous-value');
            
            // Guardar los valores actuales antes del cambio
            formData[oldType] = newType === 'SELF' ? 
                $('#id_professional_evaluation_results').val() : 
                $('#id_self_evaluation_form').val();

            if (confirm('¿Está seguro de cambiar el tipo de evaluación?\nLos formularios anteriores se preservarán.')) {
                $(this).data('previous-value', newType);
                
                // Restaurar los valores previos del tipo seleccionado
                if (newType === 'SELF') {
                    $('#id_self_evaluation_form').val(formData.SELF || '{}');
                } else {
                    $('#id_professional_evaluation_results').val(formData.PROFESSIONAL || '{}');
                }
                
                updateFormUI();
                
                // Mostrar mensaje informativo
                const message = $('<div class="warning-message">')
                    .text('Los formularios anteriores han sido preservados y puede volver a acceder a ellos cambiando el tipo de evaluación.')
                    .hide();
                
                $('.evaluation-type-indicator').after(message);
                message.slideDown().delay(5000).slideUp();
            } else {
                $(this).val(oldType);
            }
        });

        // Función para abrir el modal de gestión de formularios
        window.openFormModal = function(formType) {
            var url = '/admin/form-editor/';
            var title = '';
            var currentData = '';
            
            switch(formType) {
                case 'TRAINING':
                    title = 'Gestionar Nodos de Entrenamiento';
                    currentData = $('#id_training_form').val();
                    break;
                case 'SELF':
                    title = 'Gestionar Preguntas de Autoevaluación';
                    currentData = $('#id_self_evaluation_form').val();
                    break;
                case 'PROFESSIONAL':
                    title = 'Gestionar Formulario Profesional';
                    currentData = $('#id_professional_evaluation_results').val();
                    break;
            }

            // Guardar el estado actual antes de abrir el modal
            formData[formType] = currentData;
            
            // Aquí puedes implementar tu lógica de modal
            // Por ejemplo, usando django-admin-popup o una ventana modal personalizada
        };

        // Función para guardar automáticamente los cambios
        function autoSaveFormData() {
            const currentType = evaluationTypeSelect.val();
            if (currentType === 'SELF') {
                formData.SELF = $('#id_self_evaluation_form').val();
            } else {
                formData.PROFESSIONAL = $('#id_professional_evaluation_results').val();
            }
            formData.TRAINING = $('#id_training_form').val();
        }

        // Auto-guardar cada 30 segundos
        setInterval(autoSaveFormData, 30000);

        // Guardar antes de enviar el formulario
        $('form').on('submit', function() {
            autoSaveFormData();
        });

        // Inicializar UI
        evaluationTypeSelect.data('previous-value', evaluationTypeSelect.val());
        updateFormUI(false);
    });
})();