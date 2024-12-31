document.addEventListener('DOMContentLoaded', function() {
    const evaluationTypeSelect = document.getElementById('id_evaluation_type');
    const evaluationFormField = document.getElementById('id_evaluation_form');
    const professionalFormField = document.getElementById('id_professional_evaluation_results');

    if (evaluationTypeSelect) {
        evaluationTypeSelect.addEventListener('change', function(e) {
            const selectedType = e.target.value;
            
            if (selectedType === 'SELF') {
                // Mostrar formulario de autoevaluación y limpiar el profesional
                if (professionalFormField) {
                    professionalFormField.value = JSON.stringify({"question_nodes": []});
                }
                // Ocultar/mostrar los fieldsets correspondientes
                document.querySelector('.field-professional_evaluation_results').closest('fieldset').style.display = 'none';
                document.querySelector('.field-evaluation_form').closest('fieldset').style.display = 'block';
            } else if (selectedType === 'PROFESSIONAL') {
                // Mostrar formulario profesional y limpiar el de autoevaluación
                if (evaluationFormField) {
                    evaluationFormField.value = JSON.stringify({"question_nodes": []});
                }
                // Ocultar/mostrar los fieldsets correspondientes
                document.querySelector('.field-evaluation_form').closest('fieldset').style.display = 'none';
                document.querySelector('.field-professional_evaluation_results').closest('fieldset').style.display = 'block';
            }
        });
    }
}); 