from datetime import datetime

from pydantic import BaseModel


class User(BaseModel):
    name: str
    session: str
    username: str
    expiration: datetime
