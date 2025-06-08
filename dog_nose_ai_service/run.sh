#!/bin/bash

# 🐕 강아지 비문 인식 AI 서비스 실행 스크립트

set -e

# 색상 설정
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 로고 출력
echo -e "${BLUE}"
echo "🐕 =================================="
echo "   강아지 비문 인식 AI 서비스"
echo "   Dog Nose Recognition AI Service"  
echo "==================================${NC}"
echo ""

# 함수 정의
show_help() {
    echo "사용법: $0 [COMMAND] [OPTIONS]"
    echo ""
    echo "Commands:"
    echo "  setup     - 모델 준비 및 초기 설정"
    echo "  build     - Docker 이미지 빌드"
    echo "  start     - 서비스 시작"
    echo "  stop      - 서비스 중지"
    echo "  restart   - 서비스 재시작"
    echo "  logs      - 로그 확인"
    echo "  test      - API 테스트"
    echo "  clean     - 컨테이너 및 이미지 정리"
    echo "  status    - 서비스 상태 확인"
    echo ""
    echo "Options:"
    echo "  --gpu     - GPU 모드로 실행"
    echo "  --cpu     - CPU 모드로 실행"
    echo "  --help    - 도움말 표시"
}

check_requirements() {
    echo -e "${YELLOW}📋 시스템 요구사항 확인 중...${NC}"
    
    # Docker 확인
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}❌ Docker가 설치되지 않았습니다.${NC}"
        echo "Docker를 설치한 후 다시 시도해주세요."
        exit 1
    fi
    
    # Docker Compose 확인
    if ! command -v docker-compose &> /dev/null; then
        echo -e "${RED}❌ Docker Compose가 설치되지 않았습니다.${NC}"
        echo "Docker Compose를 설치한 후 다시 시도해주세요."
        exit 1
    fi
    
    # Docker 실행 상태 확인
    if ! docker info &> /dev/null; then
        echo -e "${RED}❌ Docker가 실행되고 있지 않습니다.${NC}"
        echo "Docker를 시작한 후 다시 시도해주세요."
        exit 1
    fi
    
    echo -e "${GREEN}✅ 시스템 요구사항 확인 완료${NC}"
}

setup_models() {
    echo -e "${YELLOW}🔧 모델 설정 중...${NC}"
    
    # 모델 디렉토리 생성
    mkdir -p models
    
    # 원본 프로젝트 경로 확인
    if [ -d "../dognose_recognition_management_service-main" ]; then
        SOURCE_PATH="../dognose_recognition_management_service-main"
    elif [ -d "./dognose_recognition_management_service-main" ]; then
        SOURCE_PATH="./dognose_recognition_management_service-main"
    else
        echo -e "${RED}❌ 원본 프로젝트를 찾을 수 없습니다.${NC}"
        echo "dognose_recognition_management_service-main 폴더가 있는지 확인해주세요."
        read -p "원본 프로젝트 경로를 입력하세요: " SOURCE_PATH
        
        if [ ! -d "$SOURCE_PATH" ]; then
            echo -e "${RED}❌ 지정된 경로가 존재하지 않습니다.${NC}"
            exit 1
        fi
    fi
    
    # 모델 변환 실행
    echo "모델 변환 중..."
    if python3 model_converter.py --source "$SOURCE_PATH" --target "./models"; then
        echo -e "${GREEN}✅ 모델 설정 완료${NC}"
    else
        echo -e "${RED}❌ 모델 설정 실패${NC}"
        exit 1
    fi
}

build_image() {
    echo -e "${YELLOW}🔨 Docker 이미지 빌드 중...${NC}"
    
    if docker-compose build; then
        echo -e "${GREEN}✅ 이미지 빌드 완료${NC}"
    else
        echo -e "${RED}❌ 이미지 빌드 실패${NC}"
        exit 1
    fi
}

start_service() {
    echo -e "${YELLOW}🚀 서비스 시작 중...${NC}"
    
    # GPU/CPU 모드 설정
    if [[ "$*" == *"--gpu"* ]]; then
        echo "GPU 모드로 시작합니다..."
        export COMPOSE_FILE="docker-compose.yml"
    elif [[ "$*" == *"--cpu"* ]]; then
        echo "CPU 모드로 시작합니다..."
        # GPU 설정 제거를 위한 임시 compose 파일 생성
        cp docker-compose.yml docker-compose.cpu.yml
        sed -i '/deploy:/,/capabilities: \[gpu\]/d' docker-compose.cpu.yml
        export COMPOSE_FILE="docker-compose.cpu.yml"
    fi
    
    if docker-compose up -d; then
        echo -e "${GREEN}✅ 서비스 시작 완료${NC}"
        echo ""
        echo "서비스 URL: http://localhost:5000"
        echo "헬스 체크: http://localhost:5000/health"
        echo ""
        echo -e "${BLUE}💡 로그 확인: $0 logs${NC}"
        echo -e "${BLUE}💡 테스트 실행: $0 test${NC}"
    else
        echo -e "${RED}❌ 서비스 시작 실패${NC}"
        exit 1
    fi
}

stop_service() {
    echo -e "${YELLOW}⏹️ 서비스 중지 중...${NC}"
    
    if docker-compose down; then
        echo -e "${GREEN}✅ 서비스 중지 완료${NC}"
    else
        echo -e "${RED}❌ 서비스 중지 실패${NC}"
        exit 1
    fi
}

restart_service() {
    echo -e "${YELLOW}🔄 서비스 재시작 중...${NC}"
    stop_service
    start_service "$@"
}

show_logs() {
    echo -e "${YELLOW}📜 로그 확인 중...${NC}"
    docker-compose logs -f
}

test_service() {
    echo -e "${YELLOW}🧪 API 테스트 중...${NC}"
    
    # 테스트 이미지 확인
    if [ ! -f "test_dog.jpg" ]; then
        echo -e "${YELLOW}⚠️ test_dog.jpg 파일이 없습니다.${NC}"
        read -p "테스트용 강아지 이미지 경로를 입력하세요: " TEST_IMAGE
        
        if [ ! -f "$TEST_IMAGE" ]; then
            echo -e "${RED}❌ 테스트 이미지를 찾을 수 없습니다.${NC}"
            exit 1
        fi
    else
        TEST_IMAGE="test_dog.jpg"
    fi
    
    # Python 테스트 스크립트 실행
    if python3 test_api.py --image "$TEST_IMAGE"; then
        echo -e "${GREEN}✅ 테스트 완료${NC}"
    else
        echo -e "${RED}❌ 테스트 실패${NC}"
        exit 1
    fi
}

clean_docker() {
    echo -e "${YELLOW}🧹 Docker 정리 중...${NC}"
    
    # 컨테이너 중지 및 제거
    docker-compose down --remove-orphans
    
    # 이미지 제거
    docker rmi dog-nose-ai_dog-nose-ai 2>/dev/null || true
    
    # 볼륨 정리
    docker volume prune -f
    
    # 네트워크 정리
    docker network prune -f
    
    echo -e "${GREEN}✅ Docker 정리 완료${NC}"
}

check_status() {
    echo -e "${YELLOW}📊 서비스 상태 확인 중...${NC}"
    
    # 컨테이너 상태
    echo "=== 컨테이너 상태 ==="
    docker-compose ps
    
    echo ""
    
    # 헬스 체크
    echo "=== 헬스 체크 ==="
    if curl -s -f http://localhost:5000/health > /dev/null; then
        echo -e "${GREEN}✅ 서비스가 정상적으로 실행 중입니다.${NC}"
        curl -s http://localhost:5000/health | python3 -m json.tool
    else
        echo -e "${RED}❌ 서비스에 접근할 수 없습니다.${NC}"
    fi
}

# 메인 실행 로직
case "$1" in
    setup)
        check_requirements
        setup_models
        ;;
    build)
        check_requirements
        build_image
        ;;
    start)
        check_requirements
        start_service "$@"
        ;;
    stop)
        stop_service
        ;;
    restart)
        restart_service "$@"
        ;;
    logs)
        show_logs
        ;;
    test)
        test_service
        ;;
    clean)
        clean_docker
        ;;
    status)
        check_status
        ;;
    --help|help)
        show_help
        ;;
    "")
        echo -e "${RED}❌ 명령을 지정해주세요.${NC}"
        echo ""
        show_help
        exit 1
        ;;
    *)
        echo -e "${RED}❌ 알 수 없는 명령: $1${NC}"
        echo ""
        show_help
        exit 1
        ;;
esac 