from sqlalchemy import Column, Integer, String, Text

from database import Base


class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    start = Column(Integer)
    end = Column(Integer, nullable=True)
    status = Column(String)
    input_type = Column(String)
    type = Column(String)
    uniprot_id = Column(String)
    fasta_text = Column(Text)
    result_path = Column(String, nullable=True)
