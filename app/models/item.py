from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class Item(SQLModel, table=True):
    item_id: Optional[str] = Field(default=None, primary_key=True)
    url: str
    text: str
    added: Optional[datetime] = None
