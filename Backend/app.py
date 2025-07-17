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
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import secrets

app = Flask(__name__)
# Configuration CORS pour développement local
CORS(app, resources={
    r"/login": {
        "origins": ["http://localhost:8085", "http://localhost:8086"],
        "methods": ["POST", "OPTIONS"],
        "allow_headers": ["Content-Type"],
        "supports_credentials": True
    },
    r"/*": {
        "origins": "*",
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["*"]
    }
})

# Middleware pour gérer les requêtes OPTIONS et éviter les doublons headers CORS
@app.after_request
def after_request(response):
    # Supprimer ces headers car ils sont déjà gérés par CORS(app)
    return response

# Charger les variables d'environnement
load_dotenv()
MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb+srv://oussamatrzd19:oussama123@leoniapp.grhnzgz.mongodb.net/LeoniApp')
JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', '123')

# Configuration email pour la réinitialisation de mot de passe
EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', '587'))
EMAIL_USER = os.getenv('EMAIL_USER', 'your-email@gmail.com')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD', 'your-app-password')
EMAIL_FROM = os.getenv('EMAIL_FROM', 'noreply@leoniapp.com')

# Configuration de la connexion MongoDB avec gestion d'erreurs
try:
    client = MongoClient(MONGODB_URI)
    # Tester la connexion
    client.server_info()
    print("✅ Connexion MongoDB réussie")
    
    # Configuration de la base de données
    DATABASE_NAME = os.getenv('DATABASE_NAME', 'LeoniApp')
    USERS_COLLECTION = os.getenv('USERS_COLLECTION', 'users') 
    DOCUMENTS_COLLECTION = os.getenv('DOCUMENTS_COLLECTION', 'document_requests')
    
    db = client[DATABASE_NAME]
    users_collection = db[USERS_COLLECTION]
    document_requests_collection = db[DOCUMENTS_COLLECTION]
    password_reset_collection = db['password_resets']
    
    # Créer les index pour optimiser les requêtes
    users_collection.create_index([("email", 1)], unique=True)
    users_collection.create_index([("parentalEmail", 1)], unique=True)
    users_collection.create_index([("employeeId", 1)], unique=True)
    document_requests_collection.create_index([("userId", 1)])
    document_requests_collection.create_index([("status", 1)])
    password_reset_collection.create_index([("email", 1)])
    password_reset_collection.create_index([("token", 1)], unique=True)
    password_reset_collection.create_index([("expiresAt", 1)], expireAfterSeconds=0)
    
except Exception as e:
    print(f"❌ Erreur de connexion MongoDB: {e}")
    exit(1)

# Validation de l'email
def is_valid_email(email):
    email_regex = r'^[^\s@]+@[^\s@]+\.[^\s@]+$'
    return re.match(email_regex, email) is not None

# Fonction pour envoyer un email
def send_email(to_email, subject, body):
    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_FROM
        msg['To'] = to_email
        msg['Subject'] = subject

        msg.attach(MIMEText(body, 'html'))

        server = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT)
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASSWORD)
        text = msg.as_string()
        server.sendmail(EMAIL_FROM, to_email, text)
        server.quit()

        return True
    except Exception as e:
        print(f"Erreur envoi email: {e}")
        return False

# Générer un token de réinitialisation
def generate_reset_token():
    return secrets.token_urlsafe(32)

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
            'profilePicture': None,  # Ajout du champ photo de profil
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
            '_id': str(result.inserted_id),
            'userId': str(result.inserted_id),  # Keep for backwards compatibility
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
@app.route('/login', methods=['POST', 'OPTIONS'])
def login():
    if request.method == 'OPTIONS':
        response = jsonify({'success': True})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', '*')
        response.headers.add('Access-Control-Allow-Methods', '*')
        return response
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
            '_id': str(user['_id']),
            'userId': str(user['_id']),  # Keep for backwards compatibility
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
            'status': {
                'current': 'en attente',
                'progress': [
                    {'step': 'en attente', 'date': None, 'completed': False},
                    {'step': 'en cours', 'date': None, 'completed': False}, 
                    {'step': 'accepté', 'date': None, 'completed': False},
                    {'step': 'refusé', 'date': None, 'completed': False}
                ]
            },
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

        # Migration des anciens documents avec status en string vers le nouveau format
        document_requests_collection.update_many(
            {'status': {'$type': 'string'}},
            [{'$set': {
                'status': {
                    'current': '$status',
                    'progress': {
                        '$switch': {
                            'branches': [
                                {
                                    'case': {'$eq': ['$status', 'en attente']},
                                    'then': [
                                        {'step': 'en attente', 'date': None, 'completed': True},
                                        {'step': 'en cours', 'date': None, 'completed': False},
                                        {'step': 'accepté', 'date': None, 'completed': False},
                                        {'step': 'refusé', 'date': None, 'completed': False}
                                    ]
                                },
                                {
                                    'case': {'$eq': ['$status', 'en cours']}, 
                                    'then': [
                                        {'step': 'en attente', 'date': None, 'completed': True},
                                        {'step': 'en cours', 'date': None, 'completed': True},
                                        {'step': 'accepté', 'date': None, 'completed': False},
                                        {'step': 'refusé', 'date': None, 'completed': False}
                                    ]
                                },
                                {
                                    'case': {'$eq': ['$status', 'accepté']},
                                    'then': [
                                        {'step': 'en attente', 'date': None, 'completed': True},
                                        {'step': 'en cours', 'date': None, 'completed': True},
                                        {'step': 'accepté', 'date': None, 'completed': True},
                                        {'step': 'refusé', 'date': None, 'completed': False}
                                    ]
                                },
                                {
                                    'case': {'$eq': ['$status', 'refusé']},
                                    'then': [
                                        {'step': 'en attente', 'date': None, 'completed': True},
                                        {'step': 'en cours', 'date': None, 'completed': False},
                                        {'step': 'accepté', 'date': None, 'completed': False},
                                        {'step': 'refusé', 'date': None, 'completed': True}
                                    ]
                                }
                            ]
                        }
                    }
                }
            }}]
        )
        
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

# Route pour récupérer les informations du profil utilisateur connecté
@app.route('/me', methods=['GET', 'OPTIONS'])
def get_current_user():
    if request.method == 'OPTIONS':
        response = jsonify({'success': True})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', '*')
        response.headers.add('Access-Control-Allow-Methods', '*')
        return response

    try:
        # Vérifier le token
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'success': False, 'message': 'Token manquant ou invalide'}), 401

        token = auth_header.split(' ')[1]
        payload = verify_token(token)

        if not payload:
            return jsonify({'success': False, 'message': 'Token invalide ou expiré'}), 401

        # Récupérer l'utilisateur depuis la base de données
        user = users_collection.find_one({
            '_id': ObjectId(payload['userId'])
        }, {'password': 0})  # Exclure le mot de passe

        if not user:
            return jsonify({'success': False, 'message': 'Utilisateur non trouvé'}), 404

        # Convertir l'ObjectId en string pour le JSON
        user['_id'] = str(user['_id'])
        user['id'] = str(user['_id'])  # Ajouter aussi 'id' pour compatibilité

        return jsonify({
            'success': True,
            'user': user
        })

    except jwt.ExpiredSignatureError:
        return jsonify({'success': False, 'message': 'Session expirée'}), 401
    except Exception as e:
        print(f"Erreur get_current_user: {str(e)}")
        return jsonify({'success': False, 'message': 'Erreur serveur'}), 500

# Route pour récupérer les informations du profil utilisateur par ID
@app.route('/users/<user_id>', methods=['GET', 'OPTIONS'])
def get_user_by_id(user_id):
    try:
        # Vérifier le token
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'success': False, 'message': 'Token manquant ou invalide'}), 401
            
        token = auth_header.split(' ')[1]
        payload = verify_token(token)
        
        if not payload:
            return jsonify({'success': False, 'message': 'Token invalide ou expiré'}), 401
        
        # Récupérer l'utilisateur depuis la base de données
        user = users_collection.find_one({
            '_id': ObjectId(user_id)
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
@app.route('/update-profile', methods=['PUT', 'OPTIONS'])
def update_profile():
    if request.method == 'OPTIONS':
        response = jsonify({'success': True})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', '*')
        response.headers.add('Access-Control-Allow-Methods', '*')
        return response

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

# Route pour mettre à jour le statut d'un document
@app.route('/update-document-status', methods=['PUT'])
def update_document_status():
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'success': False, 'message': 'Token manquant ou invalide'}), 401

        token = auth_header.split(" ")[1]
        decoded = verify_token(token)
        if not decoded:
            return jsonify({'success': False, 'message': 'Token invalide ou expiré'}), 401

        data = request.get_json()
        if not data or not all(field in data for field in ['documentId', 'newStatus']):
            return jsonify({'success': False, 'message': 'ID document et nouveau statut requis'}), 400

        # Vérifier que le nouveau statut est valide
        valid_status = ['en attente', 'en cours', 'accepté', 'refusé']
        if data['newStatus'] not in valid_status:
            return jsonify({'success': False, 'message': 'Statut invalide'}), 400

        # Mettre à jour le statut et marquer l'étape comme complétée
        result = document_requests_collection.update_one(
            {'_id': ObjectId(data['documentId'])},
            {'$set': {
                'status.current': data['newStatus'],
                'status.progress.$[elem].completed': True,
                'status.progress.$[elem].date': datetime.utcnow(),
                'updatedAt': datetime.utcnow()
            }},
            array_filters=[{'elem.step': data['newStatus']}]
        )

        if result.matched_count == 0:
            return jsonify({'success': False, 'message': 'Document non trouvé'}), 404
            
        return jsonify({
            'success': True,
            'message': 'Statut mis à jour avec succès'
        }), 200

    except Exception as e:
        print(f"❌ Erreur lors de la mise à jour du statut: {e}")
        return jsonify({
            'success': False,
            'message': 'Erreur serveur lors de la mise à jour',
            'error': str(e)
        }), 500

# Route pour demander la réinitialisation de mot de passe
@app.route('/forgot-password', methods=['POST', 'OPTIONS'])
def forgot_password():
    if request.method == 'OPTIONS':
        response = jsonify({'success': True})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', '*')
        response.headers.add('Access-Control-Allow-Methods', '*')
        return response

    try:
        data = request.get_json()

        if not data or not data.get('email'):
            return jsonify({'success': False, 'message': 'Email requis'}), 400

        email = data['email'].lower().strip()

        if not is_valid_email(email):
            return jsonify({'success': False, 'message': 'Email invalide'}), 400

        # Vérifier si l'utilisateur existe
        user = users_collection.find_one({'email': email})
        if not user:
            # Pour des raisons de sécurité, on ne révèle pas si l'email existe ou non
            return jsonify({
                'success': True,
                'message': 'Si cet email existe, vous recevrez un lien de réinitialisation'
            }), 200

        # Générer un token de réinitialisation
        reset_token = generate_reset_token()
        expires_at = datetime.utcnow() + timedelta(hours=1)  # Expire dans 1 heure

        # Sauvegarder le token dans la base de données
        password_reset_collection.delete_many({'email': email})  # Supprimer les anciens tokens
        password_reset_collection.insert_one({
            'email': email,
            'token': reset_token,
            'expiresAt': expires_at,
            'createdAt': datetime.utcnow()
        })

        # Créer le lien de réinitialisation
        reset_link = f"http://localhost:8085/reset-password?token={reset_token}"

        # Créer le contenu de l'email
        email_subject = "Réinitialisation de votre mot de passe - Leoni App"
        email_body = f"""
        <html>
        <body>
            <h2>Réinitialisation de mot de passe</h2>
            <p>Bonjour {user.get('firstName', '')},</p>
            <p>Vous avez demandé la réinitialisation de votre mot de passe pour votre compte Leoni App.</p>
            <p>Cliquez sur le lien ci-dessous pour réinitialiser votre mot de passe :</p>
            <p><a href="{reset_link}" style="background-color: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Réinitialiser mon mot de passe</a></p>
            <p>Ce lien expire dans 1 heure.</p>
            <p>Si vous n'avez pas demandé cette réinitialisation, ignorez cet email.</p>
            <br>
            <p>Cordialement,<br>L'équipe Leoni App</p>
        </body>
        </html>
        """

        # Envoyer l'email
        if send_email(email, email_subject, email_body):
            print(f"✅ Email de réinitialisation envoyé à: {email}")
        else:
            print(f"❌ Échec envoi email à: {email}")

        return jsonify({
            'success': True,
            'message': 'Si cet email existe, vous recevrez un lien de réinitialisation'
        }), 200

    except Exception as e:
        print(f"❌ Erreur forgot password: {e}")
        return jsonify({
            'success': False,
            'message': 'Erreur serveur'
        }), 500

# Route pour réinitialiser le mot de passe
@app.route('/reset-password', methods=['POST', 'OPTIONS'])
def reset_password():
    if request.method == 'OPTIONS':
        response = jsonify({'success': True})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', '*')
        response.headers.add('Access-Control-Allow-Methods', '*')
        return response

    try:
        data = request.get_json()

        if not data or not data.get('token') or not data.get('newPassword'):
            return jsonify({'success': False, 'message': 'Token et nouveau mot de passe requis'}), 400

        token = data['token']
        new_password = data['newPassword']

        if len(new_password) < 6:
            return jsonify({'success': False, 'message': 'Le mot de passe doit contenir au moins 6 caractères'}), 400

        # Vérifier le token
        reset_request = password_reset_collection.find_one({
            'token': token,
            'expiresAt': {'$gt': datetime.utcnow()}
        })

        if not reset_request:
            return jsonify({'success': False, 'message': 'Token invalide ou expiré'}), 400

        # Mettre à jour le mot de passe
        hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())

        result = users_collection.update_one(
            {'email': reset_request['email']},
            {'$set': {
                'password': hashed_password,
                'updatedAt': datetime.utcnow()
            }}
        )

        if result.matched_count == 0:
            return jsonify({'success': False, 'message': 'Utilisateur non trouvé'}), 404

        # Supprimer le token utilisé
        password_reset_collection.delete_one({'token': token})

        print(f"✅ Mot de passe réinitialisé pour: {reset_request['email']}")

        return jsonify({
            'success': True,
            'message': 'Mot de passe réinitialisé avec succès'
        }), 200

    except Exception as e:
        print(f"❌ Erreur reset password: {e}")
        return jsonify({
            'success': False,
            'message': 'Erreur serveur'
        }), 500

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    try:
        print(f"🚀 Serveur démarré sur le port {port}")
        app.run(debug=True, host='0.0.0.0', port=port, threaded=True)
    except KeyboardInterrupt:
        print("\nArrêt du serveur...")
    except Exception as e:
        print(f"❌ Erreur du serveur: {e}")
