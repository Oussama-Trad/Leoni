import { Platform } from 'react-native';

// Détection automatique de l'environnement
const getBaseURL = () => {
  // Si on est sur le web (navigateur), utiliser localhost
  if (Platform.OS === 'web') {
    return 'http://localhost:5000';
  }

  // Si on est sur mobile (Expo Go), utiliser l'IP locale du PC
  // Remplacez cette IP par celle de votre PC (trouvée avec ipconfig)
  return 'http://192.168.1.16:5000';
};

export const BASE_URL = getBaseURL();
