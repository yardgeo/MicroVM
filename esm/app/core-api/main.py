import json
import os
from typing import List

import pika
import requests
from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware

import crud
import models
import schemas
from config import Config
from utils import download_structure_from_pdb
from database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


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


@app.post("/jobs/", response_model=schemas.Job)
async def create_job(job: schemas.JobCreate, db: Session = Depends(get_db)):
    created_job = crud.create_job(db=db, job=job)

    uniprot_id = created_job.uniprot_id
    job_id = created_job.id

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
        file_name = f"{Config.UNIPROT_DIR}/{job_id}/{uniprot_id}.fasta"
        with open(file_name, "w") as file:
            file.write(response.text)
    else:
        print(f"Failed to download FASTA file for UniProt ID: {uniprot_id}")

    # download pdb
    download_structure_from_pdb(uniprot_id, job_id)

    # make message
    message = {
        'job_id': job_id,
        'uniprot_id': uniprot_id,
        'type': created_job.type
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

    return created_job


@app.get("/jobs/{job_id}/", response_model=schemas.Job)
async def get_job(job_id: int, db: Session = Depends(get_db)):
    db_job = crud.get_job(db, job_id=job_id)
    if db_job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return db_job


@app.get("/jobs/", response_model=List[schemas.Job])
async def job_list(skip: int = 0,
                   limit: int = 100,
                   job_type: str = None,
                   db: Session = Depends(get_db)):
    return crud.get_jobs(db,
                         job_type=job_type,
                         skip=skip, limit=limit)


@app.post("/jobs/{job_id}/complete", response_model=schemas.Job)
async def complete_job(job_id: int,
                       job_result: schemas.JobResult,
                       db: Session = Depends(get_db)):
    return crud.complete_job(db, job_id, job_result)


@app.get("/jobs/{job_id}/results")
async def download_results(job_id: int, db: Session = Depends(get_db)):
    db_job = crud.get_job(db, job_id=job_id)
    if db_job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return FileResponse(db_job.result_path)


@app.delete("/jobs/{job_id}/")
async def delete_job(job_id: int):
    pass
