// frontend/App.js

import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';

import AnalyzeScreen from './screens/AnalyzeScreen';
import MatchScreen from './screens/MatchScreen';

const Tab = createBottomTabNavigator();

export default function App() {
  return (
    <NavigationContainer>
      <Tab.Navigator>
        <Tab.Screen name="분석" component={AnalyzeScreen} />
        <Tab.Screen name="유실견 찾기" component={MatchScreen} />
      </Tab.Navigator>
    </NavigationContainer>
  );
}
