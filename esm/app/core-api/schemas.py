from typing import Optional

from pydantic import BaseModel


class JobBase(BaseModel):
    type: str
    uniprot_id: str
    fasta_text: str
    input_type: str


class JobResult(BaseModel):
    result_path: str


class JobCreate(JobBase):
    pass


class Job(JobBase):
    id: int
    start: Optional[int]
    end: Optional[int]
    status: Optional[str]
    result_path: Optional[str]

    class Config:
        orm_mode = True
