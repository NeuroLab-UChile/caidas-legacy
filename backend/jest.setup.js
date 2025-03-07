// Mock de window.location
Object.defineProperty(window, 'location', {
    value: {
        href: 'http://test.com',
        reload: jest.fn()
    },
    writable: true
});

// Mock de console.log y console.error para tests más limpios
global.console = {
    log: jest.fn(),
    error: jest.fn(),
    warn: jest.fn()
}; 