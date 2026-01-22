import pandas as pd
import sys

file_path = r"d:\EOS\rg_IDS-L_DANS_SHERLOCK _19052025_070028_20_05_2025_08_13_52.xls"

try:
    # Read first row to get headers
    df = pd.read_excel(file_path, engine='xlrd', nrows=0)
    
    print("HEADERS_START")
    for col in df.columns:
        print(col)
    print("HEADERS_END")
        
except Exception as e:
    print(f"Error reading file: {e}")
