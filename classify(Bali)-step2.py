#分類八里公所、公司、廠商公文
import os
import shutil
# =====================================
# 已更名PDF的資料夾
# =====================================
SOURCE_FOLDER = r"C:\Users\Administrator\Desktop\SCAN\八里"
#=================
# 依文號分類規則(公所、公司、廠商)
#=================
DOC_RULES = {

    # 公所公文
    "11537": r"C:\Users\Administrator\Desktop\SCAN\八里\公所",

    # 公司公文
    "11500": r"\\Dabs-nas2\新公用區\公文掃描檔\115\八里", 
    #廠商
    "11505": r"C:\Users\Administrator\Desktop\SCAN\八里\廠商",
    "11506": r"C:\Users\Administrator\Desktop\SCAN\八里\廠商",
    "11507": r"C:\Users\Administrator\Desktop\SCAN\八里\廠商",
}

# =====================================
# 第二層分類(北區、南區、路養...)
# =====================================
SECOND_RULES = {

    "北區": [
        "北區",
        "北區工程"
    ],

    "南區": [
        "南區",
        "南區工程"
    ],

    "區排": [
        "區排",
        "排水",
        "雨水下水道",
        "箱涵",
        "側溝",
        "橫越管"
    ],

    "路養": [
        "路養",
        "路面養護",
        "AC改善",
        "道路改善"
    ],

    "照明": [
        "照明",
        "路燈"
    ],

    "公園": [
        "公園"
    ],

    "搶災": [
        "搶災"
    ]
}
# =====================================
# 第一層分類
# =====================================
def detect_main_area(filename):

    doc_number = os.path.splitext(filename)[0]

    for prefix, folder in DOC_RULES.items():

        if doc_number.startswith(prefix):

            return folder

    return r"C:\Users\Administrator\Desktop\SCAN\未分類"


# =====================================
# 第二層分類
# =====================================
def detect_second_area(subject):

    for area, keywords in SECOND_RULES.items():

        for keyword in keywords:

            if keyword in subject:

                return area

    return "其他"



# =====================================
# 處理檔案
# =====================================
def process_file(file):
    d, n, s = extract_info(content)
    s = 主旨 或 會勘事由
    source_path = os.path.join(
        SOURCE_FOLDER,
        file
    )

    # 只處理 PDF
    if not file.lower().endswith(".pdf"):

        return

     # =========================
    # 第一層分類
    # =========================
    main_folder = detect_main_area(n)

    # =========================
    # 第二層分類
    # =========================
    second_folder = detect_second_area(s)
    

    # =========================
    # 建立最終資料夾
    # =========================
    final_folder = os.path.join(
        main_folder,
        second_folder
    )

    os.makedirs(final_folder, exist_ok=True)

    # =========================
    # 目標路徑
    # =========================
    target_path = os.path.join(
        final_folder,
        file
    )

    # 避免重複檔名
    counter = 1

    base_name, ext = os.path.splitext(file)

    while os.path.exists(target_path):

        new_filename = f"{base_name}_{counter}{ext}"

        target_path = os.path.join(
            final_folder,
            new_filename
        )

        counter += 1

    # =========================
    # 移動檔案
    # =========================
    shutil.move(source_path, target_path)

    print(f"完成：{target_path}")


# =====================================
# 主程式
# =====================================
def main():

    files = os.listdir(SOURCE_FOLDER)

    print(f"共 {len(files)} 個檔案")

    for file in files:

        process_file(file)

    print("\n全部完成")


# =====================================
# 執行
# =====================================
if __name__ == "__main__":

    main()