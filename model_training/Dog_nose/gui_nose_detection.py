#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
from pathlib import Path
import sys
import os

# 현재 디렉토리를 파이썬 경로에 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from nose import DogNosePreprocessorYOLOv5
except ImportError as e:
    print(f"nose.py 모듈을 불러올 수 없습니다: {e}")
    sys.exit(1)

class NoseDetectionGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("🐕 강아지 코 탐지 도구")
        self.root.geometry("600x500")
        
        # 변수
        self.input_folder = tk.StringVar()
        self.output_folder = tk.StringVar(value="processed_noses")
        self.confidence = tk.DoubleVar(value=0.5)
        self.image_size = tk.IntVar(value=224)
        
        self.preprocessor = None
        self.processing = False
        
        self.setup_ui()
    
    def setup_ui(self):
        """UI 구성"""
        # 메인 프레임
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 제목
        title_label = ttk.Label(main_frame, text="🐕 강아지 코 탐지 및 전처리 도구", 
                               font=('Arial', 16, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # 입력 폴더 선택
        input_frame = ttk.LabelFrame(main_frame, text="📁 입력 설정")
        input_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(input_frame, text="강아지 이미지 폴더:").pack(anchor=tk.W, padx=5, pady=5)
        
        input_path_frame = ttk.Frame(input_frame)
        input_path_frame.pack(fill=tk.X, padx=5, pady=(0, 10))
        
        ttk.Entry(input_path_frame, textvariable=self.input_folder, 
                 font=('Arial', 9)).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(input_path_frame, text="📁 선택", 
                  command=self.select_input_folder).pack(side=tk.RIGHT, padx=(5, 0))
        
        # 출력 폴더 설정
        ttk.Label(input_frame, text="결과 저장 폴더:").pack(anchor=tk.W, padx=5)
        
        output_path_frame = ttk.Frame(input_frame)
        output_path_frame.pack(fill=tk.X, padx=5, pady=(0, 10))
        
        ttk.Entry(output_path_frame, textvariable=self.output_folder,
                 font=('Arial', 9)).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(output_path_frame, text="📁 선택", 
                  command=self.select_output_folder).pack(side=tk.RIGHT, padx=(5, 0))
        
        # 고급 설정
        settings_frame = ttk.LabelFrame(main_frame, text="⚙️ 고급 설정")
        settings_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 신뢰도 설정
        conf_frame = ttk.Frame(settings_frame)
        conf_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(conf_frame, text="탐지 신뢰도:").pack(side=tk.LEFT)
        conf_scale = ttk.Scale(conf_frame, from_=0.1, to=0.9, 
                              variable=self.confidence, orient=tk.HORIZONTAL)
        conf_scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(10, 5))
        
        self.conf_label = ttk.Label(conf_frame, text="0.5")
        self.conf_label.pack(side=tk.RIGHT)
        
        conf_scale.configure(command=self.update_confidence_label)
        
        # 이미지 크기 설정
        size_frame = ttk.Frame(settings_frame)
        size_frame.pack(fill=tk.X, padx=5, pady=(0, 10))
        
        ttk.Label(size_frame, text="출력 이미지 크기:").pack(side=tk.LEFT)
        
        size_combo = ttk.Combobox(size_frame, textvariable=self.image_size,
                                 values=[128, 224, 256, 512], state="readonly", width=10)
        size_combo.pack(side=tk.RIGHT)
        size_combo.set(224)
        
        # 실행 버튼
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.start_button = ttk.Button(button_frame, text="🚀 코 탐지 시작", 
                                      command=self.start_processing)
        self.start_button.pack(side=tk.LEFT, padx=(0, 5))
        
        self.stop_button = ttk.Button(button_frame, text="⏹️ 중지", 
                                     command=self.stop_processing, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT)
        
        # 상태 표시
        self.status_var = tk.StringVar(value="준비됨")
        status_label = ttk.Label(main_frame, textvariable=self.status_var, 
                                font=('Arial', 10, 'bold'))
        status_label.pack(pady=(0, 5))
        
        # 진행률 표시
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.pack(fill=tk.X, pady=(0, 10))
        
        # 로그 출력
        log_frame = ttk.LabelFrame(main_frame, text="📄 처리 로그")
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=8, 
                                                 font=('Consolas', 9))
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 초기 로그 메시지
        self.log("강아지 코 탐지 도구가 준비되었습니다.")
        self.log("1. 강아지 이미지가 들어있는 폴더를 선택하세요.")
        self.log("2. 필요시 설정을 조정하세요.")
        self.log("3. '코 탐지 시작' 버튼을 클릭하세요.")
    
    def update_confidence_label(self, value):
        """신뢰도 라벨 업데이트"""
        self.conf_label.config(text=f"{float(value):.2f}")
    
    def select_input_folder(self):
        """입력 폴더 선택"""
        folder = filedialog.askdirectory(title="강아지 이미지 폴더를 선택하세요")
        if folder:
            self.input_folder.set(folder)
            self.log(f"입력 폴더 선택: {folder}")
            
            # 이미지 파일 개수 확인
            input_path = Path(folder)
            image_files = list(input_path.glob("*.jpg")) + list(input_path.glob("*.jpeg")) + list(input_path.glob("*.png"))
            self.log(f"발견된 이미지 파일: {len(image_files)}개")
    
    def select_output_folder(self):
        """출력 폴더 선택"""
        folder = filedialog.askdirectory(title="결과 저장 폴더를 선택하세요")
        if folder:
            self.output_folder.set(folder)
            self.log(f"출력 폴더 선택: {folder}")
    
    def log(self, message):
        """로그 메시지 출력"""
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)
        self.root.update()
    
    def start_processing(self):
        """처리 시작"""
        if not self.input_folder.get():
            messagebox.showerror("오류", "입력 폴더를 선택해주세요!")
            return
        
        if not Path(self.input_folder.get()).exists():
            messagebox.showerror("오류", "선택한 입력 폴더가 존재하지 않습니다!")
            return
        
        # UI 상태 변경
        self.processing = True
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.status_var.set("처리 중...")
        self.progress.start()
        
        # 별도 스레드에서 처리 실행
        processing_thread = threading.Thread(target=self.process_images)
        processing_thread.daemon = True
        processing_thread.start()
    
    def stop_processing(self):
        """처리 중지"""
        self.processing = False
        self.status_var.set("중지됨")
        self.reset_ui()
    
    def reset_ui(self):
        """UI 상태 초기화"""
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.progress.stop()
    
    def process_images(self):
        """이미지 처리 (별도 스레드에서 실행)"""
        try:
            # 출력 폴더 생성
            output_path = Path(self.output_folder.get())
            output_path.mkdir(parents=True, exist_ok=True)
            
            self.log("=" * 50)
            self.log("🤖 모델 로딩 중...")
            
            # 전처리기 초기화
            self.preprocessor = DogNosePreprocessorYOLOv5(
                model_path='model_training/Dog_nose/best.pt',
                target_size=(self.image_size.get(), self.image_size.get()),
                confidence_threshold=self.confidence.get(),
                nose_class_id=0
            )
            
            self.log("✅ 모델 로드 완료!")
            self.log("🔍 이미지 처리 시작...")
            
            # 이미지 처리 실행
            self.preprocessor.process_directory(
                self.input_folder.get(), 
                self.output_folder.get()
            )
            
            if self.processing:  # 중지되지 않았다면
                self.status_var.set("완료!")
                self.log("✅ 모든 작업이 완료되었습니다!")
                self.log(f"📁 결과는 {output_path} 폴더에서 확인하세요.")
                
                messagebox.showinfo("완료", 
                                   f"코 탐지 작업이 완료되었습니다!\n\n"
                                   f"결과는 다음 폴더에서 확인하세요:\n{output_path}")
            
        except Exception as e:
            self.log(f"❌ 오류 발생: {e}")
            messagebox.showerror("오류", f"처리 중 오류가 발생했습니다:\n{e}")
            self.status_var.set("오류 발생")
        
        finally:
            self.processing = False
            self.reset_ui()

def main():
    root = tk.Tk()
    app = NoseDetectionGUI(root)
    
    # 종료 시 확인
    def on_closing():
        if app.processing:
            if messagebox.askokcancel("종료", "현재 처리 중입니다. 정말 종료하시겠습니까?"):
                app.processing = False
                root.destroy()
        else:
            root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()

if __name__ == "__main__":
    main() 