#classifier.py
import re
from rules import AREA_KEYWORDS, AREA_SECOND_RULES


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

def extract_sender(text):

    print("===== HEADER =====")
    print(text[:1000])
    print("==================")

    text = text.replace("\n", "")

    patterns = [

        # 公所
        r'(新北市(?:八里|五股|林口|蘆洲)區公所)\s*函',
        r'發文機關[:：]?\s*(.*?)\s*函',
        # 工程顧問公司
        r'([\u4e00-\u9fffA-Za-z0-9]{2,40}工程顧問有限公司)\s*函',

        # 有限公司
        r'([\u4e00-\u9fffA-Za-z0-9]{2,40}有限公司)\s*函',

        # 股份有限公司
        r'([\u4e00-\u9fffA-Za-z0-9]{2,40}股份有限公司)\s*函',

        # 企業社
        r'([\u4e00-\u9fffA-Za-z0-9]{2,40}企業社)\s*函',
    ]
    for p in patterns:

        m = re.search(p, text)

        if m:
            return m.group(1)

    return ""



def classify_org(sender, text=""):
    sender = preprocess(sender) or ""
    text = text or ""

    

        # 優先判斷公所
    if ("公所" in sender
        or"區公所" in sender
        or "公所函" in sender
        or "開會通知單" in sender
        or "市政府" in sender
        or "工務局" in sender

    ):
        return "公所"

    # 公司
    if any(k in sender for k in [
        "達博思",
        "達博",
        "博思",
        "工程顧問",
        "工程顧",
        "顧問"       
    ]):
        return "公司"
    
    if any(k in text for k in [
        "八達",
        "五達",
        "林達",
        "蘆達"       
    ]):
        return "公司"

    # 廠商
    if any(k in sender for k in [
        "營造","陽天","三直","白馬","紘合","申邦","永馨","詠富","景觀","環保","旭揚",
        "土木","晨天","桔興","企業","聯合","企業社",]):
        return "廠商"
    

    return "未分類"

def is_phone(num):

    raw = num.replace("-", "")

    # 手機
    if re.fullmatch(r'09\d{8}', raw):
        return True

    # 市話
    if re.fullmatch(r'0[2-8]\d{7,9}', raw):
        return True

    # OCR常抓到的市話尾碼
    
    if raw.startswith(("2610", "8286", "2291", "2601")):
        return True

    return False

def extract_doc_number(text):

    text = remove_contact_info(text)

    search_area = text[:1500]
    print("===== DOC DEBUG =====")
    print(search_area)
    print("=====================")

    

    patterns = [
             # 公所
        r'字第\s*(\d{10})號',

        # 完整文號
        r'([^\s\n]{1,30}字第[A-Za-z0-9\-]+號)',

        # 1150602004
        r'(115\d{7,9})',

        # 1150604-01
        r'(\d{7,10}-\d{1,3})',

        # 052810
        r'(\d{6,10})']

    for p in patterns:
            m = re.search(p,text)
            if m:
                doc_no = m.group(1)

                if doc_no.isdigit():

                    if is_phone(doc_no):
                        continue
                 #檔名非法字元
                doc_no = re.sub(
                    r'[<>:"/\\|?*()]',
                    '',
                doc_no
            )
                return doc_no.strip()

    return ""
def remove_contact_info(text):

    text = re.sub(
        r'電話[:：]?\s*[\d\-()]+',
        '',
        text
    )

    text = re.sub(
        r'傳真[:：]?\s*[\d\-()]+',
        '',
        text
    )

    text = re.sub(
        r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}',
        '',
        text
    )

    return text

def extract_subject(text):

    text = preprocess(text)
    text = re.sub(r'主旨[:：]', '主旨:', text)

    m = re.search(r'主旨:(.*?)(說明|依據|附件|正本|副本|$)', text)

    return m.group(1).strip() if m else "找不到主旨"

def extract_date(text):

    patterns = [
        r'中華民國\s*(\d{3}年\d{1,2}月\d{1,2}日)',
        r'(\d{3}年\d{1,2}月\d{1,2}日)',
        r'(\d{4}/\d{1,2}/\d{1,2})',
        r'(\d{4}-\d{1,2}-\d{1,2})'
    ]

    for p in patterns:
        m = re.search(p, text)
        if m:
            return m.group(1)

    return ""


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


def detect_area(subject, full_text=None):

    subject = preprocess(subject)


    for area, kws in AREA_KEYWORDS.items():
        for k in kws:
            if k in subject:
                return area

    if full_text:
        return fallback_area(full_text)

    return "未分類"


def detect_second_area(area, subject):

    if area not in AREA_SECOND_RULES:
        return "其他"

    for sec, kws in AREA_SECOND_RULES[area].items():
        for k in kws:
            if k in subject:
                return sec

    return "其他"
