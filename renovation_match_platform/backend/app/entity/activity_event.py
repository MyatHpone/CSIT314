from __future__ import annotations

from datetime import datetime

from app.services.database import db


class ActivityEvent:
    def __init__(self, actor_id: int | None, event_type: str, entity_type: str, entity_id: int | None = None):
        self.actor_id = actor_id
        self.event_type = event_type
        self.entity_type = entity_type
        self.entity_id = entity_id

    def log_event(self) -> int:
        return db.execute(
            "INSERT INTO activity_events(actor_id,event_type,entity_type,entity_id,occurred_at) VALUES(?,?,?,?,?)",
            (self.actor_id, self.event_type, self.entity_type, self.entity_id,
             datetime.now().isoformat(timespec="seconds")))

    @staticmethod
    def log(actor_id: int | None, event_type: str, entity_type: str, entity_id: int | None = None) -> int:
        return ActivityEvent(actor_id, event_type, entity_type, entity_id).log_event()
