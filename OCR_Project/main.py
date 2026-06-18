#maim.py
import os
from pipeline import process_file


def batch(folder):

    results = []

    for f in os.listdir(folder):
        if f.endswith(".pdf"):
            r = process_file(os.path.join(folder, f))
            if r:
                results.append(r)

    return results


if __name__ == "__main__":

    folder = r"C:\Users\Administrator\Desktop\SCAN"

    results = batch(folder)
        
    print("\n====================")
    print(f"完成數量: {len(results)}")
    print("====================")

  