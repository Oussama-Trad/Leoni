# Diagnostic - Problème d'affichage du profil

## Problème identifié

L'interface affiche "Non renseigné" pour des champs qui ont pourtant des valeurs dans la base de données :

**Données en base :**
```json
{
  "_id": "687a304c63118d709d344a4f",
  "firstName": "a",
  "lastName": "a",
  "email": "a@gmail.com",
  "parentalEmail": "aa@gmail.com",
  "phoneNumber": "12345678",
  "parentalPhoneNumber": "12345899",
  "department": "Non spécifié",
  "position": "Non spécifié",
  "address": ""
}
```

**Affiché dans l'interface :** "Non renseigné"

## Causes possibles

1. **Serveur backend non démarré** - Les données ne sont pas récupérées
2. **Problème de récupération API** - L'appel à `/me` échoue
3. **Données locales corrompues** - Les données stockées localement sont incorrectes
4. **Problème de mapping** - Les champs ne sont pas correctement mappés

## Solutions ajoutées

### 1. Logs détaillés
- ✅ Logs de récupération des données serveur
- ✅ Logs des données locales
- ✅ Affichage détaillé de tous les champs

### 2. Boutons de diagnostic
- ✅ **Bouton "Recharger"** - Force le rechargement depuis le serveur
- ✅ **Bouton "Debug"** - Affiche les données locales stockées

### 3. Champs ajoutés
- ✅ Département (affiché et modifiable)
- ✅ Poste (affiché et modifiable)  
- ✅ Adresse (affiché et modifiable)
- ✅ Email parental (affiché)
- ✅ Téléphone parental (affiché)

## Comment diagnostiquer

### Étape 1 : Vérifier les logs
Ouvrez la console et regardez les logs :
```
🔍 PROFILE: Chargement du profil...
🔍 PROFILE: Réponse reçue: {...}
🔍 PROFILE: Données utilisateur reçues: {...}
```

### Étape 2 : Utiliser le bouton Debug
1. Cliquez sur le bouton **"Debug"** (jaune)
2. Regardez les données affichées dans l'alerte
3. Comparez avec les données de votre base

### Étape 3 : Utiliser le bouton Recharger
1. Cliquez sur le bouton **"Recharger"** (vert)
2. Regardez les logs dans la console
3. Vérifiez si les données sont mises à jour

### Étape 4 : Vérifier le serveur
Si les boutons ne fonctionnent pas :
1. Vérifiez que le serveur backend est démarré
2. Testez l'URL : http://localhost:5000/me
3. Vérifiez les logs du serveur

## Résultats attendus

Après diagnostic, vous devriez voir :

### Si le serveur fonctionne :
```
🔍 PROFILE: Données utilisateur reçues: {
  firstName: "a",
  lastName: "a", 
  email: "a@gmail.com",
  phoneNumber: "12345678",
  parentalEmail: "aa@gmail.com",
  parentalPhoneNumber: "12345899",
  department: "Non spécifié",
  position: "Non spécifié"
}
```

### Si le serveur ne fonctionne pas :
```
❌ PROFILE: Erreur lors du chargement du profil
🔍 PROFILE: Chargement des données locales...
```

## Actions à prendre

### Si les données sont récupérées mais mal affichées :
- Problème de rendu React
- Vérifier les conditions d'affichage

### Si les données ne sont pas récupérées :
- Démarrer le serveur backend : `python app.py`
- Vérifier la connexion réseau

### Si les données locales sont incorrectes :
- Se reconnecter pour rafraîchir les données
- Vider le cache de l'application

## Test final

Une fois le diagnostic fait :
1. **Toutes les données** devraient s'afficher correctement
2. **Les champs modifiables** devraient être pré-remplis
3. **La modification** devrait fonctionner sans erreur
