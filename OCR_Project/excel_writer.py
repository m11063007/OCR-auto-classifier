#excel_writer.py
import pandas as pd
import os
from openpyxl import load_workbook
#openpyxl讀取寫入修改excel的函式

def append_to_excel(
    excel_file,
    second_area,
    date,
    doc_no,
    subject):

    try:

        wb = load_workbook(excel_file)

        if second_area not in wb.sheetnames:

            print(f"找不到工作表：{second_area}")

            return False

        ws = wb[second_area]

        # 檢查文號是否存在
        for row in ws.iter_rows(
            min_row=2,
            values_only=True
        ):

            if str(row[1]).strip() == str(doc_no).strip():

                print(f"文號已存在：{doc_no}")

                return False

        ws.append([
            date,
            doc_no,
            subject
        ])

        wb.save(excel_file)

        return True

    except Exception as e:

        print(e)

        return False