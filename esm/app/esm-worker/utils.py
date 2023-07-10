import json

import requests

from config import Config


def finish_job(job_id: int, result_path: str):
    url = f"{Config.CORE_API_URL}/jobs/{job_id}/complete"
    data = {'result_path': result_path}
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    r = requests.post(url, data=json.dumps(data), headers=headers)

    if r.status_code == 200:
        print("Complete job successful")
    else:
        print("Cannot complete job")
