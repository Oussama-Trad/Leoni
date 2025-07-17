import { BASE_URL } from '../config';

export const fetchFromAPI = async (endpoint, options = {}) => {
  try {
    const response = await fetch(`${BASE_URL}${endpoint}`, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        ...options.headers
      },
      // Supprimer credentials: 'same-origin' pour les appels cross-origin
      // credentials: 'same-origin' ne fonctionne pas avec localhost différents
    });

    if (!response.ok) {
      let errorData = {};
      try {
        errorData = await response.json();
      } catch (e) {
        errorData = { message: await response.text() };
      }
      const error = new Error(errorData.message || `HTTP error! status: ${response.status}`);
      error.status = response.status;
      error.data = errorData;
      throw error;
    }

    return await response.json();
  } catch (error) {
    console.error('API call failed:', {
      endpoint,
      error: error.message,
      status: error.status,
      data: error.data
    });
    throw error;
  }
};