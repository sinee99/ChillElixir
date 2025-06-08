import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime
import logging
from config import Config

class FirebaseManager:
    def __init__(self):
        """Firebase 초기화"""
        try:
            # Firebase 앱이 이미 초기화되어 있는지 확인
            firebase_admin.get_app()
        except ValueError:
            # Firebase 앱이 초기화되지 않았다면 초기화
            cred = credentials.Certificate(Config.FIREBASE_CREDENTIALS_PATH)
            firebase_admin.initialize_app(cred, {
                'databaseURL': Config.FIREBASE_DATABASE_URL
            })
        
        self.db = firestore.client()
        self.collection_name = 'dog_analysis'
        
    def save_analysis_result(self, image_filename: str, predictions: dict, confidence_scores: dict):
        """
        분석 결과를 Firebase에 저장
        
        Args:
            image_filename (str): 이미지 파일명
            predictions (dict): 예측 결과 {class_id: class_name}
            confidence_scores (dict): 신뢰도 점수 {class_id: confidence}
        
        Returns:
            str: 저장된 문서 ID
        """
        try:
            # 최고 신뢰도를 가진 클래스 찾기
            best_class_id = max(confidence_scores.keys(), key=lambda x: confidence_scores[x])
            best_prediction = predictions[best_class_id]
            best_confidence = confidence_scores[best_class_id]
            
            # 저장할 데이터 구성
            analysis_data = {
                'image_filename': image_filename,
                'predicted_breed': best_prediction,
                'confidence_score': float(best_confidence),
                'all_predictions': predictions,
                'all_confidence_scores': {str(k): float(v) for k, v in confidence_scores.items()},
                'analysis_timestamp': datetime.now(),
                'model_used': 'YOLOv8_DogCharacteristic'
            }
            
            # Firestore에 저장
            doc_ref = self.db.collection(self.collection_name).add(analysis_data)
            doc_id = doc_ref[1].id
            
            logging.info(f"분석 결과가 Firebase에 저장되었습니다. 문서 ID: {doc_id}")
            return doc_id
            
        except Exception as e:
            logging.error(f"Firebase 저장 중 오류 발생: {str(e)}")
            raise e
    
    def get_analysis_by_id(self, doc_id: str):
        """
        문서 ID로 분석 결과 조회
        
        Args:
            doc_id (str): 문서 ID
            
        Returns:
            dict: 분석 결과 데이터
        """
        try:
            doc = self.db.collection(self.collection_name).document(doc_id).get()
            if doc.exists:
                return doc.to_dict()
            else:
                return None
        except Exception as e:
            logging.error(f"Firebase 조회 중 오류 발생: {str(e)}")
            raise e
    
    def get_recent_analyses(self, limit: int = 10):
        """
        최근 분석 결과들을 조회
        
        Args:
            limit (int): 조회할 개수
            
        Returns:
            list: 분석 결과 리스트
        """
        try:
            docs = self.db.collection(self.collection_name)\
                         .order_by('analysis_timestamp', direction=firestore.Query.DESCENDING)\
                         .limit(limit)\
                         .stream()
            
            results = []
            for doc in docs:
                result = doc.to_dict()
                result['doc_id'] = doc.id
                results.append(result)
            
            return results
        except Exception as e:
            logging.error(f"Firebase 조회 중 오류 발생: {str(e)}")
            raise e 