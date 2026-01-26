import subprocess
import sys
import time
import requests
import tempfile
import os
import signal


def start_server(env=None, port=8003):
    python = sys.executable
    cmd = [python, '-m', 'uvicorn', 'app.main:app', '--port', str(port)]
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env)
    return proc


def wait_for_server(port=8003, timeout=10.0):
    url = f'http://127.0.0.1:{port}/openapi.json'
    start = time.time()
    while time.time() - start < timeout:
        try:
            r = requests.get(url, timeout=1.0)
            if r.status_code == 200:
                return True
        except Exception:
            pass
        time.sleep(0.2)
    return False


def test_end_to_end(tmp_path):
    # create isolated data dir
    data_dir = tmp_path / 'data'
    data_dir.mkdir()
    env = os.environ.copy()
    env['BUDGETBUDDY_DATA_DIR'] = str(data_dir)

    proc = start_server(env=env, port=8003)
    try:
        assert wait_for_server(port=8003, timeout=10.0)
        base = 'http://127.0.0.1:8003'
        # load sample payload
        here = os.path.dirname(os.path.abspath(__file__))
        sample_path = os.path.join(here, '..', 'data', 'sample_user.json')
        with open(sample_path, 'r', encoding='utf-8') as f:
            payload = f.read()
        json_payload = payload
        r = requests.post(base + '/ingest', json=__import__('json').loads(json_payload), timeout=5)
        assert r.status_code == 200

        plan_req = {"user_id": "user_123", "months": 3}
        r2 = requests.post(base + '/plan', json=plan_req, timeout=10)
        assert r2.status_code == 200
        data = r2.json()
        assert data['user_id'] == 'user_123'
        assert 'plan' in data

        creq = {"user_id": "user_123", "tone": "friendly", "format": "letter"}
        r3 = requests.post(base + '/creative', json=creq, timeout=10)
        assert r3.status_code == 200
        cdata = r3.json()
        assert cdata['user_id'] == 'user_123'
        assert 'creative' in cdata

    finally:
        # terminate server
        proc.terminate()
        try:
            proc.wait(timeout=3)
        except Exception:
            proc.kill()
