#!/usr/bin/env python3
"""
모델 변환 및 준비 스크립트
기존 프로젝트의 YOLOv5와 Siamese 모델을 도커 서비스용으로 준비합니다.
"""

import os
import shutil
import torch
import tensorflow as tf
from pathlib import Path
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ModelConverter:
    def __init__(self, source_project_path, target_models_path):
        """
        Args:
            source_project_path: 원본 프로젝트 경로
            target_models_path: 도커 서비스용 모델 저장 경로
        """
        self.source_path = Path(source_project_path)
        self.target_path = Path(target_models_path)
        self.target_path.mkdir(parents=True, exist_ok=True)
    
    def copy_yolo_model(self):
        """YOLOv5 모델 파일 복사"""
        try:
            # YOLOv5 best.pt 파일 찾기
            yolo_source = self.source_path / "crop_dognose_yoloV5" / "runs" / "train"
            
            # 가능한 weight 파일 경로들
            possible_paths = [
                yolo_source / "dog_nose_yolov5n_14" / "weights" / "best.pt",
                yolo_source / "exp" / "weights" / "best.pt",
                yolo_source / "exp2" / "weights" / "best.pt",
            ]
            
            yolo_model_path = None
            for path in possible_paths:
                if path.exists():
                    yolo_model_path = path
                    break
            
            if yolo_model_path and yolo_model_path.exists():
                target_yolo = self.target_path / "yolo_best.pt"
                shutil.copy2(yolo_model_path, target_yolo)
                logger.info(f"YOLOv5 model copied: {yolo_model_path} -> {target_yolo}")
                return True
            else:
                logger.warning("YOLOv5 model not found. Searching in all subdirectories...")
                
                # 전체 디렉토리에서 best.pt 파일 검색
                for pt_file in yolo_source.rglob("best.pt"):
                    target_yolo = self.target_path / "yolo_best.pt"
                    shutil.copy2(pt_file, target_yolo)
                    logger.info(f"YOLOv5 model found and copied: {pt_file} -> {target_yolo}")
                    return True
                
                logger.error("YOLOv5 model file not found")
                return False
                
        except Exception as e:
            logger.error(f"Error copying YOLOv5 model: {str(e)}")
            return False
    
    def copy_siamese_models(self):
        """Siamese Neural Network 모델 파일들 복사"""
        try:
            siamese_source = self.source_path / "dognose_recognition" / "model"
            
            if not siamese_source.exists():
                logger.error(f"Siamese model directory not found: {siamese_source}")
                return False
            
            # 모든 h5 파일 복사
            copied_models = []
            for h5_file in siamese_source.glob("*.h5"):
                target_file = self.target_path / f"siamese_{h5_file.name}"
                shutil.copy2(h5_file, target_file)
                copied_models.append(target_file.name)
                logger.info(f"Siamese model copied: {h5_file} -> {target_file}")
            
            if copied_models:
                # original.h5를 기본 모델로 설정
                if "siamese_original.h5" in copied_models:
                    logger.info("Using original.h5 as default Siamese model")
                else:
                    # 첫 번째 모델을 기본으로 설정
                    first_model = self.target_path / copied_models[0]
                    default_model = self.target_path / "siamese_original.h5"
                    shutil.copy2(first_model, default_model)
                    logger.info(f"Using {copied_models[0]} as default Siamese model")
                
                return True
            else:
                logger.error("No Siamese model files found")
                return False
                
        except Exception as e:
            logger.error(f"Error copying Siamese models: {str(e)}")
            return False
    
    def validate_models(self):
        """모델 파일 유효성 검사"""
        try:
            results = {}
            
            # YOLOv5 모델 검사
            yolo_path = self.target_path / "yolo_best.pt"
            if yolo_path.exists():
                try:
                    # PyTorch 모델 로드 테스트
                    model = torch.load(yolo_path, map_location='cpu')
                    results['yolo'] = True
                    logger.info("YOLOv5 model validation: PASSED")
                except Exception as e:
                    logger.error(f"YOLOv5 model validation failed: {str(e)}")
                    results['yolo'] = False
            else:
                results['yolo'] = False
                logger.error("YOLOv5 model file not found")
            
            # Siamese 모델 검사
            siamese_path = self.target_path / "siamese_original.h5"
            if siamese_path.exists():
                try:
                    # TensorFlow 모델 로드 테스트
                    model = tf.keras.models.load_model(siamese_path)
                    results['siamese'] = True
                    logger.info("Siamese model validation: PASSED")
                except Exception as e:
                    logger.error(f"Siamese model validation failed: {str(e)}")
                    results['siamese'] = False
            else:
                results['siamese'] = False
                logger.error("Siamese model file not found")
            
            return results
            
        except Exception as e:
            logger.error(f"Error validating models: {str(e)}")
            return {'yolo': False, 'siamese': False}
    
    def create_model_info(self):
        """모델 정보 파일 생성"""
        try:
            model_info = {
                'yolo_model': 'yolo_best.pt',
                'siamese_model': 'siamese_original.h5',
                'input_size': {
                    'yolo': [640, 640],
                    'siamese': [96, 96]
                },
                'preprocessing': {
                    'yolo': 'RGB, normalized to 0-1',
                    'siamese': 'Grayscale, normalized to 0-1'
                }
            }
            
            info_file = self.target_path / "model_info.txt"
            with open(info_file, 'w', encoding='utf-8') as f:
                f.write("=== Dog Nose AI Service Models ===\n\n")
                f.write(f"YOLOv5 Model: {model_info['yolo_model']}\n")
                f.write(f"- Input Size: {model_info['input_size']['yolo']}\n")
                f.write(f"- Preprocessing: {model_info['preprocessing']['yolo']}\n\n")
                f.write(f"Siamese Model: {model_info['siamese_model']}\n")
                f.write(f"- Input Size: {model_info['input_size']['siamese']}\n")
                f.write(f"- Preprocessing: {model_info['preprocessing']['siamese']}\n\n")
                f.write("Usage:\n")
                f.write("1. YOLOv5: Detect and crop dog nose from full image\n")
                f.write("2. Siamese: Compare nose prints for identity matching\n")
            
            logger.info(f"Model info created: {info_file}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating model info: {str(e)}")
            return False
    
    def convert_all(self):
        """전체 변환 프로세스 실행"""
        logger.info("Starting model conversion process...")
        
        results = {}
        results['yolo_copied'] = self.copy_yolo_model()
        results['siamese_copied'] = self.copy_siamese_models()
        results['validation'] = self.validate_models()
        results['info_created'] = self.create_model_info()
        
        # 결과 요약
        logger.info("=== Model Conversion Summary ===")
        logger.info(f"YOLOv5 copied: {'✓' if results['yolo_copied'] else '✗'}")
        logger.info(f"Siamese copied: {'✓' if results['siamese_copied'] else '✗'}")
        logger.info(f"YOLOv5 validation: {'✓' if results['validation']['yolo'] else '✗'}")
        logger.info(f"Siamese validation: {'✓' if results['validation']['siamese'] else '✗'}")
        logger.info(f"Model info created: {'✓' if results['info_created'] else '✗'}")
        
        success = (results['yolo_copied'] and results['siamese_copied'] and
                  results['validation']['yolo'] and results['validation']['siamese'])
        
        if success:
            logger.info("✅ Model conversion completed successfully!")
        else:
            logger.warning("⚠️ Model conversion completed with some issues")
        
        return results

def main():
    """메인 실행 함수"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Convert models for Docker service')
    parser.add_argument('--source', required=True, 
                       help='Source project path (dognose_recognition_management_service-main)')
    parser.add_argument('--target', default='./models',
                       help='Target models directory (default: ./models)')
    
    args = parser.parse_args()
    
    converter = ModelConverter(args.source, args.target)
    results = converter.convert_all()
    
    return 0 if all(results['validation'].values()) else 1

if __name__ == "__main__":
    exit(main()) 