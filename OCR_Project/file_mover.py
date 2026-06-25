#file_mover.py
import os
import shutil
import re

ARCHIVE_FOLDERS = {

    "八里":    r"\\Dabs-nas2\新公用區\公文掃描檔\115\八里",

    "五股":    r"\\Dabs-nas2\新公用區\公文掃描檔\115\五股",

    "林口":    r"\\Dabs-nas2\新公用區\公文掃描檔\115\林口",

    "蘆洲":    r"\\Dabs-nas2\新公用區\公文掃描檔\115\蘆洲",
    "手動修改":    r"C:\Users\Administrator\Desktop\SCAN\手動修改"
}
def rename_only(pdf_path,doc_no, second_area, is_scan=True):
    #is_scan: 是否為掃描檔。True ➔ 檔名改成文號；False ➔ 保持原檔名
    if not os.path.exists(pdf_path):
    #確認原檔還在SCAN
        
        return None
    folder_path = os.path.dirname(pdf_path)
    #去除路徑中的檔名，只留該檔案所在的目錄路徑(純路徑)
    ext = ".pdf"#(.pdf)
    base_name = f"{doc_no}_{second_area}"
    
    #移除文號中特殊字元
    base_name = re.sub(r'[\\/:*?"<>|]', '', base_name).strip()
    new_filename = f"{base_name}{ext}"
    local_new_path = os.path.join(folder_path, new_filename)
    

    if pdf_path != local_new_path:
    #跳過電子公文(不用更名，檔名=文號，故FAlSE)
        counter = 1#本地資料夾防撞名
        while os.path.exists(local_new_path):
        #只要撞名，回傳 True
            local_new_path = os.path.join(folder_path, f"{base_name}_{counter}{ext}")
            counter += 1
        os.rename(pdf_path, local_new_path)
        
    return local_new_path
#回傳 新路徑給pipeline後續的 Excel 記帳搬移才找得到實體檔案
   



#Excel 成功後，才將檔案搬移到 NAS 
def move_pdf(current_pdf_path, area):
    
    if not os.path.exists(current_pdf_path):
        return None
    

    target = ARCHIVE_FOLDERS.get(area)

    if not target:
        print(f"分類地區失敗：{area}更名後將移至『分類地區失敗』資料夾")
        target = r"C:\Users\Administrator\Desktop\SCAN\分類地區失敗"
    #如果資料夾不存在：程式會自動幫你建立，若資料夾已存在，則會直接忽略不報錯
    os.makedirs(target, exist_ok=True)


    filename = os.path.basename(current_pdf_path)
    base_name, ext = os.path.splitext(filename)
    target_path = os.path.join(target, filename)
   
    
    # NAS 防重複覆蓋機制
    counter = 1 

    while os.path.exists(target_path):
        target_path = os.path.join(target, f"{base_name}_{counter}{ext}")
        counter += 1

    shutil.move(current_pdf_path, target_path)

    print(f"已搬移：{target_path}")

    return target_path