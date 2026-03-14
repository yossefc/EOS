"""Verifie le probleme de doublons dans l'import PARTNER."""
import sys, os
import pandas as pd
import warnings
warnings.filterwarnings('ignore')

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if not os.environ.get('DATABASE_URL'):
    os.environ['DATABASE_URL'] = 'postgresql+psycopg2://postgres:postgres@localhost:5432/eos_db'

from app import create_app
from extensions import db
from models.models import Donnee

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
cr_dir = r'E:\LDMEOS\reponses_cr backup'

app = create_app()
with app.app_context():
    # 1. Quels NUM sont dans les fichiers Format A?
    print("=" * 60)
    print("ANALYSE DES NUM DANS LES FICHIERS FORMAT A")
    print("=" * 60)

    all_nums = {}
    xls_files = sorted([f for f in os.listdir(cr_dir) if f.endswith('.xls')])
    format_a_count = 0
    format_b_count = 0
    format_a_rows = 0
    format_b_rows = 0

    for f in xls_files:
        try:
            df = pd.read_excel(os.path.join(cr_dir, f))
            cols_lower = [str(c).lower().strip() for c in df.columns]

            if len(df.columns) >= 30 or 'NUM' in [str(c).strip() for c in df.columns]:
                format_a_count += 1
                format_a_rows += len(df)
                for _, row in df.iterrows():
                    num = str(row.get('NUM', '')).strip() if pd.notna(row.get('NUM')) else None
                    if num and num != 'nan':
                        if num not in all_nums:
                            all_nums[num] = []
                        all_nums[num].append(f)
            else:
                format_b_count += 1
                format_b_rows += len(df)
        except Exception as e:
            pass

    print(f"\nFormat A: {format_a_count} fichiers, {format_a_rows} lignes")
    print(f"Format B: {format_b_count} fichiers, {format_b_rows} lignes")

    # Combien de NUM sont uniques vs dupliques?
    unique_nums = sum(1 for nums in all_nums.values() if len(nums) == 1)
    dup_nums = sum(1 for nums in all_nums.values() if len(nums) > 1)
    print(f"\nNUM uniques: {unique_nums}")
    print(f"NUM avec doublons (meme NUM dans plusieurs fichiers): {dup_nums}")

    # Montrer quelques doublons
    print(f"\nExemples de NUM dupliques:")
    count = 0
    for num, files in sorted(all_nums.items(), key=lambda x: len(x[1]), reverse=True):
        if len(files) > 1 and count < 10:
            print(f"  NUM='{num}': {len(files)} fichiers")
            count += 1

    # 2. Combien de Donnee PARTNER en DB avec ces NUM?
    print(f"\n" + "=" * 60)
    print("EN DB: PARTNER ARCHIVES")
    print("=" * 60)

    partner_archives = Donnee.query.filter(
        Donnee.client_id == 11,
        Donnee.statut_validation.in_(['archive', 'archivee'])
    ).all()

    print(f"Total PARTNER archives: {len(partner_archives)}")

    # Combien ont un numeroDossier court (1-2 chiffres)?
    short_nums = [d for d in partner_archives if d.numeroDossier and len(d.numeroDossier) <= 3]
    print(f"Avec numeroDossier court (<=3 chars): {len(short_nums)}")

    # Distribution de la longueur du numeroDossier
    len_dist = {}
    for d in partner_archives:
        l = len(d.numeroDossier) if d.numeroDossier else 0
        len_dist[l] = len_dist.get(l, 0) + 1
    print(f"\nDistribution longueur numeroDossier:")
    for l in sorted(len_dist.keys()):
        print(f"  len={l}: {len_dist[l]}")
