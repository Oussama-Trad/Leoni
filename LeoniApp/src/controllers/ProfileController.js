import { Alert } from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { jwtDecode } from 'jwt-decode';

const API_BASE_URL = 'http://localhost:5000/api';

class ProfileController {
  static async fetchUserProfile() {
    try {
      const token = await AsyncStorage.getItem('userToken');
      if (!token) throw new Error('Aucun token trouvé');

      // Utilisation correcte de jwtDecode avec le token récupéré
      const decoded = jwtDecode(token);
      
      if (!decoded?.userId) {
        throw new Error('Token invalide - userId manquant');
      }

      const response = await fetch(`${API_BASE_URL}/api/users/${decoded.userId}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      // Vérifier d'abord le type de contenu
      const contentType = response.headers.get('content-type');
      if (!contentType.includes('application/json')) {
        throw new Error(`Réponse non-JSON reçue: ${contentType}`);
      }

      if (!response.ok) {
        try {
          const error = await response.json();
          throw new Error(error.message || response.statusText);
        } catch (parseError) {
          throw new Error(`Erreur HTTP ${response.status}: ${await response.text()}`);
        }
      }

      try {
        return await response.json();
      } catch (parseError) {
        throw new Error('Format de réponse invalide');
      }
    } catch (error) {
      console.error('Erreur fetchUserProfile:', error);
      throw error;
    }
  }
  
  // ... (le reste du fichier reste inchangé)
}

export default ProfileController;
