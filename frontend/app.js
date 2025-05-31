import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { Provider as PaperProvider } from 'react-native-paper';
import { StatusBar } from 'expo-status-bar';
import { Ionicons } from '@expo/vector-icons';

// 화면 컴포넌트들
import HomeScreen from './screens/HomeScreen';
import RegisterScreen from './screens/RegisterScreen';
import FindScreen from './screens/FindScreen';
import MyPetsScreen from './screens/MyPetsScreen';

// 테마 설정 - 코발트 블루 테마
const theme = {
  colors: {
    primary: '#0047AB',
    secondary: '#4A90E2',
    background: '#FFFFFF',
    surface: '#F8F9FA',
    text: '#2C3E50',
    accent: '#6BB6FF',
  },
};

const Tab = createBottomTabNavigator();

export default function App() {
  return (
    <PaperProvider theme={theme}>
      <NavigationContainer>
        <StatusBar style="auto" />
        <Tab.Navigator
          screenOptions={({ route }) => ({
            tabBarIcon: ({ focused, color, size }) => {
              let iconName;

              if (route.name === 'Home') {
                iconName = focused ? 'home' : 'home-outline';
              } else if (route.name === 'Register') {
                iconName = focused ? 'camera' : 'camera-outline';
              } else if (route.name === 'Find') {
                iconName = focused ? 'search' : 'search-outline';
              } else if (route.name === 'MyPets') {
                iconName = focused ? 'heart' : 'heart-outline';
              }

              return <Ionicons name={iconName} size={size} color={color} />;
            },
            tabBarActiveTintColor: '#0047AB',
            tabBarInactiveTintColor: 'gray',
            tabBarStyle: {
              backgroundColor: '#FFFFFF',
              borderTopWidth: 1,
              borderTopColor: '#E0E0E0',
              paddingBottom: 8,
              paddingTop: 8,
              height: 70,
            },
            headerStyle: {
              backgroundColor: '#0047AB',
            },
            headerTintColor: '#FFFFFF',
            headerTitleStyle: {
              fontWeight: 'bold',
            },
          })}
        >
          <Tab.Screen 
            name="Home" 
            component={HomeScreen}
            options={{ 
              title: '홈',
              headerTitle: '🐾 LostPet'
            }}
          />
          <Tab.Screen 
            name="Register" 
            component={RegisterScreen}
            options={{ 
              title: '반려견 등록',
              headerTitle: '반려견 등록하기'
            }}
          />
          <Tab.Screen 
            name="Find" 
            component={FindScreen}
            options={{ 
              title: '유실견 찾기',
              headerTitle: '유실견 찾기'
            }}
          />
          <Tab.Screen 
            name="MyPets" 
            component={MyPetsScreen}
            options={{ 
              title: '내 반려견',
              headerTitle: '내 반려견 관리'
            }}
          />
        </Tab.Navigator>
      </NavigationContainer>
    </PaperProvider>
  );
} 