from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
import os
import uuid
import logging
from datetime import datetime
from dog_analyzer import DogAnalyzer
from firebase_manager import FirebaseManager
from config import Config
import tempfile
import aiofiles

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('dog_analysis.log'),
        logging.StreamHandler()
    ]
)

app = FastAPI(
    title="강아지 특성 분석 API",
    description="YOLOv8 모델을 사용한 강아지 품종 분석 서비스",
    version="1.0.0"
)

# 전역 객체 초기화
dog_analyzer = None
firebase_manager = None

@app.on_event("startup")
async def startup_event():
    """애플리케이션 시작 시 초기화"""
    global dog_analyzer, firebase_manager
    try:
        logging.info("강아지 분석 서비스를 시작합니다...")
        
        # 모델 로드
        dog_analyzer = DogAnalyzer()
        
        # Firebase 초기화
        firebase_manager = FirebaseManager()
        
        logging.info("서비스 초기화가 완료되었습니다.")
    except Exception as e:
        logging.error(f"서비스 초기화 중 오류 발생: {str(e)}")
        raise e

async def process_and_save_analysis(temp_file_path: str, original_filename: str):
    """
    백그라운드에서 이미지 분석 및 Firebase 저장 처리
    
    Args:
        temp_file_path (str): 임시 파일 경로
        original_filename (str): 원본 파일명
    """
    try:
        # 이미지 분석
        predictions, confidence_scores, raw_results = dog_analyzer.analyze_dog_image(temp_file_path)
        
        if predictions:
            # Firebase에 결과 저장
            doc_id = firebase_manager.save_analysis_result(
                original_filename, 
                predictions, 
                confidence_scores
            )
            logging.info(f"분석 결과 저장 완료 - Document ID: {doc_id}")
        
    except Exception as e:
        logging.error(f"백그라운드 분석 처리 중 오류: {str(e)}")
    finally:
        # 임시 파일 삭제
        try:
            os.unlink(temp_file_path)
        except:
            pass

@app.post("/analyze", response_model=dict)
async def analyze_dog_image(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...)
):
    """
    강아지 이미지 분석 엔드포인트
    
    Args:
        file: 업로드된 이미지 파일
        
    Returns:
        dict: 분석 결과
    """
    try:
        # 파일 형식 검증
        if not file.filename:
            raise HTTPException(status_code=400, detail="파일명이 없습니다.")
        
        file_ext = os.path.splitext(file.filename)[1].lower()
        if file_ext not in Config.ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400, 
                detail=f"지원되지 않는 파일 형식입니다. 지원 형식: {Config.ALLOWED_EXTENSIONS}"
            )
        
        # 파일 크기 검증
        contents = await file.read()
        if len(contents) > Config.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400, 
                detail=f"파일 크기가 너무 큽니다. 최대 크기: {Config.MAX_FILE_SIZE / (1024*1024):.1f}MB"
            )
        
        # 임시 파일로 저장
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=file_ext)
        temp_file_path = temp_file.name
        
        async with aiofiles.open(temp_file_path, 'wb') as f:
            await f.write(contents)
        
        # 이미지 유효성 검증
        if not dog_analyzer.validate_image_file(temp_file_path):
            os.unlink(temp_file_path)
            raise HTTPException(status_code=400, detail="유효하지 않은 이미지 파일입니다.")
        
        # 즉시 분석 수행
        predictions, confidence_scores, raw_results = dog_analyzer.analyze_dog_image(temp_file_path)
        
        if not predictions:
            os.unlink(temp_file_path)
            return {
                "success": False,
                "message": "이미지에서 강아지를 감지하지 못했습니다.",
                "filename": file.filename,
                "timestamp": datetime.now().isoformat()
            }
        
        # 최고 예측 결과
        best_class_id = max(confidence_scores.keys(), key=lambda x: confidence_scores[x])
        best_prediction = predictions[best_class_id]
        best_confidence = confidence_scores[best_class_id]
        
        # 백그라운드에서 Firebase 저장 처리
        background_tasks.add_task(
            process_and_save_analysis, 
            temp_file_path, 
            file.filename
        )
        
        return {
            "success": True,
            "filename": file.filename,
            "predicted_breed": best_prediction,
            "confidence_score": round(float(best_confidence), 3),
            "all_predictions": {str(k): v for k, v in predictions.items()},
            "all_confidence_scores": {str(k): round(float(v), 3) for k, v in confidence_scores.items()},
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"이미지 분석 중 오류 발생: {str(e)}")
        raise HTTPException(status_code=500, detail=f"서버 내부 오류: {str(e)}")

@app.get("/model-info", response_model=dict)
async def get_model_info():
    """모델 정보 조회"""
    try:
        return dog_analyzer.get_model_info()
    except Exception as e:
        logging.error(f"모델 정보 조회 중 오류: {str(e)}")
        raise HTTPException(status_code=500, detail=f"서버 내부 오류: {str(e)}")

@app.get("/recent-analyses", response_model=dict)
async def get_recent_analyses(limit: int = 10):
    """최근 분석 결과 조회"""
    try:
        results = firebase_manager.get_recent_analyses(limit)
        return {
            "success": True,
            "count": len(results),
            "analyses": results
        }
    except Exception as e:
        logging.error(f"최근 분석 결과 조회 중 오류: {str(e)}")
        raise HTTPException(status_code=500, detail=f"서버 내부 오류: {str(e)}")

@app.get("/analysis/{doc_id}", response_model=dict)
async def get_analysis_by_id(doc_id: str):
    """특정 분석 결과 조회"""
    try:
        result = firebase_manager.get_analysis_by_id(doc_id)
        if result is None:
            raise HTTPException(status_code=404, detail="분석 결과를 찾을 수 없습니다.")
        
        return {
            "success": True,
            "analysis": result
        }
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"분석 결과 조회 중 오류: {str(e)}")
        raise HTTPException(status_code=500, detail=f"서버 내부 오류: {str(e)}")

@app.get("/health", response_model=dict)
async def health_check():
    """헬스 체크"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "Dog Analysis API"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "api:app",
        host=Config.API_HOST,
        port=Config.API_PORT,
        reload=False
    ) 