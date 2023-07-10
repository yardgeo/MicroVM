import os


class Config:
    PDB_DIR = os.getenv("PDB_DIR")
    AF_DIR = os.getenv("AF_DIR")
    ESM_DIR = os.getenv("ESM_DIR")
    UNIPROT_DIR = os.getenv("UNIPROT_DIR")
    RESULTS_DIR = os.getenv("RESULTS_DIR")
    RABBITMQ_HOST = os.getenv("RABBITMQ_HOST")
    RABBITMQ_ESM_QUEUE = os.getenv("RABBITMQ_ESM_QUEUE")
    RABBITMQ_AF_QUEUE = os.getenv("RABBITMQ_AF_QUEUE")
    RABBITMQ_RESULTS_QUEUE = os.getenv("RABBITMQ_RESULTS_QUEUE")
    DATABASE_URL = os.getenv("DATABASE_URL")
    STATUS_RUNNING = os.getenv("STATUS_RUNNING", "RUNNING")
    STATUS_COMPLETED = os.getenv("STATUS_COMPLETED", "COMPLETED")
    BASE_URL = os.getenv("BASE_URL", "")
    CORE_API_URL = os.getenv("CORE_API_URL",
                             "https://cloud-vm84.cloud.cnaf.infn.it/api/")
