import os
import uuid
import json

import pika
import requests
from fastapi import FastAPI
from pydantic import BaseModel

from config import Config
from utils import download_structure_from_pdb


class CreateJobModel(BaseModel):
    uniprotId: str


app = FastAPI()

# RabbitMQ connection parameters
RABBITMQ_HOST = Config.RABBITMQ_HOST
RABBITMQ_ESM_QUEUE = Config.RABBITMQ_ESM_QUEUE
RABBITMQ_AF_QUEUE = Config.RABBITMQ_AF_QUEUE
RABBITMQ_RESULTS_QUEUE = Config.RABBITMQ_RESULTS_QUEUE

# Establish connection to RabbitMQ server
connection = pika.BlockingConnection(
    pika.ConnectionParameters(host=RABBITMQ_HOST))
channel = connection.channel()

# Declare the queue
channel.queue_declare(queue=RABBITMQ_ESM_QUEUE)
channel.queue_declare(queue=RABBITMQ_AF_QUEUE)
channel.queue_declare(queue=RABBITMQ_RESULTS_QUEUE)


@app.post("/jobs/")
async def create_job(model: CreateJobModel):
    uniprot_id = model.uniprotId
    job_id = str(uuid.uuid4())

    # create sub_dirs
    os.makedirs(f"{Config.PDB_DIR}/{job_id}", exist_ok=True)
    os.makedirs(f"{Config.AF_DIR}/{job_id}", exist_ok=True)
    os.makedirs(f"{Config.ESM_DIR}/{job_id}", exist_ok=True)
    os.makedirs(f"{Config.UNIPROT_DIR}/{job_id}", exist_ok=True)
    os.makedirs(f"{Config.RESULTS_DIR}/{job_id}", exist_ok=True)

    # download fasta file from Uniprot
    url = f"https://www.uniprot.org/uniprot/{uniprot_id}.fasta"

    # Send a GET request to download the FASTA file
    response = requests.get(url)

    if response.status_code == 200:
        # Save the downloaded FASTA file
        file_name = f"{Config.UNIPROT_DIR}/{job_id}/protein.fasta"
        with open(file_name, "w") as file:
            file.write(response.text)
    else:
        print(f"Failed to download FASTA file for UniProt ID: {uniprot_id}")

    # download pdb
    download_structure_from_pdb(uniprot_id, job_id)

    # make message
    message = {
        'job_id': job_id,
        'uniprot_id': uniprot_id
    }

    # run async jobs
    channel.basic_publish(exchange='',
                          routing_key=RABBITMQ_ESM_QUEUE,
                          body=json.dumps(message))

    channel.basic_publish(exchange='',
                          routing_key=RABBITMQ_AF_QUEUE,
                          body=json.dumps(message))

    channel.basic_publish(exchange='',
                          routing_key=RABBITMQ_RESULTS_QUEUE,
                          body=json.dumps(message))

    print(f"Message sent with job ID: {job_id}")

    return {"jobId": job_id}


@app.get("/jobs/{job_id}/status")
async def job_status(job_id: str):
    esm_pdb_ready = os.path.isfile(
        f"{Config.RESULTS_DIR}/{job_id}/esm_pdb.html")
    af_pdb_ready = os.path.isfile(f"{Config.RESULTS_DIR}/{job_id}/af_pdb.html")
    esm_af_ready = os.path.isfile(f"{Config.RESULTS_DIR}/{job_id}/esm_af.html")
    return {"ESM_PDB_Ready": esm_pdb_ready,
            "AF_PDB_Ready": af_pdb_ready,
            "ESM_AF_Ready": esm_af_ready}
