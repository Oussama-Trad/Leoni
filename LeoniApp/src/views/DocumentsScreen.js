// Version complète et corrigée du fichier
import React, { useState, useEffect } from 'react';
import {
  StyleSheet,
  Text,
  View,
  ScrollView,
  RefreshControl,
  ActivityIndicator,
  Alert
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import AsyncStorage from '@react-native-async-storage/async-storage';
import NetworkService from '../services/NetworkService';

const DocumentsScreen = () => {
  const [documents, setDocuments] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [refreshing, setRefreshing] = useState(false);



  const loadDocuments = async () => {
    try {
      setIsLoading(true);
      console.log('🔍 FRONTEND: Chargement des documents...');

      const token = await AsyncStorage.getItem('userToken');
      if (!token) {
        throw new Error('Token non trouvé');
      }

      console.log('🔍 FRONTEND: Token trouvé, appel API...');

      const response = await NetworkService.fetch('/document-requests', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      console.log('🔍 FRONTEND: Réponse reçue, status =', response.status);

      if (!response.ok) {
        const errorText = await response.text();
        console.error('🔍 FRONTEND: Erreur HTTP:', errorText);
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const contentType = response.headers.get('content-type');
      if (!contentType || !contentType.includes('application/json')) {
        const text = await response.text();
        console.error('Expected JSON but got:', text);
        throw new Error('Invalid content type');
      }

      const data = await response.json();
      console.log('🔍 FRONTEND: Données reçues:', data);

      if (data?.success && data?.requests) {
        setDocuments(data.requests);
        console.log('✅ FRONTEND: Documents chargés:', data.requests.length);
      } else if (data?.success && Array.isArray(data)) {
        setDocuments(data);
        console.log('✅ FRONTEND: Documents chargés (array):', data.length);
      } else {
        console.error('Invalid response structure:', data);
        setDocuments([]);
      }
    } catch (error) {
      console.error('❌ FRONTEND: Erreur fetch documents:', error);
      setDocuments([]);
      Alert.alert(
        'Erreur',
        error.message.includes('Network')
          ? 'Problème de connexion. Vérifiez que le serveur est démarré.'
          : 'Impossible de charger les documents.',
        [{ text: 'Réessayer', onPress: loadDocuments }]
      );
    } finally {
      setIsLoading(false);
      setRefreshing(false);
    }
  };

  const onRefresh = () => {
    setRefreshing(true);
    loadDocuments();
  };

  useEffect(() => {
    loadDocuments();
  }, []);

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Ionicons name="documents" size={60} color="#fff" />
        <Text style={styles.headerTitle}>Mes Documents</Text>
      </View>



      <ScrollView
        contentContainerStyle={styles.scrollContainer}
        refreshControl={
          <RefreshControl
            refreshing={refreshing}
            onRefresh={onRefresh}
            colors={['#fff']}
            tintColor="#fff"
          />
        }
      >
        {isLoading && !refreshing ? (
          <ActivityIndicator size="large" color="#fff" />
        ) : documents.map((doc, index) => (
          <View key={index} style={styles.documentCard}>
            <View style={styles.documentHeader}>
              <Text style={styles.documentType}>{doc.type || doc.documentType || 'Document'}</Text>
              <View style={[
                styles.statusBadge,
                {
                  backgroundColor: '#fff',
                  borderColor: '#ddd'
                },
                doc.status?.current === 'en cours' && styles.inProgressStatus,
                doc.status?.current === 'accepté' && styles.acceptedStatus,
                doc.status?.current === 'refusé' && styles.rejectedStatus
              ]}>
                <Text style={[styles.statusText, {color: '#000'}]}>{(doc.status?.current || 'en attente').toUpperCase()}</Text>
              </View>
            </View>

            {doc.description && (
              <Text style={styles.documentDescription}>
                Description: {doc.description}
              </Text>
            )}

            <Text style={styles.documentDate}>
              Envoyé le: {doc.createdAt ? new Date(doc.createdAt).toLocaleDateString() : '---'}
            </Text>
          </View>
        ))}
      </ScrollView>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#002857',
  },
  scrollContainer: {
    paddingBottom: 20,
  },
  header: {
    padding: 20,
    paddingTop: 40,
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
  documentCard: {
    backgroundColor: '#fff',
    borderRadius: 15,
    padding: 15,
    marginHorizontal: 20,
    marginBottom: 15,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  documentHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 10,
  },
  documentType: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#333',
    flex: 1,
  },
  statusBadge: {
    paddingHorizontal: 10,
    paddingVertical: 5,
    borderRadius: 12,
    borderWidth: 1,
    backgroundColor: '#fff',
  },
  inProgressStatus: {
    backgroundColor: '#FFC107',
    borderColor: '#FFA000',
  },
  acceptedStatus: {
    backgroundColor: '#4CAF50',
    borderColor: '#388E3C',
  },
  rejectedStatus: {
    backgroundColor: '#F44336',
    borderColor: '#D32F2F',
  },
  statusText: {
    color: '#fff',
    fontWeight: 'bold',
    fontSize: 12,
  },
  documentDescription: {
    fontSize: 14,
    color: '#444',
    marginVertical: 8,
  },
  documentDate: {
    fontSize: 12,
    color: '#666',
    marginTop: 10,
    fontStyle: 'italic',
  }
}); 

export default DocumentsScreen;
