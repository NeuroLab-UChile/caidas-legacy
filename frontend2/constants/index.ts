// https://docs.expo.dev/workflow/development-mode/
export const API_URL = __DEV__
  ? "http://192.168.1.227:8000/api" // Desarrollo
  : "https://caidas.uchile.cl/api"; // Producción

// Añade logs para debug
if (__DEV__) console.log("Running in Development mode");
else console.log("Running in Production mode");
console.log("API URL:", API_URL);
