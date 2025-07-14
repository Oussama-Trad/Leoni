class AppController {
  constructor() {
    // Utiliser l'adresse IP du réseau Wi-Fi pour le développement
    this.apiBaseUrl = 'http://192.168.1.16:5000'; // URL du serveur backend
  }

  // Méthode pour tester la connexion au serveur
  async testConnection() {
    try {
      const response = await fetch(`${this.apiBaseUrl}/health`, {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' },
      });
      const result = await response.json();
      console.log('Test de connexion:', result);
      return result;
    } catch (error) {
      console.error('Erreur de test de connexion:', error);
      return { success: false, message: 'Impossible de se connecter au serveur: ' + error.message };
    }
  }

  async login(email, password) {
    try {
      // Tester la connexion d'abord
      const healthCheck = await this.testConnection();
      if (!healthCheck.success) {
        return { success: false, message: 'Serveur inaccessible. Vérifiez que le backend est démarré.' };
      }

      const response = await fetch(`${this.apiBaseUrl}/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: email.trim(), password }),
      });

      const result = await response.json();
      
      if (result.success) {
        console.log('Connexion réussie:', result.user);
      } else {
        console.error('Erreur de connexion:', result.message);
      }
      
      return result;
    } catch (error) {
      console.error('Erreur réseau login:', error);
      return { 
        success: false, 
        message: 'Erreur réseau. Vérifiez votre connexion et que le serveur est démarré.' 
      };
    }
  }

  async register(userData) {
    try {
      // Tester la connexion d'abord
      const healthCheck = await this.testConnection();
      if (!healthCheck.success) {
        return { success: false, message: 'Serveur inaccessible. Vérifiez que le backend est démarré.' };
      }

      // Nettoyer les données avant l'envoi
      const cleanedData = {
        firstName: userData.firstName.trim(),
        lastName: userData.lastName.trim(),
        email: userData.email.trim().toLowerCase(),
        parentalEmail: userData.parentalEmail.trim().toLowerCase(),
        phoneNumber: userData.phoneNumber.trim(),
        parentalPhoneNumber: userData.parentalPhoneNumber.trim(),
        password: userData.password,
        confirmPassword: userData.confirmPassword,
      };

      console.log('Données d\'inscription envoyées:', {
        ...cleanedData,
        password: '[MASQUÉ]',
        confirmPassword: '[MASQUÉ]'
      });

      const response = await fetch(`${this.apiBaseUrl}/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(cleanedData),
      });

      const result = await response.json();
      
      if (result.success) {
        console.log('Inscription réussie:', result.user);
      } else {
        console.error('Erreur d\'inscription:', result.message);
      }
      
      return result;
    } catch (error) {
      console.error('Erreur réseau register:', error);
      return { 
        success: false, 
        message: 'Erreur réseau. Vérifiez votre connexion et que le serveur est démarré.' 
      };
    }
  }

  async submitDocumentRequest(token, requestData) {
    try {
      const response = await fetch(`${this.apiBaseUrl}/document-request`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify(requestData),
      });

      const result = await response.json();
      
      if (result.success) {
        console.log('Demande de document soumise:', result.request);
      } else {
        console.error('Erreur de soumission:', result.message);
      }
      
      return result;
    } catch (error) {
      console.error('Erreur réseau submitDocumentRequest:', error);
      return { 
        success: false, 
        message: 'Erreur réseau lors de la soumission de la demande.' 
      };
    }
  }

  async getDocumentRequests(token) {
    try {
      const response = await fetch(`${this.apiBaseUrl}/document-requests`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      const result = await response.json();
      
      if (result.success) {
        console.log('Demandes récupérées:', result.requests.length);
      } else {
        console.error('Erreur de récupération:', result.message);
      }
      
      return result;
    } catch (error) {
      console.error('Erreur réseau getDocumentRequests:', error);
      return { 
        success: false, 
        message: 'Erreur réseau lors de la récupération des demandes.' 
      };
    }
  }

  async logout() {
    try {
      // Nettoyer le token localement
      // Pour React Native, vous pourriez utiliser AsyncStorage
      // await AsyncStorage.removeItem('userToken');
      
      console.log('Déconnexion effectuée');
      return { success: true, message: 'Déconnexion réussie' };
    } catch (error) {
      console.error('Erreur lors de la déconnexion:', error);
      return { success: false, message: 'Erreur lors de la déconnexion' };
    }
  }

  async getProfile() {
    try {
      const token = await AsyncStorage.getItem('userToken');
      if (!token) throw new Error('Aucun token trouvé');
      
      const response = await fetch(`${this.apiBaseUrl}/me`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      
      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.message || 'Une erreur est survenue');
      }
      return data;
    } catch (error) {
      console.error('Erreur getProfile:', error);
      throw error;
    }
  }

  async updateProfile(profileData) {
    try {
      const token = await AsyncStorage.getItem('userToken');
      if (!token) throw new Error('Aucun token trouvé');
      
      const response = await fetch(`${this.apiBaseUrl}/update-profile`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(profileData)
      });
      
      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.message || 'Une erreur est survenue');
      }
      return data;
    } catch (error) {
      console.error('Erreur updateProfile:', error);
      throw error;
    }
  }

  // Méthode utilitaire pour obtenir l'IP locale
  getLocalIP() {
    return `
Pour React Native, vous devez remplacer 'localhost' par l'IP de votre machine:
1. Ouvrez un terminal/invite de commande
2. Tapez: ipconfig (Windows) ou ifconfig (Mac/Linux)
3. Trouvez votre adresse IP locale (ex: 192.168.1.100)
4. Remplacez l'IP dans apiBaseUrl

Pour le web, utilisez: http://localhost:5000
    `;
  }
}

export default AppController;