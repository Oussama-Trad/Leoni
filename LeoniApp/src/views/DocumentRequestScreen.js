import React, { useState, useEffect } from 'react';
import {
  StyleSheet,
  Text,
  View,
  TextInput,
  TouchableOpacity,
  ScrollView,
  KeyboardAvoidingView,
  Platform,
  ActivityIndicator,
  Alert
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { BASE_URL } from '../config';

const DocumentRequestScreen = () => {
  const [documentType, setDocumentType] = useState('');
  const [description, setDescription] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [requests, setRequests] = useState([]);

  // Types de documents prédéfinis
  const documentTypes = [
    'Certificat de travail',
    'Attestation de salaire',
    'Relevé de compte',
    'Certificat médical',
    'Attestation de formation',
    'Autre'
  ];

  const [showDropdown, setShowDropdown] = useState(false);

  // Charger les demandes existantes
  const loadRequests = async () => {
    try {
      const userData = await AsyncStorage.getItem('userData');
      const token = await AsyncStorage.getItem('userToken');

      if (!userData || !token) {
        console.log('Données utilisateur ou token manquants');
        return;
      }

      const user = JSON.parse(userData);
      console.log('Chargement des demandes pour:', user.email);

      const response = await fetch(`${BASE_URL}/document-requests`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      console.log('Réponse demandes:', data);

      if (data.success) {
        setRequests(data.requests || []);
      } else {
        console.error('Erreur API:', data.message);
      }
    } catch (error) {
      console.error('Erreur chargement demandes:', error);
      // Ne pas faire planter l'app, juste logger l'erreur
      setRequests([]);
    }
  };

  useEffect(() => {
    const initializeScreen = async () => {
      try {
        await loadRequests();
      } catch (error) {
        console.error('Erreur initialisation écran:', error);
      }
    };

    initializeScreen();
  }, []);

  const handleSubmit = async () => {
    if (!documentType.trim()) {
      Alert.alert('Erreur', 'Veuillez sélectionner un type de document');
      return;
    }

    try {
      setIsLoading(true);

      // Récupérer les données utilisateur depuis AsyncStorage
      const userData = await AsyncStorage.getItem('userData');
      if (!userData) {
        Alert.alert('Erreur', 'Utilisateur non connecté');
        return;
      }

      const user = JSON.parse(userData);
      console.log('Données utilisateur:', user);

      const userId = user.id || user._id || user.userId;
      if (!userId) {
        Alert.alert('Erreur', 'ID utilisateur manquant');
        return;
      }

      const requestData = {
        userId: userId,
        documentType: documentType.trim(),
        description: description.trim()
      };

      const response = await fetch(`${BASE_URL}/document-request`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestData),
      });

      const data = await response.json();

      if (data.success) {
        Alert.alert('Succès', 'Demande envoyée avec succès');
        // Réinitialiser et recharger
        setDocumentType('');
        setDescription('');
        await loadRequests();
      } else {
        Alert.alert('Erreur', data.message || 'Erreur lors de l\'envoi de la demande');
      }
    } catch (error) {
      console.error('Erreur:', error);
      Alert.alert('Erreur', 'Impossible de se connecter au serveur');
    } finally {
      setIsLoading(false);
    }
  };

  const selectDocumentType = (type) => {
    setDocumentType(type);
    setShowDropdown(false);
  };

  return (
    <KeyboardAvoidingView 
      style={styles.container}
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
      keyboardVerticalOffset={Platform.OS === 'ios' ? 64 : 0}
    >
      <ScrollView 
        contentContainerStyle={styles.scrollContainer}
        keyboardShouldPersistTaps="handled"
      >
        <View style={styles.header}>
          <Ionicons name="document-text" size={60} color="#fff" />
          <Text style={styles.headerTitle}>Demande de Document</Text>
          <Text style={styles.headerSubtitle}>
            Remplissez le formulaire ci-dessous pour faire votre demande
          </Text>
        </View>

        <View style={styles.formContainer}>
          <Text style={styles.sectionTitle}>Informations de la demande</Text>
          
          {/* Type de document */}
          <View style={styles.inputContainer}>
            <Ionicons name="folder-outline" size={20} color="#6c5ce7" style={styles.inputIcon} />
            <TouchableOpacity 
              style={styles.dropdownButton}
              onPress={() => setShowDropdown(!showDropdown)}
            >
              <Text style={[styles.dropdownText, !documentType && styles.placeholderText]}>
                {documentType || 'Sélectionner un type de document *'}
              </Text>
              <Ionicons 
                name={showDropdown ? "chevron-up" : "chevron-down"} 
                size={20} 
                color="#666" 
              />
            </TouchableOpacity>
          </View>

          {/* Dropdown des types de documents */}
          {showDropdown && (
            <View style={styles.dropdown}>
              {documentTypes.map((type, index) => (
                <TouchableOpacity
                  key={index}
                  style={styles.dropdownItem}
                  onPress={() => selectDocumentType(type)}
                >
                  <Text style={styles.dropdownItemText}>{type}</Text>
                </TouchableOpacity>
              ))}
            </View>
          )}

          {/* Description */}
          <View style={styles.inputContainer}>
            <Ionicons name="create-outline" size={20} color="#6c5ce7" style={styles.inputIcon} />
            <TextInput
              style={[styles.input, styles.textArea]}
              placeholder="Description (facultatif)"
              placeholderTextColor="#999"
              value={description}
              onChangeText={setDescription}
              multiline={true}
              numberOfLines={4}
              textAlignVertical="top"
            />
          </View>

          {/* Bouton d'envoi */}
          <TouchableOpacity 
            style={[styles.submitButton, isLoading && styles.disabledButton]} 
            onPress={handleSubmit}
            disabled={isLoading}
          >
            {isLoading ? (
              <ActivityIndicator color="#fff" />
            ) : (
              <>
                <Ionicons name="send" size={20} color="#fff" style={styles.buttonIcon} />
                <Text style={styles.submitButtonText}>Envoyer la demande</Text>
              </>
            )}
          </TouchableOpacity>

          <Text style={styles.requiredText}>* Champs obligatoires</Text>

          {/* Liste des demandes */}
          {requests.map((req, index) => (
              <View key={index} style={styles.requestCard}>
                <View style={styles.requestHeader}>
                  <Text style={styles.requestType}>{req.documentType}</Text>
                  <View style={[
                    styles.statusBadge,
                    (req.status?.current || req.status) === 'en attente' && styles.pendingBadge,
                    (req.status?.current || req.status) === 'en cours' && styles.inProgressBadge,
                    (req.status?.current || req.status) === 'confirmé' && styles.confirmedBadge,
                    (req.status?.current || req.status) === 'delivré' && styles.deliveredBadge
                  ]}>
                    <Text style={styles.statusText}>{req.status?.current || req.status || 'en attente'}</Text>
                  </View>
                </View>
                {req.description ? (
                  <Text style={styles.requestDescription}>{req.description}</Text>
                ) : null}
                <Text style={styles.requestDate}>
                  {new Date(req.createdAt).toLocaleDateString()}
                </Text>
              </View>
            ))}
        </View>
      </ScrollView>
    </KeyboardAvoidingView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#002857',
  },
  scrollContainer: {
    flexGrow: 1,
    paddingBottom: 30,
  },
  header: {
    padding: 20,
    paddingTop: 30,
    alignItems: 'center',
    backgroundColor: 'rgba(0, 40, 87, 0.8)',
    borderBottomLeftRadius: 30,
    borderBottomRightRadius: 30,
    marginBottom: 20,
  },
  headerTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#fff',
    marginTop: 15,
    marginBottom: 10,
  },
  headerSubtitle: {
    fontSize: 14,
    color: 'rgba(255, 255, 255, 0.8)',
    textAlign: 'center',
    lineHeight: 20,
  },
  formContainer: {
    paddingHorizontal: 20,
    marginTop: 10,
  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#fff',
    marginBottom: 15,
    marginTop: 10,
  },
  inputContainer: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    backgroundColor: '#fff',
    borderRadius: 15,
    marginBottom: 15,
    paddingHorizontal: 15,
    minHeight: 55,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  inputIcon: {
    marginRight: 10,
    marginTop: 17,
  },
  input: {
    flex: 1,
    height: 55,
    color: '#333',
    fontSize: 15,
    fontFamily: Platform.OS === 'ios' ? 'System' : 'Roboto',
  },
  textArea: {
    height: 100,
    paddingTop: 15,
    paddingBottom: 15,
  },
  dropdownButton: {
    flex: 1,
    height: 55,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
  },
  dropdownText: {
    color: '#333',
    fontSize: 15,
    fontFamily: Platform.OS === 'ios' ? 'System' : 'Roboto',
  },
  placeholderText: {
    color: '#999',
  },
  dropdown: {
    backgroundColor: '#fff',
    borderRadius: 15,
    marginBottom: 15,
    marginTop: -10,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  dropdownItem: {
    paddingHorizontal: 15,
    paddingVertical: 15,
    borderBottomWidth: 1,
    borderBottomColor: '#f0f0f0',
  },
  dropdownItemText: {
    color: '#333',
    fontSize: 15,
    fontFamily: Platform.OS === 'ios' ? 'System' : 'Roboto',
  },
  submitButton: {
    height: 55,
    backgroundColor: '#6c5ce7',
    borderRadius: 15,
    justifyContent: 'center',
    alignItems: 'center',
    marginTop: 20,
    flexDirection: 'row',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.2,
    shadowRadius: 3,
    elevation: 3,
  },
  disabledButton: {
    opacity: 0.6,
  },
  submitButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
  },
  buttonIcon: {
    marginRight: 10,
  },
  requiredText: {
    color: 'rgba(255, 255, 255, 0.6)',
    fontSize: 12,
    textAlign: 'center',
    marginTop: 15,
  },
});

export default DocumentRequestScreen;
