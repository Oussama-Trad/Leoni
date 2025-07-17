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

export const logout = async () => {
  try {
    await AsyncStorage.multiRemove(['userToken', 'userData']);
    return { success: true };
  } catch (error) {
    throw new Error('Erreur lors de la déconnexion');
  }
};
