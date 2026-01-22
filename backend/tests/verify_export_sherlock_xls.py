import sys
import os
import io

# Configuration
os.environ['DATABASE_URL'] = 'postgresql+psycopg2://eos_user:eos_password@localhost:5432/eos_db'
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from app import create_app
from extensions import db
from models import Client

def verify_export_xls():
    app = create_app()
    with app.app_context():
        # Find Sherlock ID
        client = Client.query.filter_by(code='RG_SHERLOCK').first()
        if not client:
            print("❌ RG_SHERLOCK not found")
            return

        with app.test_client() as c:
            print(f"Testing Legacy Export for client ID {client.id}...")
            # Send POST
            response = c.post('/api/export/sherlock', json={'client_id': client.id})
            
            print(f"Status Code: {response.status_code}")
            print(f"Content Type: {response.content_type}")
            print(f"Filename: {response.headers.get('Content-Disposition')}")
            
            if response.status_code == 200:
                # Check for OLE2 binary (D0 CF 11 E0) signature of .xls
                header = response.data[:8]
                print(f"File Header: {header.hex().upper()}")
                
                if header.hex().upper().startswith("D0CF11E0"):
                    print("✅ Valid OLE2 (.xls) signature found.")
                    
                    # Optionally verify with pandas (engine='xlrd')
                    try:
                        import pandas as pd
                        df = pd.read_excel(io.BytesIO(response.data), engine='xlrd')
                        print(f"✅ Pandas read success. Columns: {len(df.columns)}")
                        # Check header row (cols)
                        print(f"Sample columns: {list(df.columns)[:5]}")
                        
                        # Verify we have ~68 columns
                        if len(df.columns) > 60:
                             print("✅ Column count looks correct for Sherlock")
                             
                    except Exception as e:
                        print(f"❌ Failed to parse .xls: {e}")
                else:
                    print("❌ Header does not match OLE2 (.xls)")
            else:
                print(f"❌ Export failed: {repr(response.data)}")

if __name__ == "__main__":
    verify_export_xls()
