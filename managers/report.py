import json
import logging
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

from domain.webhook import Task, Period, Report
from managers.data import DataManager


class ReportManager(DataManager):

    async def doReport(self, start_time: datetime):
        end_time = datetime.now(timezone.utc)

        new_incomplete_tasks = await self.getNewIncompleteTasks(start_time, end_time)
        completed_tasks = await self.getCompletedTasks(start_time, end_time)
        old_incomplete_tasks = await self.collectOldIncompleteTasks(start_time)

        user_ids = set(new_incomplete_tasks.keys()) | set(completed_tasks.keys()) | set(old_incomplete_tasks.keys())

        for user_id in user_ids:
            report = Report(
                userId=user_id,
                period=Period(start=start_time, end=end_time),
                newIncompleteTasks=new_incomplete_tasks.get(user_id, []),
                completedTasks=completed_tasks.get(user_id, []),
                oldIncompleteTasks=old_incomplete_tasks.get(user_id, [])
            )

            file_name = f"task_report_{user_id}_{start_time.isoformat()}_{end_time.isoformat()}.json"
            logging.debug(f"Generating report with name {file_name} with {len(new_incomplete_tasks)} new incomplete tasks, "
                          f"{len(completed_tasks)} completed tasks, and {len(old_incomplete_tasks)} old incomplete tasks.")
            file_path = Path(file_name)

            with open(file_path, "w") as f:
                json.dump(report.model_dump(), f, indent=2, default=str)

        return end_time

    async def getNewIncompleteTasks(self, start_time: datetime, end_time: datetime):
        sql = ("SELECT external_id, content, created_date, user_id FROM meetperry.task WHERE created_date <= %s "
               "AND created_date > %s AND completed_date IS NULL;")
        data = [end_time.isoformat(), start_time.isoformat()]
        rows = self.postgres.execute_many(sql, data)
        tasks = defaultdict(list)
        for row in rows:
            task: Task = Task(id=row[0], content=row[1], createdOrCompletedAt=row[2])
            user_id = row[3]
            tasks[user_id].append(task)

        return dict(tasks)

    async def getCompletedTasks(self, start_time: datetime, end_time: datetime):
        sql = ("SELECT external_id, content, completed_date, user_id FROM meetperry.task WHERE completed_date IS NOT NULL "
               "AND completed_date <= %s AND completed_date > %s;")
        data = [end_time, start_time]
        rows = self.postgres.execute_many(sql, data)
        tasks = defaultdict(list)
        for row in rows:
            task: Task = Task(id=row[0], content=row[1], createdOrCompletedAt=row[2])
            user_id = row[3]
            tasks[user_id].append(task)

        return dict(tasks)

    async def collectOldIncompleteTasks(self, start_time: datetime):
        sql = ("SELECT external_id, content, created_date, user_id FROM meetperry.task WHERE created_date < %s AND "
               "completed_date IS NULL;")
        data = [start_time]
        rows = self.postgres.execute_many(sql, data)
        tasks = defaultdict(list)
        for row in rows:
            task: Task = Task(id=row[0], content=row[1], createdOrCompletedAt=row[2])
            user_id = row[3]
            tasks[user_id].append(task)

        return dict(tasks)