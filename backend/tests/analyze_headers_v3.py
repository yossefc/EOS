import pandas as pd
import sys

file_path = r"d:\EOS\rg_IDS-L_DANS_SHERLOCK _19052025_070028_20_05_2025_08_13_52.xls"

try:
    # Read first 5 rows without header to see structure
    df = pd.read_excel(file_path, engine='xlrd', header=None, nrows=5)
    
    print("ROWS_START")
    print(df.to_string())
    print("ROWS_END")
        
except Exception as e:
    print(f"Error reading file: {e}")
