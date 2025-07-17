import React from 'react';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { Ionicons } from '@expo/vector-icons';
import ProfileScreen from './ProfileScreen';
import DocumentRequestScreen from './DocumentRequestScreen';
import DocumentsScreen from './DocumentsScreen';

const Tab = createBottomTabNavigator();

const MainTabNavigator = () => {
  return (
    <Tab.Navigator
      screenOptions={({ route }) => ({
        tabBarIcon: ({ focused, color, size }) => {
          let iconName;

          if (route.name === 'Profile') {
            iconName = focused ? 'person' : 'person-outline';
          } else if (route.name === 'DocumentRequest') {
            iconName = focused ? 'document-text' : 'document-text-outline';
          } else if (route.name === 'Documents') {
            iconName = focused ? 'documents' : 'documents-outline';
          }

          return <Ionicons name={iconName} size={size} color={color} />;
        },
        tabBarActiveTintColor: '#6c5ce7',
        tabBarInactiveTintColor: '#8e8e93',
        tabBarStyle: {
          backgroundColor: '#fff',
          borderTopWidth: 1,
          borderTopColor: '#e1e1e1',
          height: 60,
          paddingBottom: 8,
          paddingTop: 8,
        },
        tabBarLabelStyle: {
          fontSize: 12,
          fontWeight: '600',
        },
        headerStyle: {
          backgroundColor: '#002857',
        },
        headerTintColor: '#fff',
        headerTitleStyle: {
          fontWeight: 'bold',
        },
      })}
    >
      <Tab.Screen 
        name="Profile" 
        component={ProfileScreen}
        options={{
          title: 'Profil',
          headerTitle: 'Mon Profil',
        }}
      />
      <Tab.Screen 
        name="Documents" 
        component={DocumentsScreen}
        options={{
          title: 'Mes Documents',
          headerTitle: 'Mes Documents',
        }}
      />
      <Tab.Screen 
        name="DocumentRequest" 
        component={DocumentRequestScreen}
        options={{
          title: 'Demande de document',
          headerTitle: 'Demande de Document',
        }}
      />
    </Tab.Navigator>
  );
};

export default MainTabNavigator;
