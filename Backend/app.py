from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime, timedelta
import bcrypt
import jwt
from dotenv import load_dotenv
import os
import re

app = Flask(__name__)
CORS(app)  # Permettre les requêtes cross-origin

# Charger les variables d'environnement
load_dotenv()
MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
JWT_SECRET_KEY = os.getenv('mongodb://localhost:27017/', '123')

# Configuration de la connexion MongoDB avec gestion d'erreurs
try:
    client = MongoClient(MONGODB_URI)
    # Tester la connexion
    client.server_info()
    print("✅ Connexion MongoDB réussie")
    
    db = client['LeoniApp']
    users_collection = db['users']
    document_requests_collection = db['document_requests']
    
    # Créer les index pour optimiser les requêtes
    users_collection.create_index([("email", 1)], unique=True)
    users_collection.create_index([("parentalEmail", 1)], unique=True)
    users_collection.create_index([("employeeId", 1)], unique=True)
    
except Exception as e:
    print(f"❌ Erreur de connexion MongoDB: {e}")
    exit(1)

# Validation de l'email
def is_valid_email(email):
    email_regex = r'^[^\s@]+@[^\s@]+\.[^\s@]+$'
    return re.match(email_regex, email) is not None

# Validation du numéro de téléphone
def is_valid_phone(phone):
    # Accepter les formats internationaux et locaux
    phone_regex = r'^\+?[\d\s\-\(\)]{8,15}$'
    return re.match(phone_regex, phone.strip()) is not None

# Générer un employeeId unique
def generate_employee_id():
    try:
        # Compter le nombre total d'utilisateurs
        count = users_collection.count_documents({})
        employee_id = f"EMP{str(count + 1).zfill(3)}"
        
        # Vérifier que l'ID n'existe pas déjà
        while users_collection.find_one({'employeeId': employee_id}):
            count += 1
            employee_id = f"EMP{str(count + 1).zfill(3)}"
        
        return employee_id
    except Exception as e:
        print(f"Erreur lors de la génération de l'employeeId: {e}")
        return f"EMP{str(datetime.now().timestamp()).replace('.', '')[-6:]}"

# Middleware pour vérifier le token JWT
def verify_token(token):
    try:
        decoded = jwt.decode(token, JWT_SECRET_KEY, algorithms=['HS256'])
        return decoded
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

# Route pour tester la connexion
@app.route('/health', methods=['GET'])
def health_check():
    try:
        # Tester la connexion MongoDB
        client.server_info()
        return jsonify({
            'success': True,
            'message': 'Serveur en ligne',
            'mongodb': 'Connecté',
            'timestamp': datetime.utcnow().isoformat()
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Erreur serveur',
            'error': str(e)
        }), 500

# Route pour l'inscription
@app.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'message': 'Données manquantes'}), 400
        
        required_fields = ['firstName', 'lastName', 'email', 'parentalEmail', 'phoneNumber', 'parentalPhoneNumber', 'password', 'confirmPassword']
        
        # Vérifier que tous les champs requis sont présents
        missing_fields = [field for field in required_fields if field not in data or not data[field].strip()]
        if missing_fields:
            return jsonify({
                'success': False, 
                'message': f'Champs manquants: {", ".join(missing_fields)}'
            }), 400

        # Validation des données
        if not is_valid_email(data['email']):
            return jsonify({'success': False, 'message': 'Format email personnel invalide'}), 400
        
        if not is_valid_email(data['parentalEmail']):
            return jsonify({'success': False, 'message': 'Format email parental invalide'}), 400
        
        if data['email'].lower() == data['parentalEmail'].lower():
            return jsonify({'success': False, 'message': 'Les emails doivent être différents'}), 400
        
        if not is_valid_phone(data['phoneNumber']):
            return jsonify({'success': False, 'message': 'Format numéro de téléphone personnel invalide'}), 400
        
        if not is_valid_phone(data['parentalPhoneNumber']):
            return jsonify({'success': False, 'message': 'Format numéro de téléphone parental invalide'}), 400
        
        if data['password'] != data['confirmPassword']:
            return jsonify({'success': False, 'message': 'Les mots de passe ne correspondent pas'}), 400
        
        if len(data['password']) < 6:
            return jsonify({'success': False, 'message': 'Le mot de passe doit contenir au moins 6 caractères'}), 400

        # Vérifier si l'email existe déjà
        if users_collection.find_one({'email': data['email'].lower()}):
            return jsonify({'success': False, 'message': 'Un compte avec cet email personnel existe déjà'}), 400
        
        if users_collection.find_one({'parentalEmail': data['parentalEmail'].lower()}):
            return jsonify({'success': False, 'message': 'Un compte avec cet email parental existe déjà'}), 400

        # Hacher le mot de passe
        hashed_password = bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt())

        # Générer un employeeId unique
        employee_id = generate_employee_id()

        # Créer l'utilisateur
        user = {
            'firstName': data['firstName'].strip(),
            'lastName': data['lastName'].strip(),
            'email': data['email'].lower().strip(),
            'parentalEmail': data['parentalEmail'].lower().strip(),
            'phoneNumber': data['phoneNumber'].strip(),
            'parentalPhoneNumber': data['parentalPhoneNumber'].strip(),
            'password': hashed_password,
            'employeeId': employee_id,
            'department': 'Non spécifié',
            'position': 'Non spécifié',
            'createdAt': datetime.utcnow(),
            'updatedAt': datetime.utcnow()
        }

        # Insérer l'utilisateur dans la base de données
        result = users_collection.insert_one(user)
        
        # Vérifier que l'insertion a réussi
        if not result.inserted_id:
            return jsonify({'success': False, 'message': 'Erreur lors de la création du compte'}), 500

        # Générer un token JWT
        token = jwt.encode({
            'userId': str(result.inserted_id),
            'email': user['email'],
            'exp': datetime.utcnow() + timedelta(hours=24)
        }, JWT_SECRET_KEY, algorithm='HS256')

        print(f"✅ Nouvel utilisateur créé: {user['email']} (ID: {employee_id})")

        return jsonify({
            'success': True,
            'message': 'Inscription réussie',
            'user': {
                'id': str(result.inserted_id),
                'firstName': user['firstName'],
                'lastName': user['lastName'],
                'email': user['email'],
                'parentalEmail': user['parentalEmail'],
                'phoneNumber': user['phoneNumber'],
                'parentalPhoneNumber': user['parentalPhoneNumber'],
                'employeeId': user['employeeId']
            },
            'token': token
        }), 201

    except Exception as e:
        print(f"❌ Erreur lors de l'inscription: {e}")
        return jsonify({
            'success': False, 
            'message': 'Erreur serveur lors de l\'inscription',
            'error': str(e)
        }), 500

# Route pour la connexion
@app.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        
        if not data or not all(field in data for field in ['email', 'password']):
            return jsonify({'success': False, 'message': 'Email et mot de passe requis'}), 400

        user = users_collection.find_one({'email': data['email'].lower().strip()})
        if not user:
            return jsonify({'success': False, 'message': 'Email ou mot de passe incorrect'}), 401

        if not bcrypt.checkpw(data['password'].encode('utf-8'), user['password']):
            return jsonify({'success': False, 'message': 'Email ou mot de passe incorrect'}), 401

        # Mettre à jour la date de dernière connexion
        users_collection.update_one(
            {'_id': user['_id']},
            {'$set': {'lastLogin': datetime.utcnow()}}
        )

        token = jwt.encode({
            'userId': str(user['_id']),
            'email': user['email'],
            'exp': datetime.utcnow() + timedelta(hours=24)
        }, JWT_SECRET_KEY, algorithm='HS256')

        print(f"✅ Connexion réussie: {user['email']}")

        return jsonify({
            'success': True,
            'message': 'Connexion réussie',
            'user': {
                'id': str(user['_id']),
                'firstName': user['firstName'],
                'lastName': user['lastName'],
                'email': user['email'],
                'parentalEmail': user['parentalEmail'],
                'phoneNumber': user['phoneNumber'],
                'parentalPhoneNumber': user['parentalPhoneNumber'],
                'employeeId': user['employeeId']
            },
            'token': token
        }), 200

    except Exception as e:
        print(f"❌ Erreur lors de la connexion: {e}")
        return jsonify({
            'success': False,
            'message': 'Erreur serveur lors de la connexion',
            'error': str(e)
        }), 500

# Route pour soumettre une demande de document
@app.route('/document-request', methods=['POST'])
def submit_document_request():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': 'Données manquantes'}), 400

        # Vérifier les champs requis
        required_fields = ['userId', 'documentType']
        missing_fields = [field for field in required_fields if field not in data or not str(data[field]).strip()]
        if missing_fields:
            return jsonify({
                'success': False, 
                'message': f'Champs manquants: {", ".join(missing_fields)}'
            }), 400

        # Vérifier que l'utilisateur existe
        user = users_collection.find_one({'_id': ObjectId(data['userId'])})
        if not user:
            return jsonify({'success': False, 'message': 'Utilisateur non trouvé'}), 404

        request_data = {
            'userId': data['userId'],
            'documentType': data['documentType'].strip(),
            'description': data.get('description', '').strip() if data.get('description') else '',
            'status': 'en attente',
            'createdAt': datetime.utcnow(),
            'updatedAt': datetime.utcnow()
        }

        result = document_requests_collection.insert_one(request_data)

        print(f"✅ Nouvelle demande de document: {data['documentType']} par {data['userId']}")

        return jsonify({
            'success': True,
            'message': 'Demande enregistrée'
        }), 201

    except Exception as e:
        print(f"❌ Erreur lors de la soumission de demande: {e}")
        return jsonify({
            'success': False,
            'message': 'Erreur serveur lors de la soumission',
            'error': str(e)
        }), 500

# Route pour récupérer les demandes de documents
@app.route('/document-requests', methods=['GET'])
def get_document_requests():
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'success': False, 'message': 'Token manquant ou invalide'}), 401

        token = auth_header.split(" ")[1]
        decoded = verify_token(token)
        if not decoded:
            return jsonify({'success': False, 'message': 'Token invalide ou expiré'}), 401

        requests = list(document_requests_collection.find({'userId': decoded['userId']}))
        for req in requests:
            req['_id'] = str(req['_id'])
            req['userId'] = str(req['userId'])
            if req.get('createdAt'):
                req['createdAt'] = req['createdAt'].isoformat()
            if req.get('updatedAt'):
                req['updatedAt'] = req['updatedAt'].isoformat()

        return jsonify({
            'success': True,
            'requests': requests
        }), 200

    except Exception as e:
        print(f"❌ Erreur lors de la récupération des demandes: {e}")
        return jsonify({
            'success': False,
            'message': 'Erreur serveur lors de la récupération',
            'error': str(e)
        }), 500

# Route pour lister tous les utilisateurs (pour debug)
@app.route('/users', methods=['GET'])
def get_users():
    try:
        users = list(users_collection.find({}, {'password': 0}))  # Exclure les mots de passe
        for user in users:
            user['_id'] = str(user['_id'])
            if user.get('createdAt'):
                user['createdAt'] = user['createdAt'].isoformat()
            if user.get('updatedAt'):
                user['updatedAt'] = user['updatedAt'].isoformat()
        
        return jsonify({
            'success': True,
            'users': users,
            'count': len(users)
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Erreur lors de la récupération des utilisateurs',
            'error': str(e)
        }), 500

# Route pour récupérer les informations du profil utilisateur
@app.route('/api/me', methods=['GET'])
def get_profile():
    try:
        # Récupérer le token depuis le header Authorization
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'success': False, 'message': 'Token manquant ou invalide'}), 401
            
        token = auth_header.split(' ')[1]
        payload = verify_token(token)
        
        if not payload:
            return jsonify({'success': False, 'message': 'Token invalide ou expiré'}), 401
        
        # Récupérer l'utilisateur depuis la base de données
        user = users_collection.find_one({
            'employeeId': payload['employeeId']
        }, {'password': 0})  # Exclure le mot de passe
        
        if not user:
            return jsonify({'success': False, 'message': 'Utilisateur non trouvé'}), 404
            
        # Convertir l'ObjectId en string pour le JSON
        user['_id'] = str(user['_id'])
        
        return jsonify({
            'success': True,
            'user': user
        })
        
    except jwt.ExpiredSignatureError:
        return jsonify({'success': False, 'message': 'Session expirée'}), 401
    except Exception as e:
        print(f"Erreur get_profile: {str(e)}")
        return jsonify({'success': False, 'message': 'Erreur serveur'}), 500

# Route pour mettre à jour le profil utilisateur
@app.route('/api/update-profile', methods=['PUT'])
def update_profile():
    try:
        # Vérifier le token
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'success': False, 'message': 'Token manquant ou invalide'}), 401
            
        token = auth_header.split(' ')[1]
        payload = verify_token(token)
        
        if not payload:
            return jsonify({'success': False, 'message': 'Token invalide ou expiré'}), 401
        
        data = request.get_json()
        
        # Validation des données
        required_fields = ['firstName', 'lastName', 'email', 'phoneNumber']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'success': False, 'message': f'Le champ {field} est requis'}), 400
        
        # Validation de l'email
        if not is_valid_email(data['email']):
            return jsonify({'success': False, 'message': 'Format d\'email invalide'}), 400
            
        # Vérifier si l'email existe déjà pour un autre utilisateur
        existing_user = users_collection.find_one({
            'email': data['email'],
            'employeeId': {'$ne': payload['employeeId']}
        })
        
        if existing_user:
            return jsonify({'success': False, 'message': 'Cet email est déjà utilisé'}), 400
        
        # Validation du numéro de téléphone
        if not is_valid_phone(data['phoneNumber']):
            return jsonify({'success': False, 'message': 'Format de numéro de téléphone invalide'}), 400
        
        # Mise à jour des informations de l'utilisateur
        update_data = {
            'firstName': data['firstName'],
            'lastName': data['lastName'],
            'email': data['email'],
            'phoneNumber': data['phoneNumber'],
            'updatedAt': datetime.utcnow()
        }
        
        # Ajouter les champs optionnels s'ils sont présents
        if 'parentalEmail' in data:
            if data['parentalEmail'] and not is_valid_email(data['parentalEmail']):
                return jsonify({'success': False, 'message': 'Format d\'email parental invalide'}), 400
            update_data['parentalEmail'] = data['parentalEmail']
            
        if 'parentalPhoneNumber' in data and data['parentalPhoneNumber']:
            if not is_valid_phone(data['parentalPhoneNumber']):
                return jsonify({'success': False, 'message': 'Format de numéro de téléphone parental invalide'}), 400
            update_data['parentalPhoneNumber'] = data['parentalPhoneNumber']
        
        # Mettre à jour l'utilisateur dans la base de données
        result = users_collection.update_one(
            {'employeeId': payload['employeeId']},
            {'$set': update_data}
        )
        
        if result.matched_count == 0:
            return jsonify({'success': False, 'message': 'Utilisateur non trouvé'}), 404
        
        # Récupérer les données mises à jour
        updated_user = users_collection.find_one(
            {'employeeId': payload['employeeId']},
            {'password': 0}  # Exclure le mot de passe
        )
        
        if updated_user:
            updated_user['_id'] = str(updated_user['_id'])
            
        return jsonify({
            'success': True,
            'message': 'Profil mis à jour avec succès',
            'user': updated_user
        })
        
    except jwt.ExpiredSignatureError:
        return jsonify({'success': False, 'message': 'Session expirée'}), 401
    except Exception as e:
        print(f"Erreur update_profile: {str(e)}")
        return jsonify({'success': False, 'message': 'Erreur serveur'}), 500

if __name__ == '__main__':
    print("🚀 Démarrage du serveur Flask...")
    print(f"📊 Base de données: {MONGODB_URI}")
    print(f"🔑 JWT Secret configuré: {'Oui' if JWT_SECRET_KEY else 'Non'}")
    
    app.run(debug=True, host='0.0.0.0', port=5000)