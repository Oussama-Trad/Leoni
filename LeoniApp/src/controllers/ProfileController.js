import { Alert } from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';

const API_BASE_URL = 'http://192.168.1.16:5000/api';

class ProfileController {
  // Récupérer les données du profil utilisateur
  static async fetchUserProfile() {
    try {
      const token = await AsyncStorage.getItem('userToken');
      if (!token) throw new Error('Aucun token trouvé');

      const response = await fetch(`${API_BASE_URL}/me`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.message || 'Erreur lors de la récupération du profil');
      }

      return await response.json();
    } catch (error) {
      console.error('Erreur fetchUserProfile:', error);
      throw error;
    }
  }

  // Mettre à jour le profil utilisateur
  static async updateUserProfile(profileData) {
    try {
      const token = await AsyncStorage.getItem('userToken');
      if (!token) throw new Error('Aucun token trouvé');

      // Validation des données
      this.validateProfileData(profileData);

      const response = await fetch(`${API_BASE_URL}/update-profile`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(profileData)
      });

      const result = await response.json();

      if (!response.ok) {
        throw new Error(result.message || 'Erreur lors de la mise à jour du profil');
      }

      return result;
    } catch (error) {
      console.error('Erreur updateUserProfile:', error);
      throw error;
    }
  }

  // Valider les données du profil
  static validateProfileData(data) {
    const requiredFields = ['firstName', 'lastName', 'email', 'phoneNumber'];
    const missingFields = requiredFields.filter(field => !data[field]);
    
    if (missingFields.length > 0) {
      throw new Error(`Les champs suivants sont obligatoires: ${missingFields.join(', ')}`);
    }

    // Validation de l'email
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(data.email)) {
      throw new Error('Veuillez entrer un email valide');
    }

    // Validation du numéro de téléphone (format français simplifié)
    const phoneRegex = /^(?:(?:\+|00)33|0)\s*[1-9](?:[\s.-]*\d{2}){4}$/;
    if (!phoneRegex.test(data.phoneNumber)) {
      throw new Error('Veuillez entrer un numéro de téléphone valide');
    }
  }

  // Déconnexion de l'utilisateur
  static async logout(navigation) {
    try {
      await AsyncStorage.removeItem('userToken');
      navigation.replace('Login');
    } catch (error) {
      console.error('Erreur lors de la déconnexion:', error);
      throw error;
    }
  }
}

export default ProfileController;
