// frontend/screens/AnalyzeScreen.js

import React, { useState } from 'react';
import { View, Button, Image, Text, ActivityIndicator, ScrollView, StyleSheet } from 'react-native';
import * as ImagePicker from 'expo-image-picker';
import { analyzeDog } from '../utils/api';

export default function AnalyzeScreen() {
  const [imageUri, setImageUri] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const pickImage = async () => {
    const result = await ImagePicker.launchImageLibraryAsync({ mediaTypes: ImagePicker.MediaTypeOptions.Images });
    if (!result.canceled) {
      setImageUri(result.assets[0].uri);
    }
  };

  const analyze = async () => {
    if (!imageUri) return;
    setLoading(true);
    const data = await analyzeDog(imageUri);
    setResult(data);
    setLoading(false);
  };

  return (
    <ScrollView contentContainerStyle={styles.container}>
      <Button title="사진 선택" onPress={pickImage} />
      {imageUri && <Image source={{ uri: imageUri }} style={styles.image} />}
      <Button title="분석 요청" onPress={analyze} disabled={!imageUri || loading} />
      {loading && <ActivityIndicator size="large" color="blue" />}
      {result && (
        <View style={styles.result}>
          <Text style={styles.title}>분석 결과</Text>
          <Text>종: {result.species}</Text>
          <Text>코 특징: {result.nose_features.join(', ')}</Text>
          <Image source={{ uri: result.dog_img_url }} style={styles.subImage} />
          <Image source={{ uri: result.nose_img_url }} style={styles.subImageSmall} />
        </View>
      )}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    padding: 20,
    alignItems: 'center',
  },
  image: {
    width: 300,
    height: 300,
    marginVertical: 10,
    borderRadius: 10,
  },
  result: {
    marginTop: 20,
    alignItems: 'center',
  },
  title: {
    fontSize: 20,
    fontWeight: 'bold',
    marginBottom: 10,
  },
  subImage: {
    width: 200,
    height: 200,
    marginTop: 10,
    borderRadius: 10,
  },
  subImageSmall: {
    width: 100,
    height: 100,
    marginTop: 10,
    borderRadius: 10,
  },
});
    