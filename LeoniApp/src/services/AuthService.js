import AsyncStorage from '@react-native-async-storage/async-storage';
import { BASE_URL } from '../config';

class AuthService {
  // Vérifier si l'utilisateur est connecté
  static async isLoggedIn() {
    try {
      const token = await AsyncStorage.getItem('userToken');
      const userData = await AsyncStorage.getItem('userData');
      
      if (!token || !userData) {
        return false;
      }
      
      // Vérifier si le token est encore valide
      const isValid = await this.validateToken(token);
      if (!isValid) {
        await this.logout();
        return false;
      }
      
      return true;
    } catch (error) {
      console.error('Erreur vérification connexion:', error);
      return false;
    }
  }
  
  // Valider le token avec le serveur
  static async validateToken(token) {
    try {
      const response = await fetch(`${BASE_URL}/me`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        timeout: 5000
      });

      return response.ok;
    } catch (error) {
      console.error('Erreur validation token:', error);
      // En cas d'erreur réseau, considérer le token comme valide localement
      // pour permettre l'utilisation hors ligne
      if (error.message.includes('fetch') || error.message.includes('Network')) {
        console.log('Mode hors ligne détecté, token considéré comme valide');
        return true;
      }
      return false;
    }
  }
  
  // Récupérer les données utilisateur
  static async getUserData() {
    try {
      const userData = await AsyncStorage.getItem('userData');
      return userData ? JSON.parse(userData) : null;
    } catch (error) {
      console.error('Erreur récupération données utilisateur:', error);
      return null;
    }
  }
  
  // Récupérer le token
  static async getToken() {
    try {
      return await AsyncStorage.getItem('userToken');
    } catch (error) {
      console.error('Erreur récupération token:', error);
      return null;
    }
  }
  
  // Sauvegarder les données de connexion
  static async saveAuthData(token, userData) {
    try {
      // Compléter automatiquement les données utilisateur avec les valeurs par défaut
      const completeUserData = {
        ...userData,
        phoneNumber: userData.phoneNumber || '12345678',
        parentalEmail: userData.parentalEmail || 'aa@gmail.com',
        parentalPhoneNumber: userData.parentalPhoneNumber || '12345899',
        department: userData.department || 'Non spécifié',
        position: userData.position || 'Non spécifié',
        address: userData.address || '',
        profilePicture: userData.profilePicture || null
      };

      await AsyncStorage.setItem('userToken', token);
      await AsyncStorage.setItem('userData', JSON.stringify(completeUserData));
      console.log('✅ AUTH: Données complètes sauvegardées:', completeUserData);
      return true;
    } catch (error) {
      console.error('Erreur sauvegarde données auth:', error);
      return false;
    }
  }
  
  // Déconnexion
  static async logout() {
    try {
      await AsyncStorage.multiRemove(['userToken', 'userData']);
      return true;
    } catch (error) {
      console.error('Erreur déconnexion:', error);
      return false;
    }
  }
  
  // Connexion
  static async login(email, password) {
    try {
      const response = await fetch(`${BASE_URL}/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email: email.trim().toLowerCase(),
          password: password
        })
      });
      
      const data = await response.json();
      
      if (data.success) {
        await this.saveAuthData(data.token, data.user);
        return { success: true, user: data.user, token: data.token };
      } else {
        return { success: false, message: data.message };
      }
    } catch (error) {
      console.error('Erreur connexion:', error);
      return { success: false, message: 'Erreur de connexion' };
    }
  }
  
  // Demande de réinitialisation de mot de passe
  static async requestPasswordReset(email) {
    try {
      const response = await fetch(`${BASE_URL}/forgot-password`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email: email.trim().toLowerCase() })
      });
      
      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Erreur demande reset password:', error);
      return { success: false, message: 'Erreur de connexion' };
    }
  }
  
  // Réinitialisation de mot de passe avec token
  static async resetPassword(token, newPassword) {
    try {
      const response = await fetch(`${BASE_URL}/reset-password`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ token, newPassword })
      });
      
      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Erreur reset password:', error);
      return { success: false, message: 'Erreur de connexion' };
    }
  }
}

export default AuthService;
