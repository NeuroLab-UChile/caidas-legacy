// Mejoras de interactividad
document.addEventListener('DOMContentLoaded', function() {
    // Confirmación personalizada para acciones peligrosas
    const dangerousActions = document.querySelectorAll('.deletelink');
    dangerousActions.forEach(action => {
        action.addEventListener('click', function(e) {
            if (!confirm('¿Está seguro de realizar esta acción? Esta operación no se puede deshacer.')) {
                e.preventDefault();
            }
        });
    });

    // Previsualización de imágenes
    const imageInputs = document.querySelectorAll('input[type="file"][accept*="image"]');
    imageInputs.forEach(input => {
        input.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    let preview = document.getElementById('image-preview');
                    if (!preview) {
                        preview = document.createElement('img');
                        preview.id = 'image-preview';
                        preview.style.maxWidth = '200px';
                        preview.style.marginTop = '10px';
                        input.parentNode.appendChild(preview);
                    }
                    preview.src = e.target.result;
                }
                reader.readAsDataURL(file);
            }
        });
    });
}); 