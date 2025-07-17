from pymongo import MongoClient
import bcrypt
from datetime import datetime
import os

# Configuration MongoDB Atlas
MONGODB_URI = 'mongodb+srv://oussamatrzd19:oussama123@leoniapp.grhnzgz.mongodb.net/LeoniApp'

print('=== TEST DE CONNEXION MONGODB ATLAS ===')
try:
    # Connexion à MongoDB Atlas
    client = MongoClient(MONGODB_URI)
    
    # Test de la connexion
    client.server_info()
    print('✅ Connexion à MongoDB Atlas réussie!')
    
    # Accès à la base de données
    db = client['LeoniApp']
    users_collection = db['users']
    
    print(f'✅ Base de données "LeoniApp" accessible')
    
    # Vérifier les utilisateurs existants
    user_count = users_collection.count_documents({})
    print(f'📊 Nombre d\'utilisateurs dans la base: {user_count}')
    
    if user_count > 0:
        print('\n=== UTILISATEURS EXISTANTS ===')
        users = list(users_collection.find({}, {'email': 1, 'firstName': 1, 'lastName': 1, 'employeeId': 1}))
        
        for i, user in enumerate(users, 1):
            print(f'{i}. Email: {user.get("email", "N/A")}')
            print(f'   Nom: {user.get("firstName", "N/A")} {user.get("lastName", "N/A")}')
            print(f'   ID employé: {user.get("employeeId", "N/A")}')
            print()
    else:
        print('\n⚠️  Aucun utilisateur trouvé dans la base de données')
        print('Voulez-vous créer un utilisateur de test? (y/n)')
        create_user = input().strip().lower()
        
        if create_user == 'y':
            # Créer un utilisateur de test
            test_user = {
                'firstName': 'Test',
                'lastName': 'User',
                'email': 'test@leoni.com',
                'parentalEmail': 'parent@leoni.com',
                'phoneNumber': '0123456789',
                'parentalPhoneNumber': '0987654321',
                'password': bcrypt.hashpw('test123'.encode('utf-8'), bcrypt.gensalt()),
                'employeeId': 'EMP001',
                'createdAt': datetime.utcnow(),
                'updatedAt': datetime.utcnow()
            }
            
            result = users_collection.insert_one(test_user)
            print(f'✅ Utilisateur de test créé!')
            print(f'Email: test@leoni.com')
            print(f'Mot de passe: test123')
            print(f'ID: {result.inserted_id}')
    
    # Test de connexion avec un utilisateur existant
    print('\n=== TEST DE CONNEXION UTILISATEUR ===')
    if user_count > 0:
        test_email = input('Entrez votre email pour tester: ').strip().lower()
        test_password = input('Entrez votre mot de passe: ')
        
        user = users_collection.find_one({'email': test_email})
        if user:
            print(f'✅ Utilisateur trouvé: {user.get("firstName")} {user.get("lastName")}')
            
            # Vérifier le mot de passe
            if bcrypt.checkpw(test_password.encode('utf-8'), user['password']):
                print('✅ MOT DE PASSE CORRECT! La connexion devrait fonctionner.')
            else:
                print('❌ MOT DE PASSE INCORRECT!')
                
                # Proposer de réinitialiser le mot de passe
                print('Voulez-vous réinitialiser le mot de passe? (y/n)')
                reset = input().strip().lower()
                if reset == 'y':
                    new_password = input('Nouveau mot de passe: ')
                    hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
                    
                    users_collection.update_one(
                        {'email': test_email},
                        {'$set': {'password': hashed_password, 'updatedAt': datetime.utcnow()}}
                    )
                    print('✅ Mot de passe réinitialisé!')
        else:
            print('❌ Aucun utilisateur trouvé avec cet email!')
            
            # Proposer de créer l'utilisateur
            print('Voulez-vous créer cet utilisateur? (y/n)')
            create = input().strip().lower()
            if create == 'y':
                firstName = input('Prénom: ')
                lastName = input('Nom: ')
                parentalEmail = input('Email parental: ')
                phoneNumber = input('Téléphone: ')
                parentalPhoneNumber = input('Téléphone parental: ')
                
                # Générer un ID employé
                last_user = users_collection.find_one({}, sort=[('employeeId', -1)])
                if last_user and last_user.get('employeeId'):
                    try:
                        last_id = int(last_user['employeeId'].replace('EMP', ''))
                        employee_id = f'EMP{last_id + 1:03d}'
                    except:
                        employee_id = 'EMP002'
                else:
                    employee_id = 'EMP001'
                
                new_user = {
                    'firstName': firstName,
                    'lastName': lastName,
                    'email': test_email,
                    'parentalEmail': parentalEmail,
                    'phoneNumber': phoneNumber,
                    'parentalPhoneNumber': parentalPhoneNumber,
                    'password': bcrypt.hashpw(test_password.encode('utf-8'), bcrypt.gensalt()),
                    'employeeId': employee_id,
                    'createdAt': datetime.utcnow(),
                    'updatedAt': datetime.utcnow()
                }
                
                result = users_collection.insert_one(new_user)
                print(f'✅ Utilisateur créé avec succès!')
                print(f'ID: {result.inserted_id}')
                print(f'Employee ID: {employee_id}')

except Exception as e:
    print(f'❌ Erreur de connexion à MongoDB Atlas: {e}')
    print('\nVérifiez:')
    print('1. Que votre adresse IP est autorisée dans MongoDB Atlas')
    print('2. Que les identifiants sont corrects')
    print('3. Que votre connexion internet fonctionne')
