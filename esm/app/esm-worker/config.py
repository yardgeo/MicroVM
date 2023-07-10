import os


class Config:
    PDB_DIR = os.getenv("PDB_DIR")
    AF_DIR = os.getenv("AF_DIR")
    ESM_DIR = os.getenv("ESM_DIR")
    UNIPROT_DIR = os.getenv("UNIPROT_DIR")
    RESULTS_DIR = os.getenv("RESULTS_DIR")
    RABBITMQ_HOST = os.getenv("RABBITMQ_HOST")
    RABBITMQ_ESM_QUEUE = os.getenv("RABBITMQ_ESM_QUEUE")
    ALLOWED_TYPES = ['esm', 'foldseek']
    FINISH_TYPE = 'esm'
    CORE_API_URL = os.getenv("CORE_API_URL")
