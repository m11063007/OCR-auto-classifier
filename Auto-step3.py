#八里機關來文登入
import os
import re
import pdfplumber
import pandas as pd

from pdf2image import convert_from_path
from paddleocr import PaddleOCR
from PIL import Image

# =========================
# OCR 初始化
# =========================
ocr = PaddleOCR(
    use_angle_cls=True,
    lang='chinese_cht'
)

# =========================
# PDF 文字提取
# =========================
def extract_text_from_pdf(pdf_path):

    full_text = ""

    # 先嘗試直接抓 PDF 文字
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()

                if text:
                    full_text += text + "\n"

    except Exception as e:
        print(f"PDF文字提取失敗: {pdf_path}")
        print(e)

    # 如果沒文字 -> OCR
    if len(full_text.strip()) < 20:

        print(f"OCR辨識中: {pdf_path}")

        try:
            images = convert_from_path(pdf_path, dpi=300)

            for img in images:

                temp_img = "temp_page.jpg"
                img.save(temp_img, "JPEG")

                result = ocr.ocr(temp_img)

                for line in result[0]:
                    full_text += line[1][0] + "\n"

                os.remove(temp_img)

        except Exception as e:
            print(f"OCR失敗: {pdf_path}")
            print(e)

    return full_text


# =========================
# 圖片 OCR
# =========================
def extract_text_from_image(image_path):

    text = ""

    result = ocr.ocr(image_path)

    for line in result[0]:
        text += line[1][0] + "\n"

    return text


# =========================
# 日期擷取
# =========================
def extract_date(text):

    patterns = [

        r'(\d{3}年\d{1,2}月\d{1,2}日)',   # 114年05月20日
        r'(\d{4}/\d{1,2}/\d{1,2})',      # 2025/05/20
        r'(\d{4}-\d{1,2}-\d{1,2})'
    ]

    for p in patterns:
        m = re.search(p, text)

        if m:
            return m.group(1)

    return ""


# =========================
# 發文字號擷取
# =========================
def extract_doc_number(text):

    patterns = [

        r'發文字號[：:]\s*(.+)',
        r'字號[：:]\s*(.+)'
    ]

    for p in patterns:

        m = re.search(p, text)

        if m:
            value = m.group(1).split('\n')[0]
            return value.strip()

    return ""


# =========================
# 主旨 / 開會事由
# =========================
def extract_subject(text):

    patterns = [

        r'主旨[：:]\s*(.+)',
        r'開會事由[：:]\s*(.+)'
    ]

    for p in patterns:

        m = re.search(p, text, re.DOTALL)

        if m:

            value = m.group(1)

            # 只取第一行
            value = value.split('\n')[0]

            return value.strip()

    return ""


# =========================
# 主程式
# =========================
folder_path = r"C:\Users\Administrator\Desktop\SCAN"

results = []

for file in os.listdir(folder_path):

    file_path = os.path.join(folder_path, file)

    text = ""

    # PDF
    if file.lower().endswith(".pdf"):

        text = extract_text_from_pdf(file_path)

    # 圖片
    elif file.lower().endswith((".jpg", ".jpeg", ".png")):

        text = extract_text_from_image(file_path)

    else:
        continue

    # 擷取資料
    date = extract_date(text)

    doc_number = extract_doc_number(text)

    subject = extract_subject(text)

    results.append({
        
        "日期": date,
        "發文字號": doc_number,
        "主旨/開會事由": subject
    })

    print(f"完成: {file}")

# =========================
# 輸出 Excel
# =========================
df = pd.DataFrame(results)

output_file = "公文提取結果.xlsx"

df.to_excel(output_file, index=False)

print(f"\n已輸出: {output_file}")