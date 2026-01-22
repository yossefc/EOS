import pandas as pd
import sys

file_path = r"d:\EOS\rg_IDS-L_DANS_SHERLOCK _19052025_070028_20_05_2025_08_13_52.xls"

try:
    # Try reading as Excel (auto-detect engine)
    # Note: 'xlrd' is needed for .xls, 'openpyxl' for .xlsx
    # We'll just read the first row
    try:
        df = pd.read_excel(file_path, nrows=0)
    except Exception as e:
        # Fallback for older xls or if engine mismatch
        print(f"Standard read failed: {e}")
        # Try creating engine explicitly if needed, but pandas usually handles it.
        # Maybe it's a CSV masquerading as XLS?
        try:
            df = pd.read_csv(file_path, sep=None, engine='python', nrows=0)
            print("Read as CSV/Text")
        except:
             raise e

    print("Columns found:")
    for col in df.columns:
        print(f"- {col}")
        
except Exception as e:
    print(f"Error reading file: {e}")
