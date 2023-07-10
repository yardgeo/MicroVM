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
    start: int
    end: int
    status: str
    result_path: str

    class Config:
        orm_mode = True
