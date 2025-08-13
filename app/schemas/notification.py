from pydantic import BaseModel, ConfigDict
from typing import Optional

class NotificationOut(BaseModel):
    id: int
    user_id: int
    task_id: Optional[int]
    message: str

    model_config = ConfigDict(from_attributes=True)
