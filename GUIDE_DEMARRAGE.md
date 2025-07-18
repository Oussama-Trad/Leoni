# Guide de Démarrage - Leoni App

## Problème : Erreur 500 / Network Request Failed

Si vous voyez ces erreurs dans l'application :
- `HTTP error! status: 500`
- `Network request failed`
- `Serveur indisponible`

**Cause :** Le serveur backend Flask n'est pas en cours d'exécution.

## Solution : Démarrer le serveur backend

### 1. Ouvrir un terminal
- Appuyez sur `Ctrl + Shift + ù` dans VS Code
- Ou utilisez le terminal Windows (PowerShell)

### 2. Naviguer vers le dossier Backend
```bash
cd C:\Users\YOOSURF\Leoni\Backend
```

### 3. Démarrer le serveur
```bash
python app.py
```

### 4. Vérifier que le serveur fonctionne
Vous devriez voir :
```
✅ Connexion MongoDB réussie
🚀 Serveur démarré sur le port 5000
* Running on http://127.0.0.1:5000
* Running on http://192.168.1.16:5000
```

### 5. Tester la connexion
Ouvrez votre navigateur et allez sur : http://localhost:5000/health

Vous devriez voir :
```json
{
  "success": true,
  "message": "Serveur en ligne",
  "mongodb": "Connecté"
}
```

## Utilisation de l'application

Une fois le serveur démarré :
1. **Rechargez l'application frontend** (appuyez sur `r` dans le terminal Expo)
2. **Connectez-vous** avec vos identifiants
3. **L'application devrait maintenant fonctionner normalement**

## Mode hors ligne

L'application peut maintenant fonctionner partiellement en mode hors ligne :
- ✅ Affichage des données utilisateur locales
- ✅ Navigation dans l'interface
- ❌ Connexion/inscription
- ❌ Soumission de nouvelles demandes
- ❌ Synchronisation des données

## Dépannage

### Le serveur ne démarre pas
1. Vérifiez que Python est installé : `python --version`
2. Vérifiez que les dépendances sont installées : `pip install -r requirements.txt`
3. Vérifiez que MongoDB est accessible

### L'application ne se connecte toujours pas
1. Vérifiez que le serveur est bien sur le port 5000
2. Vérifiez la configuration dans `LeoniApp/src/config.js`
3. Redémarrez l'application Expo

### Erreurs de CORS
Le serveur est configuré pour accepter toutes les origines en développement.
Si vous avez des erreurs CORS, vérifiez la configuration dans `Backend/app.py`.

## Commandes utiles

### Démarrer le backend
```bash
cd Backend
python app.py
```

### Démarrer le frontend
```bash
cd LeoniApp
npx expo start
```

### Vérifier la santé du serveur
```bash
curl http://localhost:5000/health
```

---

**Note :** Gardez toujours le terminal du serveur backend ouvert pendant que vous utilisez l'application !
