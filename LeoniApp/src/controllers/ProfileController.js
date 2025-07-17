import AsyncStorage from '@react-native-async-storage/async-storage';
import { BASE_URL } from '../config';

export const getProfile = async () => {
  try {
    const token = await AsyncStorage.getItem('userToken');
    if (!token) {
      throw new Error('Token non trouvé');
    }

    const response = await fetch(`${BASE_URL}/me`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    if (data.success) {
      return data;
    } else {
      throw new Error(data.message || 'Erreur lors de la récupération du profil');
    }
  } catch (error) {
    throw new Error(error.message || 'Failed to fetch profile');
  }
};

export const updateProfile = async (profileData) => {
  try {
    const token = await AsyncStorage.getItem('userToken');
    if (!token) {
      throw new Error('Token non trouvé');
    }

    const response = await fetch(`${BASE_URL}/update-profile`, {
      method: 'PUT',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        ...profileData,
        updatedAt: new Date()
      })
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    if (data.success) {
      return data;
    } else {
      throw new Error(data.message || 'Erreur lors de la mise à jour du profil');
    }
  } catch (error) {
    throw new Error(error.message || 'Failed to update profile');
  }
};

export const uploadProfilePicture = async (imageUri) => {
  try {
    const token = await AsyncStorage.getItem('userToken');
    if (!token) {
      throw new Error('Token non trouvé');
    }

    // Convertir l'image en base64
    const response = await fetch(imageUri);
    const blob = await response.blob();

    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onloadend = async () => {
        try {
          const base64data = reader.result;

          const uploadResponse = await fetch(`${BASE_URL}/upload-profile-picture`, {
            method: 'POST',
            headers: {
              'Authorization': `Bearer ${token}`,
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              imageData: base64data
            })
          });

          if (!uploadResponse.ok) {
            throw new Error(`HTTP error! status: ${uploadResponse.status}`);
          }

          const data = await uploadResponse.json();
          if (data.success) {
            resolve(data);
          } else {
            throw new Error(data.message || 'Erreur lors de l\'upload');
          }
        } catch (error) {
          reject(error);
        }
      };
      reader.onerror = () => reject(new Error('Erreur lecture fichier'));
      reader.readAsDataURL(blob);
    });
  } catch (error) {
    throw new Error(error.message || 'Erreur lors de l\'upload de l\'image');
  }
};

export const logout = async () => {
  try {
    await AsyncStorage.multiRemove(['userToken', 'userData']);
    return { success: true };
  } catch (error) {
    throw new Error('Erreur lors de la déconnexion');
  }
};
