import json
import os
import time

import requests

from config import Config


def check_files_existence(file1, file2):
    start_time = time.time()
    elapsed_time = 0

    while elapsed_time < Config.TIME_LIMIT:
        if os.path.isfile(file1) and os.path.isfile(file2):
            print("Both files exist.")
            break

        time.sleep(Config.TIME_SLEEP)
        elapsed_time = time.time() - start_time

    if elapsed_time >= Config.TIME_LIMIT:
        print("Time limit exceeded.")
        return False
    else:
        print("Loop stopped.")
        return True


def finish_job(job_id: int, result_path: str):
    url = f"{Config.CORE_API_URL}/jobs/{job_id}/complete"
    data = {'result_path': result_path}
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    r = requests.post(url, data=json.dumps(data), headers=headers)

    if r.status_code == 200:
        print("Complete job successful")
    else:
        print(r.reason, "Cannot complete job")
