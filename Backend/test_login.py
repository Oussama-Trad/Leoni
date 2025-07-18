import requests
import json

# Test de connexion au serveur
def test_login():
    url = "http://localhost:5000/login"
    data = {
        "email": "t@gmail.com",
        "password": "123456"
    }
    
    try:
        print(f"🔍 Test de connexion à {url}")
        print(f"🔍 Données envoyées: {data}")
        
        response = requests.post(url, json=data, headers={'Content-Type': 'application/json'})
        
        print(f"🔍 Status code: {response.status_code}")
        print(f"🔍 Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            print(f"✅ Réponse: {response.json()}")
        else:
            print(f"❌ Erreur {response.status_code}")
            try:
                print(f"❌ Réponse: {response.json()}")
            except:
                print(f"❌ Réponse brute: {response.text}")
                
    except Exception as e:
        print(f"❌ Erreur de connexion: {e}")

if __name__ == "__main__":
    test_login()
