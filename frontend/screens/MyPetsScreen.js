import React, { useState, useEffect } from 'react';
import {
  View,
  ScrollView,
  StyleSheet,
  Image,
  Alert,
  RefreshControl,
  TouchableOpacity,
} from 'react-native';
import {
  Card,
  Title,
  Paragraph,
  Button,
  Text,
  Surface,
  FAB,
} from 'react-native-paper';
import { Ionicons } from '@expo/vector-icons';
import { LinearGradient } from 'expo-linear-gradient';

const API_BASE_URL = 'http://192.168.0.5:8000'; // 실제 서버 IP로 변경 필요

export default function MyPetsScreen({ navigation }) {
  const [dogs, setDogs] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    loadDogs();
  }, []);

  const loadDogs = async () => {
    setIsLoading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/admin/list`);
      const data = await response.json();
      setDogs(data);
    } catch (error) {
      console.error('Load dogs error:', error);
      Alert.alert('오류', '반려견 목록을 불러오는 중 오류가 발생했습니다.');
    } finally {
      setIsLoading(false);
    }
  };

  const onRefresh = async () => {
    setRefreshing(true);
    await loadDogs();
    setRefreshing(false);
  };

  const deleteDog = async (uid, species) => {
    Alert.alert(
      '삭제 확인',
      `${species}를 정말로 삭제하시겠습니까?`,
      [
        { text: '취소', style: 'cancel' },
        {
          text: '삭제',
          style: 'destructive',
          onPress: async () => {
            try {
              const response = await fetch(`${API_BASE_URL}/admin/delete/${uid}`, {
                method: 'DELETE',
              });
              
              if (response.ok) {
                Alert.alert('성공', '반려견이 삭제되었습니다.');
                loadDogs(); // 목록 새로고침
              } else {
                Alert.alert('오류', '삭제 중 오류가 발생했습니다.');
              }
            } catch (error) {
              console.error('Delete error:', error);
              Alert.alert('오류', '삭제 중 오류가 발생했습니다.');
            }
          },
        },
      ]
    );
  };

  const DogCard = ({ dog }) => (
    <Card style={styles.dogCard}>
      <Card.Content>
        <View style={styles.dogHeader}>
          <View style={styles.dogHeaderLeft}>
            <Ionicons name="paw" size={20} color="#0047AB" />
            <Text style={styles.dogSpecies}>{dog.species}</Text>
          </View>
          <TouchableOpacity
            onPress={() => deleteDog(dog.uid, dog.species)}
            style={styles.deleteButton}
          >
            <Ionicons name="trash" size={20} color="#E74C3C" />
          </TouchableOpacity>
        </View>
        
        <View style={styles.dogContent}>
          <View style={styles.dogImages}>
            <View style={styles.dogImageContainer}>
              <Text style={styles.imageLabel}>전체 사진</Text>
              <Image source={{ uri: dog.dog_img_url }} style={styles.dogImage} />
            </View>
            <View style={styles.dogImageContainer}>
              <Text style={styles.imageLabel}>코 사진</Text>
              <Image source={{ uri: dog.nose_img_url }} style={styles.dogImage} />
            </View>
          </View>
          
          <View style={styles.dogInfo}>
            <View style={styles.dogInfoItem}>
              <Text style={styles.dogInfoLabel}>등록 ID:</Text>
              <Text style={styles.dogInfoValue}>{dog.uid.substring(0, 8)}...</Text>
            </View>
            <View style={styles.dogInfoItem}>
              <Text style={styles.dogInfoLabel}>등록일:</Text>
              <Text style={styles.dogInfoValue}>최근</Text>
            </View>
          </View>
        </View>
      </Card.Content>
    </Card>
  );

  const EmptyState = () => (
    <View style={styles.emptyContainer}>
      <Surface style={styles.emptySurface}>
        <View style={styles.emptyContent}>
          <Ionicons name="heart-outline" size={60} color="#BDC3C7" />
          <Text style={styles.emptyTitle}>등록된 반려견이 없습니다</Text>
          <Text style={styles.emptySubtitle}>
            반려견을 등록하여 AI 기반 유실견 찾기 서비스를 이용해보세요
          </Text>
          <Button
            mode="contained"
            onPress={() => navigation.navigate('Register')}
            style={styles.emptyButton}
            buttonColor="#0047AB"
          >
            첫 번째 반려견 등록하기
          </Button>
        </View>
      </Surface>
    </View>
  );

  return (
    <View style={styles.container}>
      {/* 상단 통계 카드 */}
      <Card style={styles.statsCard}>
        <LinearGradient
          colors={['#6BB6FF', '#4A90E2']}
          style={styles.statsGradient}
          start={{ x: 0, y: 0 }}
          end={{ x: 1, y: 1 }}
        >
          <Card.Content style={styles.statsContent}>
            <View style={styles.statsRow}>
              <View style={styles.statItem}>
                <Text style={styles.statNumber}>{dogs.length}</Text>
                <Text style={styles.statLabel}>등록된 반려견</Text>
              </View>
              <View style={styles.statDivider} />
              <View style={styles.statItem}>
                <Text style={styles.statNumber}>
                  {dogs.reduce((acc, dog) => acc.add(dog.species), new Set()).size}
                </Text>
                <Text style={styles.statLabel}>견종 수</Text>
              </View>
            </View>
          </Card.Content>
        </LinearGradient>
      </Card>

      {/* 반려견 목록 */}
      <ScrollView
        style={styles.scrollView}
        showsVerticalScrollIndicator={false}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
        }
      >
        {dogs.length === 0 ? (
          <EmptyState />
        ) : (
          <View style={styles.dogList}>
            <View style={styles.listHeader}>
              <Text style={styles.listTitle}>등록된 반려견 목록</Text>
              <Text style={styles.listSubtitle}>
                아래로 당겨서 새로고침할 수 있습니다
              </Text>
            </View>
            
            {dogs.map((dog) => (
              <DogCard key={dog.uid} dog={dog} />
            ))}
          </View>
        )}
        
        <View style={styles.bottomSpacing} />
      </ScrollView>

      {/* 플로팅 액션 버튼 */}
      <FAB
        icon="plus"
        style={styles.fab}
        onPress={() => navigation.navigate('Register')}
        color="white"
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F8F9FA',
  },
  statsCard: {
    margin: 16,
    borderRadius: 16,
    elevation: 4,
  },
  statsGradient: {
    borderRadius: 16,
  },
  statsContent: {
    padding: 20,
  },
  statsRow: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  statItem: {
    flex: 1,
    alignItems: 'center',
  },
  statDivider: {
    width: 1,
    height: 40,
    backgroundColor: 'rgba(255,255,255,0.3)',
    marginHorizontal: 20,
  },
  statNumber: {
    color: 'white',
    fontSize: 28,
    fontWeight: 'bold',
    marginBottom: 4,
  },
  statLabel: {
    color: 'white',
    fontSize: 14,
    opacity: 0.9,
  },
  scrollView: {
    flex: 1,
  },
  dogList: {
    paddingHorizontal: 16,
  },
  listHeader: {
    marginBottom: 16,
  },
  listTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#2C3E50',
    marginBottom: 4,
  },
  listSubtitle: {
    fontSize: 14,
    color: '#7F8C8D',
  },
  dogCard: {
    borderRadius: 12,
    elevation: 2,
    marginBottom: 12,
  },
  dogHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 16,
  },
  dogHeaderLeft: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  dogSpecies: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#2C3E50',
    marginLeft: 8,
  },
  deleteButton: {
    padding: 8,
    borderRadius: 20,
    backgroundColor: '#FCF3F3',
  },
  dogContent: {
    marginTop: 8,
  },
  dogImages: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    marginBottom: 16,
  },
  dogImageContainer: {
    alignItems: 'center',
  },
  imageLabel: {
    fontSize: 12,
    color: '#7F8C8D',
    marginBottom: 8,
  },
  dogImage: {
    width: 100,
    height: 100,
    borderRadius: 8,
    resizeMode: 'cover',
  },
  dogInfo: {
    backgroundColor: '#F8F9FA',
    borderRadius: 8,
    padding: 12,
  },
  dogInfoItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 4,
  },
  dogInfoLabel: {
    fontSize: 14,
    color: '#7F8C8D',
  },
  dogInfoValue: {
    fontSize: 14,
    fontWeight: 'bold',
    color: '#2C3E50',
  },
  emptyContainer: {
    flex: 1,
    padding: 16,
    marginTop: 40,
  },
  emptySurface: {
    borderRadius: 16,
    elevation: 2,
    backgroundColor: 'white',
  },
  emptyContent: {
    alignItems: 'center',
    paddingVertical: 40,
    paddingHorizontal: 20,
  },
  emptyTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#7F8C8D',
    marginTop: 16,
    marginBottom: 8,
  },
  emptySubtitle: {
    fontSize: 14,
    color: '#7F8C8D',
    textAlign: 'center',
    lineHeight: 20,
    marginBottom: 24,
  },
  emptyButton: {
    borderRadius: 8,
    paddingHorizontal: 16,
  },
  fab: {
    position: 'absolute',
    margin: 16,
    right: 0,
    bottom: 0,
    backgroundColor: '#0047AB',
  },
  bottomSpacing: {
    height: 80,
  },
}); 