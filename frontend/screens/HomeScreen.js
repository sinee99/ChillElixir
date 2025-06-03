import React from 'react';
import {
  View,
  ScrollView,
  StyleSheet,
  Dimensions,
  TouchableOpacity,
} from 'react-native';
import {
  Card,
  Title,
  Paragraph,
  Button,
  Surface,
  Text,
} from 'react-native-paper';
import { LinearGradient } from 'expo-linear-gradient';
import { Ionicons } from '@expo/vector-icons';

const { width } = Dimensions.get('window');

export default function HomeScreen({ navigation }) {
  const MenuCard = ({ title, subtitle, icon, color, onPress, gradientColors }) => (
    <TouchableOpacity onPress={onPress} style={styles.menuCard}>
      <LinearGradient
        colors={gradientColors || ['#FF6B6B', '#FF8E8E']}
        style={styles.gradientCard}
        start={{ x: 0, y: 0 }}
        end={{ x: 1, y: 1 }}
      >
        <View style={styles.cardContent}>
          <View style={styles.iconContainer}>
            <Ionicons name={icon} size={30} color="white" />
          </View>
          <View style={styles.textContainer}>
            <Text style={styles.cardTitle}>{title}</Text>
            <Text style={styles.cardSubtitle}>{subtitle}</Text>
          </View>
        </View>
      </LinearGradient>
    </TouchableOpacity>
  );

  const QuickActionCard = ({ title, description, icon, onPress }) => (
    <TouchableOpacity onPress={onPress} style={styles.quickCard}>
      <Surface style={styles.quickCardSurface}>
        <View style={styles.quickCardContent}>
          <Ionicons name={icon} size={24} color="#0047AB" />
          <Text style={styles.quickCardTitle}>{title}</Text>
          <Text style={styles.quickCardDesc}>{description}</Text>
        </View>
      </Surface>
    </TouchableOpacity>
  );

  return (
    <ScrollView style={styles.container} showsVerticalScrollIndicator={false}>
      {/* 웰컴 카드 */}
      <Card style={styles.welcomeCard}>
        <LinearGradient
          colors={['#4A90E2', '#0047AB']}
          style={styles.welcomeGradient}
          start={{ x: 0, y: 0 }}
          end={{ x: 1, y: 1 }}
        >
          <Card.Content style={styles.welcomeContent}>
            <Title style={styles.welcomeTitle}>
              안녕하세요! 🐾
            </Title>
            <Paragraph style={styles.welcomeText}>
              LostPet과 함께 반려견을 안전하게 지켜보세요
            </Paragraph>
          </Card.Content>
        </LinearGradient>
      </Card>

      {/* 주요 기능 메뉴 */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>주요 기능</Text>
        
        <MenuCard
          title="반려견 등록하기"
          subtitle="AI로 우리 강아지를 분석해보세요"
          icon="camera"
          gradientColors={['#0047AB', '#4A90E2']}
          onPress={() => navigation.navigate('Register')}
        />

        <MenuCard
          title="유실견 찾기"
          subtitle="코 사진으로 유실견을 찾아보세요"
          icon="search"
          gradientColors={['#6BB6FF', '#4A90E2']}
          onPress={() => navigation.navigate('Find')}
        />

        <MenuCard
          title="내 반려견 관리"
          subtitle="등록된 반려견 정보를 확인하세요"
          icon="heart"
          gradientColors={['#1E90FF', '#6BB6FF']}
          onPress={() => navigation.navigate('MyPets')}
        />
      </View>

      {/* 빠른 실행 */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>빠른 실행</Text>
        <View style={styles.quickActions}>
          <QuickActionCard
            title="즉시 촬영"
            description="바로 사진 찍기"
            icon="camera-outline"
            onPress={() => navigation.navigate('Register')}
          />
          <QuickActionCard
            title="갤러리 선택"
            description="사진 불러오기"
            icon="images-outline"
            onPress={() => navigation.navigate('Register')}
          />
        </View>
      </View>

      {/* 통계 카드 */}
      <Card style={styles.statsCard}>
        <Card.Content>
          <Title style={styles.statsTitle}>서비스 현황</Title>
          <View style={styles.statsRow}>
            <View style={styles.statItem}>
              <Text style={styles.statNumber}>1,247</Text>
              <Text style={styles.statLabel}>등록된 반려견</Text>
            </View>
            <View style={styles.statItem}>
              <Text style={styles.statNumber}>89</Text>
              <Text style={styles.statLabel}>성공적 매칭</Text>
            </View>
            <View style={styles.statItem}>
              <Text style={styles.statNumber}>119</Text>
              <Text style={styles.statLabel}>지원 견종</Text>
            </View>
          </View>
        </Card.Content>
      </Card>

      <View style={styles.bottomSpacing} />
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F8F9FA',
  },
  welcomeCard: {
    margin: 16,
    borderRadius: 16,
    elevation: 4,
  },
  welcomeGradient: {
    borderRadius: 16,
  },
  welcomeContent: {
    padding: 20,
  },
  welcomeTitle: {
    color: 'white',
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 8,
  },
  welcomeText: {
    color: 'white',
    fontSize: 16,
    opacity: 0.9,
  },
  section: {
    marginHorizontal: 16,
    marginVertical: 8,
  },
  sectionTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#2C3E50',
    marginBottom: 16,
  },
  menuCard: {
    marginBottom: 12,
    borderRadius: 16,
    elevation: 3,
  },
  gradientCard: {
    borderRadius: 16,
    padding: 20,
  },
  cardContent: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  iconContainer: {
    width: 50,
    height: 50,
    borderRadius: 25,
    backgroundColor: 'rgba(255,255,255,0.2)',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 16,
  },
  textContainer: {
    flex: 1,
  },
  cardTitle: {
    color: 'white',
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 4,
  },
  cardSubtitle: {
    color: 'white',
    fontSize: 14,
    opacity: 0.9,
  },
  quickActions: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  quickCard: {
    flex: 1,
    marginHorizontal: 4,
  },
  quickCardSurface: {
    borderRadius: 12,
    elevation: 2,
    backgroundColor: 'white',
  },
  quickCardContent: {
    padding: 16,
    alignItems: 'center',
  },
  quickCardTitle: {
    fontSize: 14,
    fontWeight: 'bold',
    color: '#2C3E50',
    marginTop: 8,
    marginBottom: 4,
  },
  quickCardDesc: {
    fontSize: 12,
    color: '#7F8C8D',
    textAlign: 'center',
  },
  statsCard: {
    margin: 16,
    borderRadius: 16,
    elevation: 2,
  },
  statsTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#2C3E50',
    marginBottom: 16,
    textAlign: 'center',
  },
  statsRow: {
    flexDirection: 'row',
    justifyContent: 'space-around',
  },
  statItem: {
    alignItems: 'center',
  },
  statNumber: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#0047AB',
    marginBottom: 4,
  },
  statLabel: {
    fontSize: 12,
    color: '#7F8C8D',
    textAlign: 'center',
  },
  bottomSpacing: {
    height: 20,
  },
}); 