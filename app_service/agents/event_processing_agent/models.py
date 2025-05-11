from pydantic import BaseModel, Field
from datetime import datetime
from typing import Dict, Any, Optional
import json
from uuid import UUID

class Event(BaseModel):
    id: int
    vendor_id: str
    location_uuid: str
    event_trigger_point: str
    event_details_text: Dict[str, Any]
    event_location_latitude: float
    event_location_longitude: float
    event_timestamp: datetime
    processed_for_suggestion: bool = False
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_db_record(cls, record: dict):
        """Create an Event instance from a database record"""
        data = dict(record)
        
        # Convert UUID to string
        if isinstance(data.get('location_uuid'), UUID):
            data['location_uuid'] = str(data['location_uuid'])
            
        # Parse JSON string to dict if needed
        if isinstance(data.get('event_details_text'), str):
            try:
                data['event_details_text'] = json.loads(data['event_details_text'])
            except json.JSONDecodeError:
                data['event_details_text'] = {}
        
        # Ensure timestamps are datetime objects
        for field in ['event_timestamp', 'created_at', 'updated_at']:
            if field in data and not isinstance(data[field], datetime):
                try:
                    if isinstance(data[field], str):
                        data[field] = datetime.fromisoformat(data[field].replace('Z', '+00:00'))
                    elif isinstance(data[field], (int, float)):
                        data[field] = datetime.fromtimestamp(data[field])
                except (ValueError, TypeError):
                    data[field] = datetime.utcnow()
                
        return cls(**data) 