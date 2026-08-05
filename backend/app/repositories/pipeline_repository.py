from sqlalchemy.orm import Session
from typing import List, Optional

from app.models.processing import ProcessingJob


class PipelineRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_job(self, job: ProcessingJob) -> ProcessingJob:
        self.db.add(job)
        self.db.commit()
        self.db.refresh(job)
        return job

    def update_job(self, job: ProcessingJob) -> ProcessingJob:
        self.db.add(job)
        self.db.commit()
        self.db.refresh(job)
        return job

    def get_job(self, job_id: int) -> Optional[ProcessingJob]:
        return self.db.get(ProcessingJob, job_id)

    def list_jobs(self, limit: int = 100) -> List[ProcessingJob]:
        return self.db.query(ProcessingJob).order_by(ProcessingJob.start_time.desc()).limit(limit).all()
