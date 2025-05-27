// frontend/utils/api.js

// 서버 주소를 본인의 FastAPI 주소로 바꾸세요!
const BASE_URL = 'http://<YOUR_BACKEND_SERVER>:8000'; // 예: http://192.168.0.5:8000

export const analyzeDog = async (uri) => {
  const formData = new FormData();
  formData.append('file', {
    uri,
    name: 'dog.jpg',
    type: 'image/jpeg',
  });

  try {
    const response = await fetch(`${BASE_URL}/analyze`, {
      method: 'POST',
      body: formData,
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });

    return await response.json();
  } catch (err) {
    console.error('분석 요청 실패:', err);
    return { error: '서버 오류 또는 연결 실패' };
  }
};

export const matchDog = async (uri) => {
  const formData = new FormData();
  formData.append('file', {
    uri,
    name: 'query.jpg',
    type: 'image/jpeg',
  });

  try {
    const response = await fetch(`${BASE_URL}/match`, {
      method: 'POST',
      body: formData,
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });

    return await response.json();
  } catch (err) {
    console.error('매칭 요청 실패:', err);
    return { error: '서버 오류 또는 연결 실패' };
  }
};
