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

def verify_export():
    app = create_app()
    with app.app_context():
        # Find Sherlock ID
        client = Client.query.filter_by(code='RG_SHERLOCK').first()
        if not client:
            print("❌ RG_SHERLOCK not found")
            return

        with app.test_client() as c:
            print(f"Testing export for client ID {client.id}...")
            # Send POST as implemented
            response = c.post('/api/export/sherlock', json={'client_id': client.id})
            
            print(f"Status Code: {response.status_code}")
            print(f"Content Type: {response.content_type}")
            
            if response.status_code == 200:
                if 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' in response.content_type:
                    print(f"✅ Export successful. Size: {len(response.data)} bytes")
                    # Optionally try to open it with pandas to check columns
                    try:
                        import pandas as pd
                        df = pd.read_excel(io.BytesIO(response.data))
                        print(f"✅ Excel valid. Columns: {len(df.columns)}")
                        print(f"   Sample columns: {list(df.columns)[:5]}")
                        
                        # Verify we have 68 (or close) columns
                        if len(df.columns) >= 60:
                             print("✅ Column count looks correct for Sherlock")
                        else:
                             print(f"⚠️ Warning: Expected ~68 columns, got {len(df.columns)}")
                             
                    except Exception as e:
                        print(f"❌ Failed to parse Excel: {e}")
                else:
                    print("❌ Wrong content type for Excel")
            else:
                print(f"❌ Export failed: {response.data.decode('utf-8')[:200]}")

if __name__ == "__main__":
    verify_export()
