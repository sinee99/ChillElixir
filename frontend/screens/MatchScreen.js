// frontend/screens/MatchScreen.js

import React, { useState } from 'react';
import { View, Button, Image, Text, FlatList, ActivityIndicator, StyleSheet } from 'react-native';
import * as ImagePicker from 'expo-image-picker';
import { matchDog } from '../utils/api';

export default function MatchScreen() {
  const [imageUri, setImageUri] = useState(null);
  const [matches, setMatches] = useState([]);
  const [loading, setLoading] = useState(false);

  const pickImage = async () => {
    const result = await ImagePicker.launchImageLibraryAsync();
    if (!result.canceled) {
      setImageUri(result.assets[0].uri);
      setMatches([]);
    }
  };

  const match = async () => {
    if (!imageUri) return;
    setLoading(true);
    const data = await matchDog(imageUri);
    setMatches(data.matches || []);
    setLoading(false);
  };

  return (
    <View style={styles.container}>
      <Button title="코 사진 선택" onPress={pickImage} />
      {imageUri && <Image source={{ uri: imageUri }} style={styles.image} />}
      <Button title="유실견 찾기" onPress={match} disabled={!imageUri || loading} />
      {loading && <ActivityIndicator size="large" color="green" />}
      <Text style={styles.title}>유사한 등록 개체 UID</Text>
      <FlatList
        data={matches}
        keyExtractor={(item) => item}
        renderItem={({ item }) => <Text style={styles.result}>• {item}</Text>}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    padding: 20,
  },
  image: {
    width: 300,
    height: 300,
    marginVertical: 10,
    borderRadius: 10,
  },
  title: {
    fontWeight: 'bold',
    marginTop: 20,
  },
  result: {
    paddingVertical: 5,
    fontSize: 16,
  },
});
