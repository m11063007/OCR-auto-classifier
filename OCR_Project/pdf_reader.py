#pdf_reader.py
#統一PDF解析
import pdfplumber
import os
from pdf2image import convert_from_path
import pytesseract
import cv2
import numpy as np


# ---------- 設定 ----------
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
POPPLER_PATH = r"C:\Users\Administrator\OneDrive\自動化公文歸檔\poppler-25.12.0\Library\bin"
#poppler PDF轉img(PDF內容讀取純文字、內嵌檔案、字型與元數據)
# ---------- 影像前處理 ----------
def preprocess(img):
    img = np.array(img)
    #將Pillow影像轉回Numpy陣列，列陣為度形狀為(高度，寬度，通道數)RGB通道數為3

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # 去噪
    gray = cv2.medianBlur(gray, 3)

    # 二值化（關鍵）255:白/0:黑色
    _, th = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
#                        (灰階影像,預設閥值,最大值:當像素大於閥值，則取代的數值)
#cv2.THRESH_BINARY 二值化模式，大於門檻變純白（255），小於門檻變純黑（0）。
#cv2.THRESH_OTSU   自動計算整張圖片的亮度分佈（直方圖），自行幫你算出一個最完美的門檻值
#第一個回傳值（_）：OTSU 演算法幫你自動算出來的門檻值（介於 0~255 之間）。程式碼用底線 _ 代表忽略它、不儲存。
#th:最終影像陣列
    return th

def pdf_to_images(pdf_path, dpi=400):
    return convert_from_path(
        pdf_path,
        dpi=400,
        poppler_path=POPPLER_PATH
    )


def ocr_image(img):
    

    config = r"--oem 3 --psm 6" # OCR模式設定（段落模式）
    img = preprocess(img)
    return pytesseract.image_to_string(
        img,
        lang="chi_tra+eng",
        config=config
    )


def ocr_pdf(pdf_path):
    images = pdf_to_images(pdf_path)

    texts = []
    for img in images:
        texts.append(ocr_image(img))

    return "\n".join(texts)
#--------------抓文字
def extract_text_pdf(pdf_path):
    text=""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"

    return text

# ---------- 自動判斷入口（推薦用這個） ----------
def read_pdf_text(pdf_path):
    if not os.path.exists(pdf_path):# 檔案不存在
        raise FileNotFoundError(pdf_path)
 # 先試文字層
    text=extract_text_pdf(pdf_path)# 如果有文字
    if text.strip():
    #从一个字符串中删除任何开头和/或结尾的空白。   
        return text # 直接回傳
    return ocr_pdf(pdf_path) # 否則OCR

    

if __name__ == "__main__":
    path = r"C:\Users\Administrator\Desktop\SCAN\八里\公所\其他\1153759010.pdf"
    text = read_pdf_text(path)
    print(text)
