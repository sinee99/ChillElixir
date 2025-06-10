import requests
import json

def get_access_token():
    """OAuth2 액세스 토큰을 획득합니다."""
    token_url = 'https://www.nyckel.com/connect/token'
    data = {
        'grant_type': 'client_credentials',
        'client_id': 'iq34c1zbwx18d0939kd6aifur3mwfy75',
        'client_secret': '5zxo5xdzbs581opp4sl3zeqza8d8f2vypv2d2kxc6evid7s2ewsnc36r9xdxj4k9'
    }
    
    try:
        response = requests.post(token_url, data=data)
        response.raise_for_status()
        token = response.json()['access_token']
        print("✅ 토큰 획득 성공")
        return token
    except Exception as e:
        print(f"❌ 토큰 획득 실패: {e}")
        return None

def create_label(token, function_id, label_name, description=""):
    """올바른 형식으로 라벨을 생성합니다."""
    url = f'https://www.nyckel.com/v1/functions/{function_id}/labels'
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    # API 문서에 따른 올바른 형식
    label_data = {
        "name": label_name
    }
    
    if description:
        label_data["description"] = description
    
    try:
        response = requests.post(url, headers=headers, json=label_data)
        
        if response.status_code in [200, 201]:
            result = response.json()
            return True, f"라벨 '{label_name}' 생성 성공! ID: {result.get('id', 'Unknown')}"
        else:
            return False, f"라벨 생성 실패: {response.status_code} - {response.text}"
            
    except Exception as e:
        return False, f"오류 발생: {e}"

def list_labels(token, function_id):
    """함수의 라벨 목록을 조회합니다."""
    url = f'https://www.nyckel.com/v1/functions/{function_id}/labels'
    headers = {
        'Authorization': f'Bearer {token}'
    }
    
    try:
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            labels = response.json()
            return True, labels
        else:
            return False, f"라벨 조회 실패: {response.status_code} - {response.text}"
            
    except Exception as e:
        return False, f"오류 발생: {e}"

def main():
    """메인 함수"""
    print("🏷️  올바른 방식으로 라벨 생성 시작")
    print("="*50)
    
    # 토큰 획득
    token = get_access_token()
    if not token:
        return
    
    # 테스트할 함수들과 라벨들
    functions_labels = {
        'dog-size-classifier': {
            'id': 'function_zqro27bkkoxnt6uz',
            'labels': [
                {'name': '소형견', 'description': '작은 크기의 강아지'},
                {'name': '중형견', 'description': '중간 크기의 강아지'},
                {'name': '대형견', 'description': '큰 크기의 강아지'}
            ]
        },
        'dog-ear-type-classifier': {
            'id': 'function_63mwhy5mw03ot1a0',
            'labels': [
                {'name': '서있는귀', 'description': '직립한 귀를 가진 강아지'},
                {'name': '늘어진귀', 'description': '늘어진 귀를 가진 강아지'}
            ]
        }
    }
    
    # 각 함수에 라벨 생성
    for func_name, func_info in functions_labels.items():
        print(f"\n🔧 '{func_name}' 함수에 라벨 생성 중...")
        function_id = func_info['id']
        
        # 기존 라벨 확인
        success, labels_or_error = list_labels(token, function_id)
        if success:
            existing_labels = [label.get('name') for label in labels_or_error]
            print(f"   현재 라벨: {existing_labels}")
        else:
            print(f"   라벨 조회 실패: {labels_or_error}")
            existing_labels = []
        
        # 새 라벨들 추가
        success_count = 0
        for label_info in func_info['labels']:
            label_name = label_info['name']
            label_desc = label_info['description']
            
            if label_name in existing_labels:
                print(f"   ⏭️  라벨 '{label_name}'은 이미 존재합니다.")
                success_count += 1
                continue
            
            print(f"   📝 라벨 '{label_name}' 생성 중...")
            success, message = create_label(token, function_id, label_name, label_desc)
            
            if success:
                print(f"      ✅ {message}")
                success_count += 1
            else:
                print(f"      ❌ {message}")
        
        print(f"   📊 {func_name}: {success_count}/{len(func_info['labels'])}개 라벨 완료")
        
        # 최종 라벨 목록 확인
        success, final_labels = list_labels(token, function_id)
        if success:
            print(f"   🏷️  최종 라벨 목록: {[label.get('name') for label in final_labels]}")
    
    print(f"\n🎉 라벨 생성 작업 완료!")
    print(f"\n💡 이제 분류 테스트를 실행해보세요:")
    print(f"   python test_dog_images.py")

if __name__ == "__main__":
    main() 