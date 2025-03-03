export const getMediaUrl = (path: string) => {
  if (!path) return null;
  
  // Asegurarnos de que el path no empiece con slash
  const cleanPath = path.startsWith('/') ? path.slice(1) : path;
  
  return `https://caidas.uchile.cl/media/${cleanPath}`;
}; 