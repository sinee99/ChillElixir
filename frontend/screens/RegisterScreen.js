import React, { useState } from 'react';
import {
  View,
  ScrollView,
  StyleSheet,
  Image,
  Alert,
  TouchableOpacity,
} from 'react-native';
import {
  Card,
  Title,
  Paragraph,
  Button,
  ActivityIndicator,
  Text,
  Surface,
} from 'react-native-paper';
import * as ImagePicker from 'expo-image-picker';
import { Ionicons } from '@expo/vector-icons';
import { LinearGradient } from 'expo-linear-gradient';

const API_BASE_URL = 'http://192.168.0.5:8000'; // 실제 서버 IP로 변경 필요

export default function RegisterScreen() {
  const [selectedImage, setSelectedImage] = useState(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisResult, setAnalysisResult] = useState(null);

  const requestPermissions = async () => {
    const { status } = await ImagePicker.requestMediaLibraryPermissionsAsync();
    if (status !== 'granted') {
      Alert.alert('권한 필요', '사진을 선택하려면 갤러리 접근 권한이 필요합니다.');
      return false;
    }
    return true;
  };

  const requestCameraPermissions = async () => {
    const { status } = await ImagePicker.requestCameraPermissionsAsync();
    if (status !== 'granted') {
      Alert.alert('권한 필요', '사진을 촬영하려면 카메라 접근 권한이 필요합니다.');
      return false;
    }
    return true;
  };

  const takePhoto = async () => {
    const hasPermission = await requestCameraPermissions();
    if (!hasPermission) return;

    const result = await ImagePicker.launchCameraAsync({
      mediaTypes: ImagePicker.MediaTypeOptions.Images,
      allowsEditing: true,
      aspect: [1, 1],
      quality: 0.8,
    });

    if (!result.canceled) {
      setSelectedImage(result.assets[0].uri);
      setAnalysisResult(null);
    }
  };

  const pickImage = async () => {
    const hasPermission = await requestPermissions();
    if (!hasPermission) return;

    const result = await ImagePicker.launchImageLibraryAsync({
      mediaTypes: ImagePicker.MediaTypeOptions.Images,
      allowsEditing: true,
      aspect: [1, 1],
      quality: 0.8,
    });

    if (!result.canceled) {
      setSelectedImage(result.assets[0].uri);
      setAnalysisResult(null);
    }
  };

  const analyzeImage = async () => {
    if (!selectedImage) {
      Alert.alert('오류', '먼저 사진을 선택해주세요.');
      return;
    }

    setIsAnalyzing(true);
    
    try {
      const formData = new FormData();
      formData.append('file', {
        uri: selectedImage,
        type: 'image/jpeg',
        name: 'dog_photo.jpg',
      });

      const response = await fetch(`${API_BASE_URL}/analyze`, {
        method: 'POST',
        body: formData,
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      const result = await response.json();
      
      if (result.error) {
        Alert.alert('분석 오류', result.error);
      } else {
        setAnalysisResult(result);
        Alert.alert('성공!', '반려견이 성공적으로 등록되었습니다.');
      }
    } catch (error) {
      console.error('Analysis error:', error);
      Alert.alert('오류', '분석 중 오류가 발생했습니다. 네트워크 연결을 확인해주세요.');
    } finally {
      setIsAnalyzing(false);
    }
  };

  const PhotoPickerCard = ({ title, subtitle, icon, onPress, gradient }) => (
    <TouchableOpacity onPress={onPress} style={styles.photoCard}>
      <LinearGradient
        colors={gradient}
        style={styles.photoGradient}
        start={{ x: 0, y: 0 }}
        end={{ x: 1, y: 1 }}
      >
        <View style={styles.photoCardContent}>
          <Ionicons name={icon} size={40} color="white" />
          <Text style={styles.photoCardTitle}>{title}</Text>
          <Text style={styles.photoCardSubtitle}>{subtitle}</Text>
        </View>
      </LinearGradient>
    </TouchableOpacity>
  );

  return (
    <ScrollView style={styles.container} showsVerticalScrollIndicator={false}>
      {/* 안내 카드 */}
      <Card style={styles.infoCard}>
        <Card.Content>
          <Title style={styles.infoTitle}>반려견 등록 안내</Title>
          <Paragraph style={styles.infoText}>
            • 강아지가 선명하게 보이는 사진을 선택해주세요{'\n'}
            • 한 장의 사진에 강아지 1마리만 포함되어야 합니다{'\n'}
            • AI가 자동으로 견종과 코 특징을 분석합니다
          </Paragraph>
        </Card.Content>
      </Card>

      {/* 사진 선택 */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>사진 선택</Text>
        <View style={styles.photoOptions}>
          <PhotoPickerCard
            title="카메라"
            subtitle="직접 촬영하기"
            icon="camera"
            gradient={['#0047AB', '#4A90E2']}
            onPress={takePhoto}
          />
          <PhotoPickerCard
            title="갤러리"
            subtitle="사진 선택하기"
            icon="images"
            gradient={['#6BB6FF', '#4A90E2']}
            onPress={pickImage}
          />
        </View>
      </View>

      {/* 선택된 사진 미리보기 */}
      {selectedImage && (
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>선택된 사진</Text>
          <Surface style={styles.imagePreview}>
            <Image source={{ uri: selectedImage }} style={styles.previewImage} />
          </Surface>
          
          <Button
            mode="contained"
            onPress={analyzeImage}
            loading={isAnalyzing}
            disabled={isAnalyzing}
            style={styles.analyzeButton}
            buttonColor="#0047AB"
          >
            {isAnalyzing ? 'AI 분석 중...' : 'AI 분석 시작'}
          </Button>
        </View>
      )}

      {/* 분석 결과 */}
      {analysisResult && (
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>분석 결과</Text>
          
          <Card style={styles.resultCard}>
            <Card.Content>
              <View style={styles.resultHeader}>
                <Ionicons name="checkmark-circle" size={24} color="#4CAF50" />
                <Title style={styles.resultTitle}>분석 완료!</Title>
              </View>
              
              <View style={styles.resultItem}>
                <Text style={styles.resultLabel}>견종:</Text>
                <Text style={styles.resultValue}>{analysisResult.species}</Text>
              </View>
              
              <View style={styles.resultItem}>
                <Text style={styles.resultLabel}>등록 ID:</Text>
                <Text style={styles.resultValue}>{analysisResult.uid}</Text>
              </View>
              
              <Text style={styles.resultNote}>
                반려견이 성공적으로 등록되었습니다. 이제 유실견 찾기 기능을 이용할 수 있습니다.
              </Text>
            </Card.Content>
          </Card>

          {/* 분석된 이미지들 */}
          <Card style={styles.imageCard}>
            <Card.Content>
              <Title style={styles.imageCardTitle}>분석된 이미지</Title>
              <View style={styles.analyzedImages}>
                <View style={styles.analyzedImageContainer}>
                  <Text style={styles.imageLabel}>강아지 전체</Text>
                  <Image 
                    source={{ uri: analysisResult.dog_img_url }} 
                    style={styles.analyzedImage} 
                  />
                </View>
                <View style={styles.analyzedImageContainer}>
                  <Text style={styles.imageLabel}>코 부분</Text>
                  <Image 
                    source={{ uri: analysisResult.nose_img_url }} 
                    style={styles.analyzedImage} 
                  />
                </View>
              </View>
            </Card.Content>
          </Card>
        </View>
      )}

      <View style={styles.bottomSpacing} />
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F8F9FA',
  },
  infoCard: {
    margin: 16,
    borderRadius: 12,
    elevation: 2,
  },
  infoTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#2C3E50',
    marginBottom: 8,
  },
  infoText: {
    fontSize: 14,
    color: '#7F8C8D',
    lineHeight: 20,
  },
  section: {
    marginHorizontal: 16,
    marginVertical: 8,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#2C3E50',
    marginBottom: 12,
  },
  photoOptions: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  photoCard: {
    flex: 1,
    marginHorizontal: 4,
    borderRadius: 12,
    elevation: 3,
  },
  photoGradient: {
    borderRadius: 12,
    padding: 20,
  },
  photoCardContent: {
    alignItems: 'center',
  },
  photoCardTitle: {
    color: 'white',
    fontSize: 16,
    fontWeight: 'bold',
    marginTop: 8,
    marginBottom: 4,
  },
  photoCardSubtitle: {
    color: 'white',
    fontSize: 12,
    opacity: 0.9,
  },
  imagePreview: {
    borderRadius: 12,
    padding: 12,
    marginBottom: 16,
    elevation: 2,
    backgroundColor: 'white',
  },
  previewImage: {
    width: '100%',
    height: 200,
    borderRadius: 8,
    resizeMode: 'cover',
  },
  analyzeButton: {
    borderRadius: 8,
    paddingVertical: 4,
  },
  resultCard: {
    borderRadius: 12,
    elevation: 2,
    marginBottom: 12,
  },
  resultHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 16,
  },
  resultTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#2C3E50',
    marginLeft: 8,
  },
  resultItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 8,
  },
  resultLabel: {
    fontSize: 16,
    color: '#7F8C8D',
  },
  resultValue: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#2C3E50',
  },
  resultNote: {
    fontSize: 14,
    color: '#7F8C8D',
    marginTop: 12,
    textAlign: 'center',
    fontStyle: 'italic',
  },
  imageCard: {
    borderRadius: 12,
    elevation: 2,
  },
  imageCardTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#2C3E50',
    marginBottom: 12,
    textAlign: 'center',
  },
  analyzedImages: {
    flexDirection: 'row',
    justifyContent: 'space-around',
  },
  analyzedImageContainer: {
    alignItems: 'center',
  },
  imageLabel: {
    fontSize: 14,
    color: '#7F8C8D',
    marginBottom: 8,
  },
  analyzedImage: {
    width: 100,
    height: 100,
    borderRadius: 8,
    resizeMode: 'cover',
  },
  bottomSpacing: {
    height: 20,
  },
}); 