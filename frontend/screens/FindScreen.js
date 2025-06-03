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
  Text,
  Surface,
} from 'react-native-paper';
import * as ImagePicker from 'expo-image-picker';
import { Ionicons } from '@expo/vector-icons';
import { LinearGradient } from 'expo-linear-gradient';

const API_BASE_URL = 'http://192.168.0.5:8000'; // 실제 서버 IP로 변경 필요

export default function FindScreen() {
  const [selectedImage, setSelectedImage] = useState(null);
  const [isSearching, setIsSearching] = useState(false);
  const [searchResults, setSearchResults] = useState(null);
  const [matchedDogs, setMatchedDogs] = useState([]);

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
      setSearchResults(null);
      setMatchedDogs([]);
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
      setSearchResults(null);
      setMatchedDogs([]);
    }
  };

  const searchSimilarDogs = async () => {
    if (!selectedImage) {
      Alert.alert('오류', '먼저 코 사진을 선택해주세요.');
      return;
    }

    setIsSearching(true);
    
    try {
      // 1. 매칭 검색
      const formData = new FormData();
      formData.append('file', {
        uri: selectedImage,
        type: 'image/jpeg',
        name: 'nose_photo.jpg',
      });

      const matchResponse = await fetch(`${API_BASE_URL}/match`, {
        method: 'POST',
        body: formData,
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      const matchResult = await matchResponse.json();
      setSearchResults(matchResult);

      // 2. 매칭된 강아지들의 상세 정보 가져오기
      if (matchResult.matches && matchResult.matches.length > 0) {
        const dogDetailsResponse = await fetch(`${API_BASE_URL}/admin/list`);
        const allDogs = await dogDetailsResponse.json();
        
        const matchedDogsData = allDogs.filter(dog => 
          matchResult.matches.includes(dog.uid)
        );
        setMatchedDogs(matchedDogsData);
      } else {
        setMatchedDogs([]);
        Alert.alert('검색 결과', '일치하는 반려견을 찾을 수 없습니다.');
      }
    } catch (error) {
      console.error('Search error:', error);
      Alert.alert('오류', '검색 중 오류가 발생했습니다. 네트워크 연결을 확인해주세요.');
    } finally {
      setIsSearching(false);
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

  const MatchedDogCard = ({ dog }) => (
    <Card style={styles.matchCard}>
      <Card.Content>
        <View style={styles.matchHeader}>
          <Ionicons name="paw" size={20} color="#0047AB" />
          <Text style={styles.matchTitle}>매칭된 반려견</Text>
        </View>
        
        <View style={styles.matchContent}>
          <View style={styles.matchImages}>
            <View style={styles.matchImageContainer}>
              <Text style={styles.matchImageLabel}>전체 사진</Text>
              <Image source={{ uri: dog.dog_img_url }} style={styles.matchImage} />
            </View>
            <View style={styles.matchImageContainer}>
              <Text style={styles.matchImageLabel}>코 사진</Text>
              <Image source={{ uri: dog.nose_img_url }} style={styles.matchImage} />
            </View>
          </View>
          
          <View style={styles.matchInfo}>
            <View style={styles.matchInfoItem}>
              <Text style={styles.matchInfoLabel}>견종:</Text>
              <Text style={styles.matchInfoValue}>{dog.species}</Text>
            </View>
            <View style={styles.matchInfoItem}>
              <Text style={styles.matchInfoLabel}>등록 ID:</Text>
              <Text style={styles.matchInfoValue}>{dog.uid}</Text>
            </View>
          </View>
        </View>
      </Card.Content>
    </Card>
  );

  return (
    <ScrollView style={styles.container} showsVerticalScrollIndicator={false}>
      {/* 안내 카드 */}
      <Card style={styles.infoCard}>
        <LinearGradient
          colors={['#4A90E2', '#0047AB']}
          style={styles.infoGradient}
          start={{ x: 0, y: 0 }}
          end={{ x: 1, y: 1 }}
        >
          <Card.Content style={styles.infoContent}>
            <View style={styles.infoHeader}>
              <Ionicons name="search" size={30} color="white" />
              <Title style={styles.infoTitle}>유실견 찾기</Title>
            </View>
            <Paragraph style={styles.infoText}>
              찾고 있는 강아지의 코 부분을 촬영하거나 선택해주세요.{'\n'}
              AI가 등록된 반려견들과 비교하여 유사한 코 패턴을 찾아드립니다.
            </Paragraph>
          </Card.Content>
        </LinearGradient>
      </Card>

      {/* 사진 선택 */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>코 사진 선택</Text>
        <View style={styles.photoOptions}>
          <PhotoPickerCard
            title="카메라"
            subtitle="코 사진 촬영하기"
            icon="camera"
            gradient={['#0047AB', '#4A90E2']}
            onPress={takePhoto}
          />
          <PhotoPickerCard
            title="갤러리"
            subtitle="코 사진 선택하기"
            icon="images"
            gradient={['#6BB6FF', '#4A90E2']}
            onPress={pickImage}
          />
        </View>
      </View>

      {/* 팁 카드 */}
      <Card style={styles.tipCard}>
        <Card.Content>
          <View style={styles.tipHeader}>
            <Ionicons name="bulb" size={20} color="#6BB6FF" />
            <Text style={styles.tipTitle}>촬영 팁</Text>
          </View>
          <Text style={styles.tipText}>
            • 강아지의 코가 정면으로 잘 보이도록 촬영해주세요{'\n'}
            • 밝은 곳에서 선명하게 촬영해주세요{'\n'}
            • 코 주변의 털 패턴도 포함해서 촬영하면 더 정확합니다
          </Text>
        </Card.Content>
      </Card>

      {/* 선택된 사진 미리보기 */}
      {selectedImage && (
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>선택된 코 사진</Text>
          <Surface style={styles.imagePreview}>
            <Image source={{ uri: selectedImage }} style={styles.previewImage} />
          </Surface>
          
          <Button
            mode="contained"
            onPress={searchSimilarDogs}
            loading={isSearching}
            disabled={isSearching}
            style={styles.searchButton}
            buttonColor="#4A90E2"
          >
            {isSearching ? '유사견 검색 중...' : '유사견 검색 시작'}
          </Button>
        </View>
      )}

      {/* 검색 결과 */}
      {searchResults && (
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>검색 결과</Text>
          
          {matchedDogs.length > 0 ? (
            <>
              <Card style={styles.resultSummary}>
                <Card.Content>
                  <View style={styles.resultHeader}>
                    <Ionicons name="checkmark-circle" size={24} color="#4CAF50" />
                    <Text style={styles.resultTitle}>
                      {matchedDogs.length}마리의 유사한 반려견을 찾았습니다!
                    </Text>
                  </View>
                </Card.Content>
              </Card>
              
              {matchedDogs.map((dog, index) => (
                <MatchedDogCard key={dog.uid} dog={dog} />
              ))}
            </>
          ) : (
            <Card style={styles.noResultCard}>
              <Card.Content>
                <View style={styles.noResultContent}>
                  <Ionicons name="sad" size={40} color="#7F8C8D" />
                  <Text style={styles.noResultTitle}>일치하는 반려견을 찾을 수 없습니다</Text>
                  <Text style={styles.noResultText}>
                    등록된 반려견 중에서 유사한 코 패턴을 가진 강아지를 찾지 못했습니다.{'\n'}
                    다른 각도의 사진으로 다시 시도해보세요.
                  </Text>
                </View>
              </Card.Content>
            </Card>
          )}
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
    borderRadius: 16,
    elevation: 4,
  },
  infoGradient: {
    borderRadius: 16,
  },
  infoContent: {
    padding: 20,
  },
  infoHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 12,
  },
  infoTitle: {
    color: 'white',
    fontSize: 20,
    fontWeight: 'bold',
    marginLeft: 12,
  },
  infoText: {
    color: 'white',
    fontSize: 14,
    lineHeight: 20,
    opacity: 0.9,
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
  tipCard: {
    margin: 16,
    borderRadius: 12,
    elevation: 2,
  },
  tipHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8,
  },
  tipTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#2C3E50',
    marginLeft: 8,
  },
  tipText: {
    fontSize: 14,
    color: '#7F8C8D',
    lineHeight: 20,
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
  searchButton: {
    borderRadius: 8,
    paddingVertical: 4,
  },
  resultSummary: {
    borderRadius: 12,
    elevation: 2,
    marginBottom: 12,
  },
  resultHeader: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  resultTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#2C3E50',
    marginLeft: 8,
    flex: 1,
  },
  matchCard: {
    borderRadius: 12,
    elevation: 2,
    marginBottom: 12,
  },
  matchHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 12,
  },
  matchTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#2C3E50',
    marginLeft: 8,
  },
  matchContent: {
    marginTop: 8,
  },
  matchImages: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    marginBottom: 16,
  },
  matchImageContainer: {
    alignItems: 'center',
  },
  matchImageLabel: {
    fontSize: 12,
    color: '#7F8C8D',
    marginBottom: 8,
  },
  matchImage: {
    width: 80,
    height: 80,
    borderRadius: 8,
    resizeMode: 'cover',
  },
  matchInfo: {
    backgroundColor: '#F8F9FA',
    borderRadius: 8,
    padding: 12,
  },
  matchInfoItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 4,
  },
  matchInfoLabel: {
    fontSize: 14,
    color: '#7F8C8D',
  },
  matchInfoValue: {
    fontSize: 14,
    fontWeight: 'bold',
    color: '#2C3E50',
  },
  noResultCard: {
    borderRadius: 12,
    elevation: 2,
  },
  noResultContent: {
    alignItems: 'center',
    paddingVertical: 20,
  },
  noResultTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#7F8C8D',
    marginTop: 12,
    marginBottom: 8,
  },
  noResultText: {
    fontSize: 14,
    color: '#7F8C8D',
    textAlign: 'center',
    lineHeight: 20,
  },
  bottomSpacing: {
    height: 20,
  },
}); 