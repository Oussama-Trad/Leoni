import requests
import json

# URL de l'API
url = "http://localhost:5000/register"

# Données de test
data = {
    "firstName": "Test",
    "lastName": "User",
    "email": "test@example.com",
    "parentalEmail": "parent@example.com",
    "phoneNumber": "0123456789",
    "parentalPhoneNumber": "0987654321",
    "password": "password123",
    "confirmPassword": "password123"
}

headers = {
    'Content-Type': 'application/json'
}

try:
    # Envoyer la requête
    response = requests.post(url, headers=headers, data=json.dumps(data))
    
    # Afficher la réponse
    print("Status Code:", response.status_code)
    print("Response:", response.text)
    
except requests.exceptions.RequestException as e:
    print("Erreur de connexion:", str(e))
