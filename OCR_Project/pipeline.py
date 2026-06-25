#pipeline流程控制，控制讀取、擷取、分類、Excel 記帳與實體搬移的先後順序
from pdf_reader import read_pdf_text
from classifier import extract_date, extract_doc_number, extract_subject,detect_area, fallback_area, detect_second_area, get_doc_category 
from config_lookup import lookup_excel_file
from excel_writer import append_to_excel
from file_mover import move_pdf,rename_only,ARCHIVE_FOLDERS
from logger import log, warn, error
import os
from file_mover import move_pdf

def process_file(pdf_path):
    
    text = read_pdf_text(pdf_path)
   
    if not text:
        warn("讀不到PDF")
        return None
   
    date = extract_date(text)
    doc_no = extract_doc_number(text)
    subject = extract_subject(text)
    category = get_doc_category(doc_no)
    
    # 安全防禦：如果沒抓到文號，立刻中斷，防止後續程序崩潰
    if not doc_no:
        warn("無法辨識文號")
       
        move_pdf(pdf_path, area="手動修改")
        return None
    
    #檔案特徵判斷
    print("-------------------------------------")
    log(f" 文號:[{doc_no}] | 分類:【{category}】")
   

    #掃描檔or 電子檔
    filename = os.path.basename(pdf_path)
    name_without_ext = os.path.splitext(filename)[0]
    #115xxxxx+.pdf
    if name_without_ext.isdigit() or doc_no in name_without_ext:
        is_scan_file = False  # 電子公文（原檔名已是純數字文號），搬移時不重新更名 [1]
        #觸發 file_over中if pdf_path != local_new_path:
    else:
        is_scan_file = True   # 紙本掃描檔（原檔名為雜訊），歸檔時強制啟動文號更名 [1]
        
    # ----------------------------------------------------------
    # 行政區與案件兩層分類
    # ----------------------------------------------------------
    area = detect_area(subject, full_text=text)
    if area in ("分類地區失敗", "未分類"):
        area = fallback_area(text)

    second_area = detect_second_area(area, subject)
    target_dir = ARCHIVE_FOLDERS.get(area, r"\\Dabs-nas2\新公用區\公文掃描檔\115\分類地區失敗")
    
    # 預計出廠的精準名稱 (如: 1150612001_公園.pdf)
    expected_nas_path = os.path.join(target_dir, f"{doc_no}_{second_area}.pdf")

    # 如果 NAS 裡早就已經有「這發文號且同一個案件類別」的 PDF 了，才煞車跳過
    if os.path.exists(expected_nas_path):
        warn(f"【NAS 歷史防禦】NAS 歸檔區已存在此案件公文 [{doc_no}_{second_area}.pdf]，流程終止！")
        return None
# ----------------------------------------------------------
    # 改名
 # ----------------------------------------------------------
    current_path = rename_only(pdf_path, doc_no, second_area, is_scan=is_scan_file)
    new_filename = os.path.basename(current_path)
    log(f" ➔ 本地更名完成，新暫存檔名: {new_filename}")
 #----------------------------------------------------------
    # 公司文直接搬檔（不寫 Excel）
    if category == "公司":

        final_path = move_pdf(current_path, area)
        
        if final_path:
            log(f"【完成】公司文歸檔成功 ➔ {final_path}")
        else:
            error(f"【失敗】公司文搬移錯誤")
         #公司終點   
        return {
            "area": area, "category": category, "doc_no": doc_no, 
            "subject": subject, "second_area": second_area
        }
# ==========================================================        
#Excel 記帳
# ==========================================================        
    # Excel lookup底線 _ 是一個專門用來存放「我知道你存在，但我不需要用你」的附帶資訊
    excel_file, _ = lookup_excel_file(area, category,debug=True)
    if not excel_file:
        warn("找不到Excel設定，未搬檔")
        return None
    # 搬檔（主流程）
    excel_ok = append_to_excel(
        excel_file=excel_file,
        second_area=second_area,
        date=date,
        doc_no=doc_no,
        subject=subject
    )
    #新寫路入跟已寫入都可搬移
    if excel_ok is True or excel_ok== "EXIST":

        final_path = move_pdf(current_path, area)
        if excel_ok == "EXIST":
            log(f"excel有紀錄，直接移檔")
        else:
            log(f"【完成】公文成功登錄並安全歸檔 ➔ {final_path}")
    else:    
        warn(f"【攔截歸檔】請關閉Excel ，安全保留原始 PDF 於原位: {new_filename}")
    #公所/廠商終點
    return {
        "area": area,
        "category": category,
        "doc_no": doc_no,
        "subject": subject,
        "second_area": second_area
    }