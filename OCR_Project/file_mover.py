#file_mover.py
import os
import shutil

ARCHIVE_FOLDERS = {

    "八里":    r"\\Dabs-nas2\新公用區\公文掃描檔\115\八里",

    "五股":    r"\\Dabs-nas2\新公用區\公文掃描檔\115\五股",

    "林口":    r"\\Dabs-nas2\新公用區\公文掃描檔\115\林口",

    "蘆洲":    r"\\Dabs-nas2\新公用區\公文掃描檔\115\蘆洲"
}

def move_pdf(pdf_path, area, doc_no, subject):

    if not os.path.exists(pdf_path):
        print(f"[SKIP] 檔案不存在: {pdf_path}")
        return

    target = ARCHIVE_FOLDERS.get(area)

    if not target:
        print(f"未設定區域：{area}")
        return

    os.makedirs(target, exist_ok=True)

    ext = os.path.splitext(pdf_path)[1]

    target_path = os.path.join(target, f"{doc_no}{ext}")

    counter = 1
    while os.path.exists(target_path):
        target_path = os.path.join(target, f"{doc_no}_{counter}{ext}")
        counter += 1

    shutil.move(pdf_path, target_path)

    print(f"已搬移：{target_path}")

    return target_path