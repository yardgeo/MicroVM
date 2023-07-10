import time

from sqlalchemy.orm import Session

import models
import schemas
from config import Config


def get_job(db: Session, job_id: int) -> models.Job:
    return db.query(models.Job).filter(models.Job.id == job_id).first()


def get_jobs(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Job).offset(skip).limit(limit).all()


def complete_job(db: Session, job_id: int, job_result: schemas.JobResult):
    job = get_job(db, job_id)
    job.status = Config.STATUS_COMPLETED
    job.end = int(time.time())
    job.result_path = job_result.result_path
    job.download_url = f"{Config.PROD_CORE_API_URL}/jobs/{job_id}/results"
    db.add(job)
    db.commit()
    db.refresh(job)
    return job


def create_job(db: Session, job: schemas.JobCreate):
    db_job = models.Job(start=int(time.time()),
                        status=Config.STATUS_RUNNING,
                        uniprot_id=job.uniprot_id,
                        fasta_text=job.fasta_text,
                        input_type=job.input_type,
                        type=job.type)
    db.add(db_job)
    db.commit()
    db.refresh(db_job)
    return db_job
