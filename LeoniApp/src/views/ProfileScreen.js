import React, { useState, useEffect, useRef } from 'react';
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
import { useNavigation } from '@react-navigation/native';
import ProfileController from '../controllers/ProfileController';
import ProfileModel from '../models/ProfileModel';

// Composant réutilisable pour les champs de formulaire
const InputField = ({ 
  icon, 
  placeholder, 
  value, 
  onChangeText, 
  keyboardType = 'default', 
  editable = true 
}) => (
  <View style={styles.inputContainer}>
    <Ionicons name={icon} size={20} color="#666" style={styles.inputIcon} />
    <TextInput
      style={[styles.input, !editable && styles.inputDisabled]}
      placeholder={placeholder}
      placeholderTextColor="#999"
      value={value}
      onChangeText={onChangeText}
      keyboardType={keyboardType}
      editable={editable}
    />
  </View>
);

const ProfileScreen = () => {
  const navigation = useNavigation();
  const [state, setState] = useState({
    firstName: '',
    lastName: '',
    email: '',
    parentalEmail: '',
    phoneNumber: '',
    parentalPhoneNumber: '',
    isEditing: false,
    isLoading: false
  });

  const modelRef = useRef(new ProfileModel());
  const model = modelRef.current;

  // Charger les données du profil au montage
  useEffect(() => {
    loadProfile();
    
    // S'abonner aux changements du modèle
    const handleModelChange = (newState) => {
      setState(prevState => ({ ...prevState, ...newState }));
    };
    
    model.subscribe(handleModelChange);
    
    return () => {
      // Nettoyage
      model.subscribe(null);
    };
  }, []);

  // Charger les données du profil
  const loadProfile = async () => {
    try {
      model.setIsLoading(true);
      const profileData = await ProfileController.fetchUserProfile();
      model.setProfileData(profileData.user);
    } catch (error) {
      Alert.alert('Erreur', error.message || 'Impossible de charger le profil');
    } finally {
      model.setIsLoading(false);
    }
  };

  // Gérer la modification d'un champ
  const handleFieldChange = (field, value) => {
    model.setField(field, value);
  };

  // Basculer le mode édition
  const toggleEdit = () => {
    model.setIsEditing(!state.isEditing);
  };

  // Enregistrer les modifications
  const handleSave = async () => {
    try {
      model.setIsLoading(true);
      const updatedProfile = await ProfileController.updateUserProfile({
        firstName: state.firstName,
        lastName: state.lastName,
        email: state.email,
        parentalEmail: state.parentalEmail,
        phoneNumber: state.phoneNumber,
        parentalPhoneNumber: state.parentalPhoneNumber
      });
      
      model.setProfileData(updatedProfile.user);
      model.setIsEditing(false);
      Alert.alert('Succès', 'Votre profil a été mis à jour avec succès');
    } catch (error) {
      Alert.alert('Erreur', error.message || 'Erreur lors de la mise à jour du profil');
    } finally {
      model.setIsLoading(false);
    }
  };

  // Gérer la déconnexion
  const handleLogout = async () => {
    try {
      await ProfileController.logout(navigation);
    } catch (error) {
      Alert.alert('Erreur', 'Impossible de se déconnecter');
    }
  };

  // Afficher le chargement
  if (state.isLoading && !state.isEditing) {
    return (
      <View style={[styles.container, styles.loadingContainer]}>
        <ActivityIndicator size="large" color="#6c5ce7" />
      </View>
    );
  }

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
          <View style={styles.avatarContainer}>
            <Ionicons name="person-circle" size={80} color="#fff" />
          </View>
          <Text style={styles.headerTitle}>
            {state.firstName} {state.lastName}
          </Text>
          <Text style={styles.headerSubtitle}>{state.email}</Text>
        </View>

        <View style={styles.formContainer}>
          <Text style={styles.sectionTitle}>Informations personnelles</Text>
          
          <InputField
            icon="person-outline"
            placeholder="Prénom *"
            value={state.firstName}
            onChangeText={(text) => handleFieldChange('firstName', text)}
            editable={state.isEditing}
          />
          
          <InputField
            icon="person-outline"
            placeholder="Nom *"
            value={state.lastName}
            onChangeText={(text) => handleFieldChange('lastName', text)}
            editable={state.isEditing}
          />
          
          <InputField
            icon="mail-outline"
            placeholder="Email *"
            value={state.email}
            keyboardType="email-address"
            autoCapitalize="none"
            onChangeText={(text) => handleFieldChange('email', text)}
            editable={state.isEditing}
          />
          
          <InputField
            icon="call-outline"
            placeholder="Téléphone *"
            value={state.phoneNumber}
            keyboardType="phone-pad"
            onChangeText={(text) => handleFieldChange('phoneNumber', text)}
            editable={state.isEditing}
          />
          
          <Text style={[styles.sectionTitle, { marginTop: 20 }]}>Contact d'urgence</Text>
          
          <InputField
            icon="mail-outline"
            placeholder="Email parental"
            value={state.parentalEmail}
            keyboardType="email-address"
            autoCapitalize="none"
            onChangeText={(text) => handleFieldChange('parentalEmail', text)}
            editable={state.isEditing}
          />
          
          <InputField
            icon="call-outline"
            placeholder="Téléphone parental"
            value={state.parentalPhoneNumber}
            keyboardType="phone-pad"
            onChangeText={(text) => handleFieldChange('parentalPhoneNumber', text)}
            editable={state.isEditing}
          />

          {state.isEditing ? (
            <View style={styles.buttonContainer}>
              <TouchableOpacity 
                style={[styles.button, styles.saveButton]} 
                onPress={handleSave}
                disabled={state.isLoading}
              >
                {state.isLoading ? (
                  <ActivityIndicator color="#fff" />
                ) : (
                  <Text style={styles.buttonText}>Enregistrer les modifications</Text>
                )}
              </TouchableOpacity>
              
              <TouchableOpacity 
                style={[styles.button, styles.cancelButton]} 
                onPress={toggleEdit}
                disabled={state.isLoading}
              >
                <Text style={[styles.buttonText, {color: '#6c5ce7'}]}>Annuler</Text>
              </TouchableOpacity>
            </View>
          ) : (
            <View style={styles.buttonContainer}>
              <TouchableOpacity 
                style={[styles.button, styles.editButton]} 
                onPress={toggleEdit}
              >
                <Text style={styles.buttonText}>Modifier le profil</Text>
              </TouchableOpacity>
              
              <TouchableOpacity 
                style={[styles.button, styles.logoutButton]} 
                onPress={handleLogout}
              >
                <Ionicons name="log-out-outline" size={20} color="#fff" style={styles.buttonIcon} />
                <Text style={styles.buttonText}>Déconnexion</Text>
              </TouchableOpacity>
            </View>
          )}
          
          <Text style={styles.requiredText}>* Champs obligatoires</Text>
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
  loadingContainer: {
    justifyContent: 'center',
    alignItems: 'center',
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
  avatarContainer: {
    width: 100,
    height: 100,
    borderRadius: 50,
    backgroundColor: 'rgba(255, 255, 255, 0.1)',
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 15,
  },
  headerTitle: {
    fontSize: 22,
    fontWeight: 'bold',
    color: '#fff',
    marginBottom: 5,
  },
  headerSubtitle: {
    fontSize: 14,
    color: 'rgba(255, 255, 255, 0.8)',
    marginBottom: 10,
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
    alignItems: 'center',
    backgroundColor: '#fff',
    borderRadius: 15,
    marginBottom: 15,
    paddingHorizontal: 15,
    height: 55,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  inputIcon: {
    marginRight: 10,
    color: '#6c5ce7',
  },
  input: {
    flex: 1,
    height: '100%',
    color: '#333',
    fontSize: 15,
    fontFamily: Platform.OS === 'ios' ? 'System' : 'Roboto',
  },
  inputDisabled: {
    color: '#666',
    opacity: 0.9,
  },
  buttonContainer: {
    marginTop: 20,
  },
  button: {
    height: 55,
    borderRadius: 15,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 15,
    flexDirection: 'row',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.2,
    shadowRadius: 3,
    elevation: 3,
  },
  editButton: {
    backgroundColor: '#6c5ce7',
  },
  saveButton: {
    backgroundColor: '#6c5ce7',
  },
  cancelButton: {
    backgroundColor: '#fff',
    borderWidth: 1,
    borderColor: '#6c5ce7',
  },
  logoutButton: {
    backgroundColor: '#ff4757',
  },
  buttonText: {
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
    marginTop: 10,
  },
});

export default ProfileScreen;
