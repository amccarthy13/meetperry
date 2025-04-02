from datetime import datetime
from typing import List

from pydantic import BaseModel

class Period(BaseModel):
    start: datetime
    end: datetime

class Task(BaseModel):
    id: str
    content: str
    createdOrCompletedAt: datetime

class Report(BaseModel):
    userId: str
    period: Period
    newIncompleteTasks: List[Task]
    completedTasks: List[Task]
    oldIncompleteTasks: List[Task]
