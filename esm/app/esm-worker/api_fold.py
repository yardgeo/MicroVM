import requests


def esm_fold_pdb_api(sequence: str, file_name: str):
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
    }

    data = sequence

    r = requests.post('https://api.esmatlas.com/foldSequence/v1/pdb/',
                      headers=headers, data=data)

    if r.status_code == 200:
        with open(file_name, "wb") as file:
            file.write(r.content)
        print("Complete job successful")
    else:
        print("Cannot complete job")
