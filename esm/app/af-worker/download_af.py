import json

import requests


def download_model(uniprot_id, job_id, output_directory):
    # Send a GET request to the AlphaFold API
    url = f"https://alphafold.ebi.ac.uk/api/prediction/{uniprot_id}"
    response = requests.get(url)

    if response.status_code == 200:
        data = json.loads(response.content)

        # Check if the response contains the structure prediction
        if "pdbUrl" in data[0]:
            pdb_url = data[0]["pdbUrl"]

            # Download the AlphaFold structure prediction
            response = requests.get(pdb_url)

            if response.status_code == 200:
                # Save the structure prediction to a file
                file_name = f"{output_directory}/{job_id}/{uniprot_id}.pdb"
                with open(file_name, "w") as file:
                    file.write(response.content)
                print(
                    f"Downloaded AlphaFold structure prediction for UniProt ID: {uniprot_id}")
            else:
                print(
                    f"Failed to download AlphaFold structure prediction for UniProt ID: {uniprot_id}")
        else:
            print(
                f"No structure prediction available for UniProt ID: {uniprot_id}")
