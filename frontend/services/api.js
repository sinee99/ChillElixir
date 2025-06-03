// API 서비스 유틸리티 - 코발트 블루 테마 적용
const API_BASE_URL = 'http://192.168.0.5:8000'; // 개발용 - 실제 서버 IP로 변경 필요

class ApiService {
  static async analyzeDog(imageUri) {
    try {
      const formData = new FormData();
      formData.append('file', {
        uri: imageUri,
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
      
      if (!response.ok) {
        throw new Error(result.error || '분석 중 오류가 발생했습니다.');
      }

      return result;
    } catch (error) {
      console.error('Analyze dog error:', error);
      throw error;
    }
  }

  static async matchDog(imageUri) {
    try {
      const formData = new FormData();
      formData.append('file', {
        uri: imageUri,
        type: 'image/jpeg',
        name: 'nose_photo.jpg',
      });

      const response = await fetch(`${API_BASE_URL}/match`, {
        method: 'POST',
        body: formData,
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      const result = await response.json();
      
      if (!response.ok) {
        throw new Error('매칭 검색 중 오류가 발생했습니다.');
      }

      return result;
    } catch (error) {
      console.error('Match dog error:', error);
      throw error;
    }
  }

  static async getAllDogs() {
    try {
      const response = await fetch(`${API_BASE_URL}/admin/list`);
      const result = await response.json();
      
      if (!response.ok) {
        throw new Error('반려견 목록을 불러오는 중 오류가 발생했습니다.');
      }

      return result;
    } catch (error) {
      console.error('Get all dogs error:', error);
      throw error;
    }
  }

  static async deleteDog(uid) {
    try {
      const response = await fetch(`${API_BASE_URL}/admin/delete/${uid}`, {
        method: 'DELETE',
      });
      
      if (!response.ok) {
        throw new Error('반려견 삭제 중 오류가 발생했습니다.');
      }

      const result = await response.json();
      return result;
    } catch (error) {
      console.error('Delete dog error:', error);
      throw error;
    }
  }

  // 서버 연결 테스트
  static async testConnection() {
    try {
      const response = await fetch(`${API_BASE_URL}/admin/list`);
      return response.ok;
    } catch (error) {
      console.error('Connection test failed:', error);
      return false;
    }
  }
}

export default ApiService; 