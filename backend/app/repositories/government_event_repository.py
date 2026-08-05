from typing import List, Optional
from datetime import datetime

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from app.models.government_event import GovernmentEvent
from app.models.evidence import Evidence


class GovernmentEventRepository:
    """Repository for storing and querying GovernmentEvent records."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def save(self, event: GovernmentEvent) -> GovernmentEvent:
        """Persist a GovernmentEvent and return the refreshed instance."""
        self.db.add(event)
        self.db.commit()
        self.db.refresh(event)
        return event

    def get_by_company(self, company_id: str) -> List[GovernmentEvent]:
        """Return all events associated with a given company (via Evidence.company_id)."""
        return (
            self.db.query(GovernmentEvent)
            .join(GovernmentEvent.evidence)
            .filter(Evidence.company_id == company_id)
            .order_by(GovernmentEvent.event_date.desc(), GovernmentEvent.id)
            .all()
        )

    def get_by_project(self, project_id: str) -> List[GovernmentEvent]:
        """Return all events associated with a given project (via Evidence.project_id)."""
        return (
            self.db.query(GovernmentEvent)
            .join(GovernmentEvent.evidence)
            .filter(Evidence.project_id == project_id)
            .order_by(GovernmentEvent.event_date.desc(), GovernmentEvent.id)
            .all()
        )

    def get_by_country(self, country_id: str) -> List[GovernmentEvent]:
        """Return events for the given country. Matches either GovernmentEvent.country_id or the linked Evidence.country_id."""
        return (
            self.db.query(GovernmentEvent)
            .outerjoin(GovernmentEvent.evidence)
            .filter(
                or_(
                    GovernmentEvent.country_id == country_id,
                    Evidence.country_id == country_id,
                )
            )
            .order_by(GovernmentEvent.event_date.desc(), GovernmentEvent.id)
            .all()
        )

    def get_by_date_range(self, start: datetime, end: datetime) -> List[GovernmentEvent]:
        """Return events whose event_date falls in the given inclusive range.

        If event_date is NULL, falls back to using detected_date.
        """
        return (
            self.db.query(GovernmentEvent)
            .filter(
                or_(
                    and_(GovernmentEvent.event_date >= start, GovernmentEvent.event_date <= end),
                    and_(GovernmentEvent.event_date == None, GovernmentEvent.detected_date >= start, GovernmentEvent.detected_date <= end),
                )
            )
            .order_by(GovernmentEvent.event_date.asc(), GovernmentEvent.detected_date.asc())
            .all()
        )

    def timeline(self, entity_id: str, entity_type: str) -> List[GovernmentEvent]:
        """Return a chronological timeline of events for an entity.

        entity_type supports: 'company', 'project', 'country'. When 'country' both
        GovernmentEvent.country_id and Evidence.country_id are considered. For unknown
        entity_type all events are returned ordered by date.
        """
        q = self.db.query(GovernmentEvent).outerjoin(GovernmentEvent.evidence)

        if entity_type == "company":
            q = q.filter(Evidence.company_id == entity_id)
        elif entity_type == "project":
            q = q.filter(Evidence.project_id == entity_id)
        elif entity_type == "country":
            q = q.filter(or_(GovernmentEvent.country_id == entity_id, Evidence.country_id == entity_id))

        return q.order_by(GovernmentEvent.event_date.asc(), GovernmentEvent.detected_date.asc(), GovernmentEvent.id).all()
