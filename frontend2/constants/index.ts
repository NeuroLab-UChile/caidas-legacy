export const API_URL = __DEV__ 
  ? 'https://caidas.uchile.cl/api'  // Desarrollo
  : 'https://caidas.uchile.cl/api'; // Producción

// Añade logs para debug
if (__DEV__) {
  console.log('Running in Development mode');
  console.log('API URL:', API_URL);
} else {
  console.log('Running in Production mode');
  console.log('API URL:', API_URL);
}