from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import subprocess
import traceback
from werkzeug.utils import secure_filename
from datetime import datetime
import uuid

app = Flask(__name__)
CORS(app)

# 업로드 루트 디렉토리
BACKEND_UPLOAD_DIR = os.path.join(os.path.dirname(__file__), 'uploads')
os.makedirs(BACKEND_UPLOAD_DIR, exist_ok=True)

@app.route('/api/upload', methods=['POST'])
def upload_and_process():
    try:
        file = request.files.get('file')
        room_type = request.form.get('roomType', 'room')
        if not file:
            return jsonify(success=False, error='파일이 없습니다.'), 400

        # 1. 날짜 기반 세션/방 폴더 생성
        date_str = datetime.now().strftime('%Y%m%d')
        session_id = f"session_{date_str}_{uuid.uuid4().hex[:6]}"
        room_dir = os.path.join(BACKEND_UPLOAD_DIR, session_id, room_type)
        os.makedirs(room_dir, exist_ok=True)

        # 2. 파일 저장
        filename = secure_filename(file.filename)
        video_path = os.path.join(room_dir, filename)
        file.save(video_path)

        print(f"[UPLOAD] 저장된 비디오: {video_path}")

        # 3. 결과 디렉토리 등 경로 계산
        frame_dir_abs = os.path.abspath(os.path.join(room_dir, 'frames'))
        stitched_path = os.path.abspath(os.path.join(room_dir, 'result_image.jpg'))
        equi_path = stitched_path.replace('result_image.jpg', 'result_equi.jpg')
        yolo_out = os.path.abspath(os.path.join(room_dir, 'yolo_output'))

        # 4. 환경변수 dict 생성
        env = os.environ.copy()
        env["PIPELINE_INPUT_VIDEO"] = os.path.abspath(video_path)
        env["PIPELINE_FRAME_DIR"] = frame_dir_abs
        env["PIPELINE_STITCH_RESULT"] = stitched_path
        env["PIPELINE_EQUI_RESULT"] = equi_path
        env["YOLO_MODEL_PATH"] = os.path.abspath("best_250723.pt")
        env["YOLO_OUTPUT_DIR"] = yolo_out
        env["FRAME_INTERVAL"] = "30"

        # 5. 파이프라인 실행
        pipeline_path = os.path.abspath("backend/run_pipeline.py")
        print(f"[RUN] 파이프라인 시작: {pipeline_path}")
        result = subprocess.run(
            ['python', pipeline_path],
            env=env,
            capture_output=True,
            text=True,
            check=True
        )
        print("[PIPELINE] 완료:", result.stdout)

        return jsonify(success=True, message="파이프라인 완료", session_id=session_id)

    except subprocess.CalledProcessError as e:
        print("[❌ 파이프라인 실패]")
        print("stdout:\n", e.stdout)
        print("stderr:\n", e.stderr)
        return jsonify(success=False, error='파이프라인 실패', stdout=e.stdout, stderr=e.stderr), 500

    except Exception as e:
        traceback.print_exc()
        return jsonify(success=False, error='예외 발생', message=str(e)), 500

@app.route('/uploads/<path:filename>')
def serve_file(filename):
    return send_from_directory(BACKEND_UPLOAD_DIR, filename)

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5050)