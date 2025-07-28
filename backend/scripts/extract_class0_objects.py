import os
import cv2
import shutil

def parse_yolo_labels(label_file_path):
    class0_objects = []

    if not os.path.exists(label_file_path):
        print(f"[ERROR] 라벨 파일이 존재하지 않습니다: {label_file_path}")
        return []

    with open(label_file_path, 'r') as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) >= 5 and int(parts[0]) == 0:
                class0_objects.append(tuple(map(float, parts[1:5])))

    print(f"[INFO] 클래스 0 객체 {len(class0_objects)}개 발견")
    return class0_objects

def yolo_to_pixel_coords(x_center, y_center, width, height, img_width, img_height):
    center_x = x_center * img_width
    center_y = y_center * img_height
    box_width = width * img_width
    box_height = height * img_height

    x1 = int(center_x - box_width / 2)
    y1 = int(center_y - box_height / 2)
    x2 = int(center_x + box_width / 2)
    y2 = int(center_y + box_height / 2)

    return (x1, y1, x2, y2)

def equi_to_original_coords(equi_x, equi_y, equi_width, equi_height, orig_width, orig_height):
    new_h = orig_width // 2
    pad = (new_h - orig_height) // 2
    orig_x = equi_x
    orig_y = equi_y - pad
    orig_y = max(0, orig_y)
    return orig_x, orig_y

def crop_and_save_objects_with_reverse_transform(image_path, class0_objects, output_dir, equi_image_path):
    if not os.path.exists(image_path) or not os.path.exists(equi_image_path):
        print("[ERROR] 이미지 파일이 존재하지 않습니다.")
        return

    orig_image = cv2.imread(image_path)
    equi_image = cv2.imread(equi_image_path)
    if orig_image is None or equi_image is None:
        print("[ERROR] 이미지를 읽을 수 없습니다.")
        return

    orig_h, orig_w = orig_image.shape[:2]
    equi_h, equi_w = equi_image.shape[:2]

    new_h = orig_w // 2
    pad = (new_h - orig_h) // 2
    print(f"[INFO] 변환 파라미터: new_h={new_h}, pad={pad}")

    os.makedirs(output_dir, exist_ok=True)

    for i, (x_c, y_c, w, h) in enumerate(class0_objects):
        x1, y1, x2, y2 = yolo_to_pixel_coords(x_c, y_c, w, h, equi_w, equi_h)
        ox1, oy1 = equi_to_original_coords(x1, y1, equi_w, equi_h, orig_w, orig_h)
        ox2, oy2 = equi_to_original_coords(x2, y2, equi_w, equi_h, orig_w, orig_h)

        ox1 = max(0, int(ox1))
        oy1 = max(0, int(oy1))
        ox2 = min(orig_w, int(ox2))
        oy2 = min(orig_h, int(oy2))

        if ox2 > ox1 and oy2 > oy1:
            crop = orig_image[oy1:oy2, ox1:ox2]

            if crop.size == 0:
                print(f"[SKIP] 잘림 결과 이미지가 비어 있습니다. index: {i}")
                continue

            resized_crop = cv2.resize(crop, (200, 300), interpolation=cv2.INTER_AREA)
            out_path = os.path.join(output_dir, f"class0_object_{i+1}_from_original.jpg")
            cv2.imwrite(out_path, resized_crop)
            print(f"[SAVED] {out_path}")
        else:
            print(f"[WARNING] 잘못된 바운딩 박스: {ox1},{oy1},{ox2},{oy2}")

def move_images_to_session_dir(output_dir, session_dir, session_id):
    target_dir = os.path.join("frontend", "public", "images", "거실문", session_id)
    os.makedirs(target_dir, exist_ok=True)

    moved_files = []
    for i, fname in enumerate(sorted(os.listdir(output_dir))):
        if fname.endswith("_from_original.jpg"):
            src = os.path.join(output_dir, fname)
            dst_name = f"문{i+1}.jpg"
            dst = os.path.join(target_dir, dst_name)
            shutil.move(src, dst)
            moved_files.append(dst_name)
            print(f"[MOVE] {fname} → 거실문/{session_id}/{dst_name}")

    return moved_files

def run_object_extraction(session_dir):
    label_file = os.path.join(session_dir, "yolo_output", "labels", "result_equi.txt")
    orig_img = os.path.join(session_dir, "result_image.jpg")
    equi_img = os.path.join(session_dir, "result_equi.jpg")
    output_dir = os.path.join(session_dir, "extracted_class0_objects")

    print(f"[INFO] 세션 디렉토리: {session_dir}")
    session_id = os.path.basename(os.path.dirname(session_dir))

    objects = parse_yolo_labels(label_file)
    if not objects:
        return {"success": False, "message": "클래스 0 객체 없음", "files": []}

    crop_and_save_objects_with_reverse_transform(orig_img, objects, output_dir, equi_img)
    moved = move_images_to_session_dir(output_dir, session_dir, session_id)

    return {
        "success": True,
        "message": f"{len(moved)}개 객체 저장 완료",
        "files": moved,
        "output_path": os.path.join("frontend", "public", "images", "거실문", session_id)
    }