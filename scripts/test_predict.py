from pathlib import Path
import sys
import csv

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.train_pipeline import DATA_PATH
from backend.predict_service import Predictor
def load_sample(n=10):
    rows = []
    with open(DATA_PATH, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for i, r in enumerate(reader):
            if i >= n:
                break
            text = (r.get('Complaint Type') or '') + ' ' + (r.get('Descriptor') or '')
            rows.append(text)
    return rows


def main():
    sample = load_sample(10)
    p = Predictor()
    for s in sample:
        print('INPUT:', s)
        print('PRED:', p.predict(s))
        print('---')


if __name__ == '__main__':
    main()
