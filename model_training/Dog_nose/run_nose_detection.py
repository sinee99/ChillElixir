#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import os
from pathlib import Path
from nose import DogNosePreprocessorYOLOv5

def main():
    parser = argparse.ArgumentParser(description='🐕 강아지 코 탐지 및 전처리 도구')
    parser.add_argument('--input', '-i', type=str, required=True,
                        help='입력 이미지 폴더 경로')
    parser.add_argument('--output', '-o', type=str, default='processed_noses',
                        help='출력 폴더 경로 (기본값: processed_noses)')
    parser.add_argument('--model', '-m', type=str, default='model_training/Dog_nose/best.pt',
                        help='YOLOv5 모델 경로 (기본값: model_training/Dog_nose/best.pt)')
    parser.add_argument('--confidence', '-c', type=float, default=0.5,
                        help='탐지 신뢰도 임계값 (기본값: 0.5)')
    parser.add_argument('--size', '-s', type=int, nargs=2, default=[224, 224],
                        help='출력 이미지 크기 (기본값: 224 224)')
    
    args = parser.parse_args()
    
    # 입력 폴더 확인
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"❌ 입력 폴더가 존재하지 않습니다: {input_path}")
        return
    
    # 출력 폴더 생성
    output_path = Path(args.output)
    output_path.mkdir(parents=True, exist_ok=True)
    
    print("🐕 강아지 코 탐지 시작!")
    print("=" * 50)
    print(f"📁 입력 폴더: {input_path}")
    print(f"📁 출력 폴더: {output_path}")
    print(f"🤖 모델 경로: {args.model}")
    print(f"🎯 신뢰도 임계값: {args.confidence}")
    print(f"📏 출력 크기: {args.size[0]}x{args.size[1]}")
    print("=" * 50)
    
    # 전처리기 초기화
    preprocessor = DogNosePreprocessorYOLOv5(
        model_path=args.model,
        target_size=tuple(args.size),
        confidence_threshold=args.confidence,
        nose_class_id=0
    )
    
    # 이미지 처리 실행
    preprocessor.process_directory(args.input, args.output)
    
    print("\n✅ 모든 작업이 완료되었습니다!")

if __name__ == "__main__":
    main() 