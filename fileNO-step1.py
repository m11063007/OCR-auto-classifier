#重新命名公文掃描檔的檔名(文號)，分類各區公文(含電子公文)入各區資料夾
from PIL import Image
import pytesseract
from pdf2image import convert_from_path
import os
import pdfplumber
import re
# =====================================
# PDF來源資料夾
# =====================================
SOURCE_FOLDER = r"C:\Users\Administrator\Desktop\SCAN"
# ---------- 設定 ----------
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
POPPLER_PATH = r"C:\Users\Administrator\OneDrive\自動化公文歸檔\poppler-25.12.0\Library\bin"
#poppler PDF轉img(PDF內容讀取純文字、內嵌檔案、字型與元數據)
# =====================================
# 文號 Regex
# =====================================
DOC_PATTERN = [

    r'字第\s*(\d{10})\s*號?',
    r'字第\s*(\d{9})\s*號?',
    r'第\s*(\d{10})\s*號?',
    r'第\s*(\d{9})\s*號?',
    r'(115\d{7})'
]

# =====================================
# OCR 前處理
# =====================================
def clean_text(text):

    text = text.replace(" ", "")
    text = text.replace("\n", "")
    text = text.replace(":", "")
    text = text.replace("：", "")

    return text


# =====================================
# 判斷分類（依主旨）
# =====================================
def detect_area(text):

    subject_match = re.search(
        r'主.[:：](.*?)(說明|辦法|正本|副本)',
        text
    )

    if subject_match:

        subject = subject_match.group(1)

    else:

        subject = text

    print(f"主旨：{subject}")

    keywords = ["蘆洲", "五股",  "林口"]

    for k in keywords:

        if k in subject:

            return k

    return "八里"
#======================================
#讀取電子pdf文字
#=======================================
def read_digital_pdf(pdf_path):
    text =""
    with pdfplumber.open(pdf_path) as pdf:
        if pdf.pages:
            text= pdf.pages[0].extract_text()
    if text:
        return clean_text(text)
    return ""

# =====================================
# OCR 讀取 PDF
# =====================================
def read_scan_pdf(pdf_path):

    text = ""

    images = convert_from_path(
        pdf_path,
        dpi=300,
        first_page=1,
        last_page=1,
        grayscale=True,
        poppler_path=POPPLER_PATH
    )

    image = images[0]

    # pytesseract OCR
    text = pytesseract.image_to_string(
        image,
        lang="chi_tra+eng"   # 繁中+英文
    )

    return clean_text(text)




        # =====================================
        # 搜尋文號
        # =====================================
def find_doc_number(text):

    for p in DOC_PATTERN:

        match = re.search(p, text)

        if match:

            return match.group(1)
    return None
# =====================================
# 處理 PDF
# =====================================
def process_pdf(pdf_path):

    filename = os.path.basename(pdf_path)

    try:

        print(f"\n處理中：{filename}")
        # =====================================
        # 先判斷是否電子PDF
        # =====================================
        text = read_digital_pdf(pdf_path)

        is_digital = bool(text)

# =====================================
# 若是掃描PDF -> OCR
# =====================================
        if not text:

            print("掃描PDF OCR中...")

            text = read_scan_pdf(pdf_path)
        
        # =====================================
        # 判斷分類
        # =====================================
        area = detect_area(text)

        print(f"分類：{area}")

        # =====================================
        # 建立資料夾
        # =====================================
        target_folder = os.path.join(
            SOURCE_FOLDER,
            area
        )
        os.makedirs(target_folder, exist_ok=True)
    

        # =====================================
        # 新檔名
        # =====================================
       
        doc_number= find_doc_number(text)
        if doc_number:
                new_filename = f"{doc_number}.pdf"
        else:
                new_filename = filename

        target_path = os.path.join(
            target_folder,
            new_filename
        )

        # =====================================
        # 避免重複檔名
        # =====================================
        counter = 1

        while os.path.exists(target_path):

            new_filename = f"{doc_number}_{counter}.pdf"

            target_path = os.path.join(
                target_folder,
                new_filename
            )

            counter += 1

    

    except Exception as e:

        print(f"錯誤：{filename}")
        print(e)


# =====================================
# 主程式
# =====================================
def main():

    pdf_files = [
        f for f in os.listdir(SOURCE_FOLDER)
        if f.lower().endswith(".pdf")
    ]

    print(f"共 {len(pdf_files)} 個PDF")

    for file in pdf_files:

        pdf_path = os.path.join(
            SOURCE_FOLDER,
            file
        )

        process_pdf(pdf_path)

    print("\n全部完成")


# =====================================
# 執行
# =====================================
if __name__ == "__main__":

    main()