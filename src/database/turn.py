from typing import Optional
from sqlmodel import SQLModel, Field
from datetime import datetime


class Turn(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    started_at: datetime = Field(default_factory=datetime.utcnow)
    ends_at: datetime
