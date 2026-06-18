#pipeline
from pdf_reader import read_pdf_text
from classifier import *
from config_lookup import lookup_excel_file
from excel_writer import append_to_excel
from file_mover import move_pdf
from logger import log, warn, error


def process_file(pdf_path):
    
    text = read_pdf_text(pdf_path)
   
    if not text:
        warn("讀不到PDF")
        return None
    sender = extract_sender(text)
    category = classify_org(sender)
    sender = extract_sender(text)
    date = extract_date(text)
    doc_no = extract_doc_number(text)
    subject = extract_subject(text)

    if not doc_no:
        warn("無文號")
        return None

    area = detect_area(subject)
    if area == "未分類":
        area = fallback_area(text)

    

    second_area = detect_second_area(area, subject)
    
    # ⭐ 公司文直接搬檔（不寫 Excel）
    if category == "公司":

        log("公司文 → 不寫Excel")

        try:
            move_pdf(pdf_path, area, doc_no, subject)
        except Exception as e:
            error(f"搬檔失敗: {e}")

        return {
            "area": area,
            "category": category,
            "doc_no": doc_no,
            "subject": subject
        }

    # ⭐ Excel lookup
    excel_file, used_key = lookup_excel_file(area, category,  debug=True)
    if not excel_file:
        warn("找不到Excel設定")
        return None
    # ⭐ 搬檔（主流程）
    excel_ok = False
    try:
        append_to_excel(
        excel_file,
        second_area,
        date,
        doc_no,
        subject)

        log("Excel寫入成功")
        excel_ok = True
    except Exception as e:

        error(f"Excel失敗: {e}")
    if excel_ok:

        try:

            move_pdf(
                pdf_path,
                area,
                doc_no,
                subject )

            log("搬檔成功")

        except Exception as e:

            error(f"搬檔失敗: {e}")

    else:

        warn("Excel未成功，保留原始PDF")

    return {
        "area": area,
        "category": category,
        "doc_no": doc_no,
        "subject": subject,
        "second_area": second_area
    }