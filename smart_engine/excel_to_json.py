import pandas as pd, json, time, os

DATA_DIR = os.path.join(os.getcwd(), 'data')
POSSIBLE = ['live_data.csv', 'live_data.ods', 'live_data.xlsx']
JSON_PATH = os.path.join(DATA_DIR, 'live_data.json')

def convert_once():
    for fname in POSSIBLE:
        path = os.path.join(DATA_DIR, fname)
        if os.path.exists(path):
            try:
                if fname.endswith('.csv'):
                    df = pd.read_csv(path)
                elif fname.endswith('.ods'):
                    df = pd.read_excel(path, engine='odf')
                else:
                    df = pd.read_excel(path)
                data = {r['Tag']: r['Value'] for _, r in df.iterrows()}
                tmp = JSON_PATH + '.tmp'
                with open(tmp, 'w') as f:
                    json.dump(data, f, indent=2)
                os.replace(tmp, JSON_PATH)
                print('[Converter] Wrote live_data.json')
                return
            except Exception as e:
                print(f'[Converter] Error reading {fname}: {e}')
    print('[Converter] No data file found')

if __name__=='__main__':
    while True:
        convert_once()
        time.sleep(5)
