import requests


def retrieve_pdb_id(uniprot_id):
    # Define the UniProt API endpoint
    api_url = f"https://www.uniprot.org/uniprot/{uniprot_id}.xml"

    try:
        # Send GET request to the API endpoint
        response = requests.get(api_url)

        if response.status_code == 200:
            # Parse the XML response
            xml_data = response.text

            # Extract the PDB ID from the XML data
            pdb_id = extract_pdb_id(xml_data)

            if pdb_id:
                print(
                    f"PDB ID retrieved for UniProt ID: {uniprot_id} is {pdb_id}")
            else:
                print(f"No PDB ID found for UniProt ID: {uniprot_id}")
        else:
            print(f"Failed to retrieve PDB ID for UniProt ID: {uniprot_id}")

    except requests.exceptions.RequestException as e:
        print(f"Error occurred during the request: {e}")


def extract_pdb_id(xml_data):
    # Extract the PDB ID from the XML data
    start_index = xml_data.find('<dbReference type="PDB" id="')
    if start_index != -1:
        start_index += len('<dbReference type="PDB" id="')
        end_index = xml_data.find('"', start_index)
        pdb_id = xml_data[start_index:end_index]
        return pdb_id
    else:
        return None


# Specify the UniProt ID of the protein
uniprot_id = "A1A4S6"

# Retrieve the PDB ID
retrieve_pdb_id(uniprot_id)
