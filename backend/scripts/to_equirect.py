import os
import cv2
import json
import shutil

SRC = os.environ.get("PIPELINE_STITCH_RESULT", "./viewer/result_image.jpg")
DST = os.environ.get("PIPELINE_EQUI_RESULT", "./viewer/result_equi.jpg")

img = cv2.imread(SRC)
if img is None:
    print(f"[ERROR] 이미지 로딩 실패: {SRC}")
    exit(1)

h, w = img.shape[:2]
aspect_ratio = w / h
target_ratio = 2.0
new_h = int(w / target_ratio)
pad = (new_h - h) // 2

# ✅ 음수 padding 방지 및 안전 처리
if aspect_ratio >= target_ratio or pad <= 0:
    print(f"[INFO] 이미지가 이미 2:1 이상입니다. 그대로 저장.")
    shutil.copy(SRC, DST)
else:
    print(f"[INFO] 상하단 padding 추가 → 총 padding: {new_h - h}px")
    padded_img = cv2.copyMakeBorder(
        img,
        top=pad,
        bottom=new_h - h - pad,
        left=0,
        right=0,
        borderType=cv2.BORDER_CONSTANT,
        value=(0, 0, 0)
    )
    cv2.imwrite(DST, padded_img)
    print('[√] 2:1 비율 맞춤 완료 →', DST)

# JSON 생성
result_json_path = DST.replace(".jpg", ".json")
result_data = {
    "message": "no objects detected",
    "objects": []
}

with open(result_json_path, "w") as f:
    json.dump(result_data, f, indent=2)

print(f"[√] JSON 생성 완료 → {result_json_path}")