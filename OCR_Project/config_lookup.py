#config_lookup
from config import EXCEL_MAPPING

def lookup_excel_file(area, category, debug=False):
    key = (area.strip(), category.strip())

    if key in EXCEL_MAPPING:

        if debug:
            print(f"命中 Excel mapping：{key}")

        return EXCEL_MAPPING[key], key

    if debug:
        print(f"❌ 找不到 Excel mapping：{area}-{category}")

    return None, None