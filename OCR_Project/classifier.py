#classifier.py
import re
import os
from rules import AREA_KEYWORDS, AREA_SECOND_RULES

def is_phone(num):

    raw = num.replace("-", "")

    # 手機
    if re.fullmatch(r'09\d{8}', raw):
        return True

    # 市話
    if re.fullmatch(r'0[2-8]\d{7,9}', raw):
        return True

    # OCR常抓到的市話尾碼
    
    if len(raw)==8 and raw.startswith(("2610", "8286", "2291", "2601")):
        return True
#上面的 if 條件通通沒有成立，告訴主程式：「這串數字不是電話，是公文文號」。
    return False
def remove_contact_info(text):

    text = re.sub(r'電話[:：]?\s*[\d\-()]+', '', text)

    text = re.sub( r'傳真[:：]?\s*[\d\-()]+', '', text)

    text = re.sub(r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}',
        '', text )
    return text

def extract_doc_number(text):

    text = remove_contact_info(text)

    patterns = [
        # 1. 處理帶有年度括號與字第的格式 (如: 五達經技(115)字第1140010001號, 豐工(114)字第1140610002號)
        r'第\s*(\d{10})\s*號?',
        r'第\s*(\d{9})\s*號?',
        r'(?:字第|第)\s*(\d{9,10})\s*號?',        
        #處理括號夾在中間或後面的特殊格式 (如: 翰工字第(115) 0417-1號 -> 擷取 0417-1)
        r'(?:字第|第)\s*(?:\(\d{3}\))?\s*(\d{4,10}-\d{1,3})\s*號?',
        # 3. 處理廠商類只有 6~7 碼且無連字號的格式 (如: 直字第1150225號, 桔字第0331-1號, 旭字第01150401-1號)
        r'字\s*(\d{6,8})\s*號?',
        r'字第\s*(\d{6,8}-\d{1,2}|\d{6,8})\s*號?',
        r'(?:字第|第)\s*(\d{4,8}-\d{1,2})',
        r'(115\d{7})',
        # 1150604-01
        r'(\d{7,10}-\d{1,3})']
#\s代表空白字元、*代表出現0次以上，避免OCR時有空格出現
#\d代表任意數字、{10}代表出現10次、()是capturing group，即是後面出現的group(1)
#?代表出現0或1次，號字可有可無   
    for p in patterns:
            #re.finditer，確保遇到電話時可以跳過並繼續找下一個符合的文號
        for m in re.finditer(p,text):
            #確認抓到是不是電話，如果不是，就是要的公文文號
            matched_value = m.group(1) 
                #group(0)抓全部"字第\s*(\d{10})\s*號"，group(1)只抓括弧內特定目標"(\d{10})"
            matched_value = matched_value.strip()
                # 移除前後可能因為 OCR 產生的空白
            if not is_phone(matched_value):
                    return matched_value
    return None   

#分類公所、公司、廠商(依文號)
def get_doc_category(doc_no):
    if not doc_no:
        return "未知"
    
    doc_clean=doc_no.strip()#移除空白
    raw=re.sub(r"\D","", doc_clean)#把字串中的非數字字元刪除，\D任意非數字字元，\d 代表數字
#0417-1移除-
# raw[3] 代表第四碼數字（索引從 0 開始算：0,1,2是年份，3是第四碼） 11537XXXXX
    if len(raw) == 10 and (raw[3] in ("3", "4", "5","6")):
            return "公所"
# 2. 檢查是否符合公司特徵（前三碼任意，後面接 00 開頭）11500X0XXX
    if len(raw) == 10 and re.match(r"^\d{3}00", raw):#^從字串最左邊開始
            return "公司"
    return "廠商"
    
 

def clean_text(text):
    return re.sub(r"\s+", "", text.replace("\n", ""))
CORRECTION_MAP = {
    "八時": "八里",
    "八裏": "八里",
    "八里區": "八里"
}

def normalize(text):
    for k, v in CORRECTION_MAP.items():
        text = text.replace(k, v)
    return text 
def preprocess(text):
    text = text.replace("\n", "")
    text = normalize(text)
    text = clean_text(text)
    return text



def extract_subject(text):

    text = preprocess(text)
    text = re.sub(r'(主旨|事由|會勘事由|開會事由)[:：]', '主旨:', text)

    m = re.search(r'主旨:(.*?)(說明|依據|附件|正本|副本|$)', text)

    return m.group(1).strip() if m else "找不到主旨"

#分類八里、五股、林口、蘆洲
def detect_area(subject, full_text=None):

    subject = preprocess(subject)


    for area, kws in AREA_KEYWORDS.items():
        for k in kws:
            if k in subject:
                return area

    if full_text:
        return fallback_area(full_text)

    return r"C:\Users\Administrator\Desktop\SCAN\分類地區失敗"



def fallback_area(text):

    text = preprocess(text)

    patterns = {
        "八里": [r"八里區公所", r"八里區",r"八里"],
        "五股": [r"五股區公所", r"五股區",r"五股"],
        "林口": [r"林口區公所", r"林口區", r"林口"],
        "蘆洲": [r"蘆洲區公所", r"蘆洲區", r"蘆洲"]
    }

    for area, regs in patterns.items():
        if any(re.search(r, text) for r in regs):
            return area

    return "未分類"

def extract_date(text):
#OCR移除空白
    if not text:
        return ""
    clean_text = text.replace("\n", "").replace(" ", "").replace("\r", "")
    patterns = [
        r'中華民國\s*(\d{3})[年牢午\s]?\s*(\d{1,2})[月\s]?\s*(\d{1,2})[日曰口1\s]?',
        
        # 2. 沒有中華民國開頭，但有數字年份的格式
        r'(\d{3})[年牢午\s]?\s*(\d{1,2})[月\s]?\s*(\d{1,2})[日曰口1\s]?',
        
        # 3. 西元格式維持不變
        r'(\d{4}/\d{1,2}/\d{1,2})',
        r'(\d{4}-\d{1,2}-\d{1,2})'
    ]

    for p in patterns:
        m = re.search(p, clean_text)
        if m:
            # 如果是命中前兩條「容錯規則」（有 3 個群組）
            if len(m.groups()) == 3 and m.group(1):
                # 重新組合成乾淨標準的格式回傳（例如：115年06月23日）
                return f"{m.group(1)}年{m.group(2)}月{m.group(3)}日"
            # 如果是西元格式
            return m.group(1)


    return ""#空字串，等於直接刪除




#分類案件(北區、技服、排水.....)後寫進excel各自的工作表
def detect_second_area(area, subject):

    if area not in AREA_SECOND_RULES:
        return "自行分類"

    for sec, kws in AREA_SECOND_RULES[area].items():
        for k in kws:
            if k in subject:
                return sec

    return "自行分類"
