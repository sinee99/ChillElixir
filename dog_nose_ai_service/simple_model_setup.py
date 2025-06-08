#!/usr/bin/env python3
"""
간단한 모델 설정 스크립트 (TensorFlow 불필요)
"""

import os
import shutil
import sys
from pathlib import Path
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def simple_model_setup():
    """TensorFlow 없이 모델 파일 복사"""
    
    # 프로젝트 경로들
    possible_sources = [
        "../dognose_recognition_management_service-main",
        "./dognose_recognition_management_service-main", 
        "dognose_recognition_management_service-main"
    ]
    
    source_path = None
    for path in possible_sources:
        if os.path.exists(path):
            source_path = Path(path)
            break
    
    if not source_path:
        logger.error("❌ 원본 프로젝트를 찾을 수 없습니다.")
        print("🔍 다음 위치에서 dognose_recognition_management_service-main 폴더를 찾고 있습니다:")
        for path in possible_sources:
            print(f"   - {os.path.abspath(path)}")
        return False
    
    print(f"✅ 원본 프로젝트 발견: {source_path}")
    
    # 모델 디렉토리 생성
    models_dir = Path("models")
    models_dir.mkdir(exist_ok=True)
    
    success_count = 0
    
    # 1. Siamese 모델 복사 (.h5 파일들)
    siamese_source = source_path / "dognose_recognition" / "model"
    if siamese_source.exists():
        print(f"📂 Siamese 모델 폴더 발견: {siamese_source}")
        
        for h5_file in siamese_source.glob("*.h5"):
            target = models_dir / f"siamese_{h5_file.name}"
            shutil.copy2(h5_file, target)
            print(f"   ✅ 복사됨: {h5_file.name} -> {target.name}")
            success_count += 1
        
        # original.h5를 기본 모델로 설정
        if (models_dir / "siamese_original.h5").exists():
            print("   🎯 original.h5를 기본 Siamese 모델로 설정")
        else:
            # 첫 번째 h5 파일을 기본으로 설정
            h5_files = list(models_dir.glob("siamese_*.h5"))
            if h5_files:
                shutil.copy2(h5_files[0], models_dir / "siamese_original.h5")
                print(f"   🎯 {h5_files[0].name}을 기본 Siamese 모델로 설정")
    else:
        print(f"❌ Siamese 모델 폴더 없음: {siamese_source}")
    
    # 2. YOLOv5 모델 찾기 (.pt 파일)
    yolo_source = source_path / "crop_dognose_yoloV5"
    best_pt_files = []
    
    if yolo_source.exists():
        print(f"📂 YOLOv5 폴더 발견: {yolo_source}")
        
        # best.pt 파일들 검색
        for pt_file in yolo_source.rglob("best.pt"):
            best_pt_files.append(pt_file)
            print(f"   🎯 발견: {pt_file}")
        
        if best_pt_files:
            # 가장 최근 파일 선택 (또는 첫 번째)
            selected_pt = best_pt_files[0]
            target_pt = models_dir / "yolo_best.pt"
            shutil.copy2(selected_pt, target_pt)
            print(f"   ✅ 복사됨: {selected_pt} -> {target_pt}")
            success_count += 1
        else:
            print("   ❌ best.pt 파일을 찾을 수 없습니다.")
            # 대안으로 다른 .pt 파일들 검색
            pt_files = list(yolo_source.rglob("*.pt"))
            if pt_files:
                print("   🔍 다른 .pt 파일들:")
                for i, pt_file in enumerate(pt_files[:5]):  # 최대 5개만 표시
                    print(f"      {i}: {pt_file}")
                
                choice = input("   사용할 파일 번호를 입력하세요 (0): ").strip()
                try:
                    idx = int(choice) if choice else 0
                    selected_pt = pt_files[idx]
                    target_pt = models_dir / "yolo_best.pt"
                    shutil.copy2(selected_pt, target_pt)
                    print(f"   ✅ 복사됨: {selected_pt} -> {target_pt}")
                    success_count += 1
                except (ValueError, IndexError):
                    print("   ❌ 잘못된 선택입니다.")
    else:
        print(f"❌ YOLOv5 폴더 없음: {yolo_source}")
    
    # 3. 모델 정보 파일 생성
    info_file = models_dir / "model_info.txt"
    with open(info_file, 'w', encoding='utf-8') as f:
        f.write("=== Dog Nose AI Service Models ===\n\n")
        f.write(f"설치된 모델 수: {success_count}\n\n")
        
        # 설치된 파일들 나열
        f.write("설치된 파일들:\n")
        for model_file in models_dir.glob("*"):
            if model_file.is_file() and model_file.name != "model_info.txt":
                size_mb = model_file.stat().st_size / (1024 * 1024)
                f.write(f"- {model_file.name} ({size_mb:.1f}MB)\n")
        
        f.write("\n사용법:\n")
        f.write("1. YOLOv5 (yolo_best.pt): 강아지 얼굴에서 코 영역 탐지\n")
        f.write("2. Siamese (siamese_original.h5): 비문 패턴 비교 및 인식\n")
    
    print(f"\n📊 요약:")
    print(f"   설치된 모델: {success_count}개")
    print(f"   모델 저장 위치: {models_dir.absolute()}")
    print(f"   정보 파일: {info_file}")
    
    # 설치된 파일들 확인
    print(f"\n📁 설치된 파일들:")
    for model_file in models_dir.glob("*"):
        if model_file.is_file():
            size_mb = model_file.stat().st_size / (1024 * 1024)
            print(f"   📄 {model_file.name} ({size_mb:.1f}MB)")
    
    if success_count >= 2:
        print(f"\n🎉 모델 설정 완료! 이제 Docker 서비스를 시작할 수 있습니다.")
        print(f"   다음 단계: .\run.ps1 start 또는 run.bat start")
        return True
    else:
        print(f"\n⚠️ 일부 모델만 설치되었습니다. Docker 내에서 추가 설정이 필요할 수 있습니다.")
        return False

if __name__ == "__main__":
    print("🐕 강아지 비문 인식 AI - 간단 모델 설정")
    print("=" * 50)
    success = simple_model_setup()
    sys.exit(0 if success else 1) 