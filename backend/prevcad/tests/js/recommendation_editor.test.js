describe('Recommendation Editor', () => {
    let container;
    let form;
    let mockElements;

    // Mock de fetch
    global.fetch = jest.fn(() =>
        Promise.resolve({
            ok: true,
            status: 200,
            text: () => Promise.resolve(JSON.stringify({ success: true })),
            headers: new Map([['content-type', 'application/json']])
        })
    );

    beforeEach(() => {
        // Configurar el DOM para testing
        container = document.createElement('div');
        document.body.appendChild(container);

        // Crear elementos necesarios
        form = document.createElement('form');
        form.id = 'healthcategory_form';
        
        mockElements = {
            defaultRecommendations: document.createElement('div'),
            defaultRadio: document.createElement('input'),
            customRadio: document.createElement('input'),
            recommendationText: document.createElement('textarea'),
            statusColor: document.createElement('select'),
            isDraft: document.createElement('input'),
            videoInput: document.createElement('input'),
            removeVideoBtn: document.createElement('button'),
            csrfToken: document.createElement('input')
        };

        // Configurar elementos
        mockElements.defaultRecommendations.id = 'defaultRecommendations';
        mockElements.defaultRecommendations.textContent = JSON.stringify({
            no_risk: 'Recomendación sin riesgo',
            prev_risk: 'Recomendación riesgo previo',
            risk: 'Recomendación con riesgo',
            pending: 'Recomendación pendiente'
        });

        mockElements.defaultRadio.id = 'use-default';
        mockElements.defaultRadio.type = 'radio';
        mockElements.defaultRadio.name = 'recommendation-type';

        mockElements.customRadio.id = 'use-custom';
        mockElements.customRadio.type = 'radio';
        mockElements.customRadio.name = 'recommendation-type';

        mockElements.recommendationText.id = 'recommendation-text';
        
        mockElements.statusColor.id = 'status-color';
        ['verde', 'amarillo', 'rojo', 'gris'].forEach(color => {
            const option = document.createElement('option');
            option.value = color;
            option.textContent = color;
            mockElements.statusColor.appendChild(option);
        });

        mockElements.isDraft.id = 'is-draft';
        mockElements.isDraft.type = 'checkbox';

        mockElements.videoInput.id = 'video-input';
        mockElements.videoInput.type = 'file';
        mockElements.videoInput.accept = 'video/*';

        mockElements.removeVideoBtn.id = 'remove-video';
        mockElements.removeVideoBtn.textContent = 'Eliminar video';

        mockElements.csrfToken.name = 'csrfmiddlewaretoken';
        mockElements.csrfToken.value = 'mock-csrf-token';

        // Agregar elementos al form
        Object.values(mockElements).forEach(element => {
            form.appendChild(element);
        });

        container.appendChild(form);

        // Cargar el script
        require('../templates/admin/js/recommendation_editor.js');
    });

    afterEach(() => {
        document.body.removeChild(container);
        jest.clearAllMocks();
    });

    test('carga inicial correcta', () => {
        expect(document.getElementById('healthcategory_form')).toBeTruthy();
        expect(document.getElementById('recommendation-text')).toBeTruthy();
        expect(document.getElementById('status-color')).toBeTruthy();
    });

    test('actualización de recomendación por defecto', () => {
        mockElements.defaultRadio.checked = true;
        mockElements.defaultRadio.dispatchEvent(new Event('change'));
        mockElements.statusColor.value = 'verde';
        mockElements.statusColor.dispatchEvent(new Event('change'));

        expect(mockElements.recommendationText.value).toBe('Recomendación sin riesgo');
        expect(mockElements.recommendationText.disabled).toBe(true);
    });

    test('manejo de video', () => {
        const file = new File(['dummy content'], 'test.mp4', { type: 'video/mp4' });
        Object.defineProperty(mockElements.videoInput, 'files', {
            value: [file]
        });

        mockElements.videoInput.dispatchEvent(new Event('change'));
        
        // Verificar que se actualizaron los campos ocultos
        const videoField = form.querySelector('input[name="video"]');
        expect(videoField).toBeTruthy();
        expect(videoField.value).toBe('test.mp4');
    });

    test('envío del formulario', async () => {
        const submitEvent = new Event('submit');
        form.dispatchEvent(submitEvent);

        expect(global.fetch).toHaveBeenCalledTimes(1);
        expect(global.fetch).toHaveBeenCalledWith(
            expect.any(String),
            expect.objectContaining({
                method: 'POST',
                headers: expect.objectContaining({
                    'X-CSRFToken': 'mock-csrf-token'
                })
            })
        );
    });

    test('manejo de errores de video', () => {
        const largeFile = new File(['dummy'.repeat(1000000)], 'large.mp4', { type: 'video/mp4' });
        const alertMock = jest.spyOn(window, 'alert').mockImplementation(() => {});

        Object.defineProperty(mockElements.videoInput, 'files', {
            value: [largeFile]
        });

        mockElements.videoInput.dispatchEvent(new Event('change'));
        
        expect(alertMock).toHaveBeenCalledWith('El archivo es demasiado grande. Máximo 100MB.');
        expect(mockElements.videoInput.value).toBe('');
    });
});

describe('Video Upload Functionality', () => {
    let form;
    let videoInput;
    let submitButton;
    
    beforeEach(() => {
        // Configurar el DOM
        document.body.innerHTML = `
            <form id="healthcategory_form">
                <input type="file" id="video-input" accept="video/*">
                <input type="hidden" name="csrfmiddlewaretoken" value="mock-token">
                <button type="submit">Guardar</button>
            </form>
        `;
        
        form = document.getElementById('healthcategory_form');
        videoInput = document.getElementById('video-input');
        submitButton = form.querySelector('button[type="submit"]');
        
        // Mock fetch para simular respuesta del servidor
        global.fetch = jest.fn(() =>
            Promise.resolve({
                ok: true,
                status: 200,
                text: () => Promise.resolve(JSON.stringify({
                    success: true,
                    video_url: '/media/recommendations/videos/test-video.mp4'
                })),
                headers: new Map([['content-type', 'application/json']])
            })
        );
    });

    test('subida exitosa de video', async () => {
        // Crear un archivo de video simulado
        const videoFile = new File(
            ['video content'], 
            'test-video.mp4', 
            { type: 'video/mp4' }
        );

        // Simular la selección del archivo
        Object.defineProperty(videoInput, 'files', {
            value: [videoFile]
        });
        videoInput.dispatchEvent(new Event('change'));

        // Verificar que el archivo se agregó correctamente
        expect(videoInput.files[0].name).toBe('test-video.mp4');

        // Simular el envío del formulario
        const formData = new FormData();
        formData.append('video', videoFile);
        
        form.dispatchEvent(new Event('submit'));

        // Esperar a que se complete la solicitud fetch
        await new Promise(resolve => setTimeout(resolve, 0));

        // Verificar que fetch fue llamado correctamente
        expect(global.fetch).toHaveBeenCalledTimes(1);
        expect(global.fetch).toHaveBeenCalledWith(
            expect.any(String),
            expect.objectContaining({
                method: 'POST',
                headers: expect.objectContaining({
                    'X-CSRFToken': 'mock-token'
                })
            })
        );

        // Verificar que el botón de submit se deshabilitó durante la subida
        expect(submitButton.disabled).toBe(true);
        expect(submitButton.textContent).toBe('Guardando...');

        // Verificar que el formulario se procesa correctamente después de la subida
        await new Promise(resolve => setTimeout(resolve, 1100)); // Esperar el timeout de recarga
        expect(window.location.reload).toHaveBeenCalled();
    });

    test('manejo de error en la subida', async () => {
        // Mock fetch para simular error
        global.fetch.mockImplementationOnce(() =>
            Promise.resolve({
                ok: false,
                status: 400,
                text: () => Promise.resolve(JSON.stringify({
                    error: 'Error al subir el video'
                }))
            })
        );

        const videoFile = new File(
            ['video content'], 
            'test-video.mp4', 
            { type: 'video/mp4' }
        );

        Object.defineProperty(videoInput, 'files', {
            value: [videoFile]
        });
        videoInput.dispatchEvent(new Event('change'));

        // Mock alert para verificar mensaje de error
        const alertMock = jest.spyOn(window, 'alert').mockImplementation(() => {});

        form.dispatchEvent(new Event('submit'));
        
        await new Promise(resolve => setTimeout(resolve, 0));

        expect(alertMock).toHaveBeenCalledWith(
            expect.stringContaining('Error al guardar los cambios')
        );
        expect(submitButton.disabled).toBe(false);
        expect(submitButton.textContent).toBe('Guardar cambios');
    });

    test('validación de tamaño de archivo', () => {
        // Crear un archivo grande (> 100MB)
        const largeVideoFile = new File(
            [new ArrayBuffer(101 * 1024 * 1024)], // 101MB
            'large-video.mp4',
            { type: 'video/mp4' }
        );

        const alertMock = jest.spyOn(window, 'alert').mockImplementation(() => {});

        Object.defineProperty(videoInput, 'files', {
            value: [largeVideoFile]
        });
        videoInput.dispatchEvent(new Event('change'));

        expect(alertMock).toHaveBeenCalledWith('El archivo es demasiado grande. Máximo 100MB.');
        expect(videoInput.value).toBe('');
    });
}); 