from typing import List, Optional
from sqlalchemy.orm import Session
from datetime import datetime

from app.models.crawl import CrawlRun


class CrawlRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, run: CrawlRun) -> CrawlRun:
        self.db.add(run)
        self.db.commit()
        self.db.refresh(run)
        return run

    def update(self, run: CrawlRun) -> CrawlRun:
        self.db.add(run)
        self.db.commit()
        self.db.refresh(run)
        return run

    def list_history(self, limit: int = 100) -> List[CrawlRun]:
        return self.db.query(CrawlRun).order_by(CrawlRun.start_time.desc()).limit(limit).all()

    def last_run_for_country(self, country_code: str) -> Optional[CrawlRun]:
        return (
            self.db.query(CrawlRun)
            .filter(CrawlRun.country_code == country_code)
            .order_by(CrawlRun.start_time.desc())
            .first()
        )

    def list_running(self) -> List[CrawlRun]:
        return self.db.query(CrawlRun).filter(CrawlRun.status == "running").all()
