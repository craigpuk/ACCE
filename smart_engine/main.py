import json, os, threading, time, gc
from datetime import datetime
from flask import Flask, jsonify, send_from_directory
from collections import deque

app = Flask(__name__)
BASE = os.getcwd()
DATA_DIR = os.path.join(BASE, 'data')
LIVE = os.path.join(DATA_DIR, 'live_data.json')
CURRENT = os.path.join(DATA_DIR, 'current_data.json')
CFG = os.path.join(BASE, 'smart_engine')

TAG_CFG = json.load(open(os.path.join(CFG, 'tag_config.json')))
LOGIC = json.load(open(os.path.join(CFG, 'logic_rules.json')))
history = {tag: deque(maxlen=10) for tag in TAG_CFG}

def check_logic(readings):
    alarms = []
    for rule in LOGIC.values():
        conds = rule.get('conditions', {})
        matches = []
        ok = True
        for t, cond in conds.items():
            val = readings.get(t, {}).get('value')
            if val is None or ('above' in cond and val <= cond['above']) or ('below' in cond and val >= cond['below']):
                ok = False
                break
            matches.append(f"{t}={val}")
        if ok:
            cause = rule.get('cause', '')
            impact = rule.get('impact','')
            message = rule.get('message','')
            desc = []
            if cause:
                desc.append(f"Cause: {cause}")
            if impact:
                desc.append(f"Impact: {impact}")
            tag_str = ', '.join(matches)
            alarms.append(f"{message} ({'; '.join(desc)}) [Tags: {tag_str}]")
    return alarms

def update_loop():
    while True:
        try:
            raw = json.load(open(LIVE, 'r', encoding='utf-8'))
        except:
            time.sleep(3)
            continue

        readings = {}
        for t, v in raw.items():
            mn = TAG_CFG.get(t, {}).get('min')
            mx = TAG_CFG.get(t, {}).get('max')
            # Custom CO thresholds
            if t == 'CO_Stack_ppm':
                if v <= 100:
                    status = 'green'
                elif v <= 300:
                    status = 'yellow'
                else:
                    status = 'red'
            else:
                if mn is not None and mx is not None:
                    if v < mn or v > mx:
                        status = 'red'
                    elif v > 0.9 * mx or v < 1.1 * mn:
                        status = 'yellow'
                    else:
                        status = 'green'
                else:
                    status = 'green'
            readings[t] = {'value': v, 'status': status}
            history[t].append(v)

        alarms = check_logic(readings)
        payload = {'readings': readings, 'alarms': alarms, 'last_updated': datetime.now().isoformat()}
        tmp = CURRENT + '.tmp'
        with open(tmp, 'w', encoding='utf-8') as f:
            json.dump(payload, f, indent=2)
        # retry replace
        for i in range(5):
            try:
                os.replace(tmp, CURRENT)
                break
            except PermissionError:
                time.sleep(0.1)
        gc.collect()
        time.sleep(3)

threading.Thread(target=update_loop, daemon=True).start()

@app.route('/')
def home():
    return send_from_directory(os.path.join(BASE, 'dashboard_ui'), 'index.html')

@app.route('/<path:p>')
def static_files(p):
    return send_from_directory(os.path.join(BASE, 'dashboard_ui'), p)

@app.route('/data')
def data():
    try:
        with open(CURRENT, 'r', encoding='utf-8') as f:
            payload = json.load(f)
    except:
        return jsonify({'readings': {}, 'alarms': ['❌ Waiting for data'], 'last_updated': None})
    return jsonify(payload)

if __name__ == '__main__':
    app.run(port=5000, debug=False)
