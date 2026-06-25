#maim.py
import os
from pipeline import process_file
from logger import log, error  # 沿用你原本設計的 logger

def batch(folder):
    #空List，用於收集處理PDF成功後回傳的結果
    results = []
    #讀取指定資料夾內，所有檔案並存入List
    all_files = os.listdir(folder)
    #抓PDF檔
    pdf_files = [f for f in all_files if f.lower().endswith(".pdf")]
    for f in pdf_files:
        #組合路徑及檔名
        full_path = os.path.join(folder, f)
        try:
            r = process_file(full_path)
            if r:
                results.append(r)
        #遇損毀PDF不會終止        
        except Exception as e:
            # 發生錯誤時，印出通報，並繼續執行迴圈的下一檔
            error(f"❌ 檔案 {f} 在處理過程中發生嚴重崩潰，跳過此檔。錯誤原因: {e}")
            continue

    return results


if __name__ == "__main__":

    folder = r"C:\Users\Administrator\Desktop\SCAN"

    results = batch(folder)
        
    print("\n====================")
    print(f"完成數量: {len(results)}")
   

  