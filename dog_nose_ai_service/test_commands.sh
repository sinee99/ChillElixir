#!/bin/bash
# 강아지 비문 인식 API 테스트 명령어들

echo "🔍 서버 상태 확인"
curl -X GET http://localhost:5000/health | jq

echo -e "
🔍 모델 목록 조회"
curl -X GET http://localhost:5000/models | jq

echo -e "
🔍 모델 전환 테스트 (canny 모델로 변경)"
curl -X POST -H "Content-Type: application/json" -d '{"model_type": "canny"}' http://localhost:5000/switch_model | jq

# 이미지가 있는 경우의 테스트 명령어들 (주석 해제하여 사용)
# echo -e "
🔍 코 크롭 테스트"
# curl -X POST -F "image=@test_images/dog1.jpg" http://localhost:5000/crop_nose | jq

# echo -e "
🔍 특징 추출 테스트"
# curl -X POST -F "image=@test_images/dog1.jpg" -F "model_type=original" http://localhost:5000/extract_features | jq

# echo -e "
🔍 전체 프로세스 테스트"
# curl -X POST -F "image=@test_images/dog1.jpg" -F "model_type=canny" http://localhost:5000/process_full | jq

# echo -e "
🔍 비문 비교 테스트"
# curl -X POST -F "image1=@test_images/dog1.jpg" -F "image2=@test_images/dog2.jpg" -F "model_type=original" http://localhost:5000/compare_noses | jq
