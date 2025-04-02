import logging

import psycopg2

from exceptions.webhook import InvalidEventStatusException, DuplicateTaskCreationException, TaskNotFoundException
from managers.data import DataManager
from schemas.webhook import WebhookPayload


class WebhookManager(DataManager):

    async def processWebhook(self, payload: WebhookPayload):
        if payload.event == "created":
            await self.createTask(payload)
        elif payload.event == "updated":
            if not await self.taskExists(payload):
                raise TaskNotFoundException()
            await self.updateTask(payload)
        elif payload.event == "deleted":
            if not await self.taskExists(payload):
                raise TaskNotFoundException()
            await self.deleteTask(payload)
        else:
            raise InvalidEventStatusException()

    async def createTask(self, payload: WebhookPayload):
        logging.debug(f"Creating task for id {payload.metadata.id} and userId {payload.metadata.userId}")
        try:
            sql = "INSERT INTO meetperry.task (external_id, user_id, content, created_date) VALUES (%s, %s, %s, %s);"
            data = [payload.metadata.id, payload.metadata.userId, payload.metadata.content, payload.timestamp]
            self.postgres.execute(sql, data)
        except psycopg2.errors.UniqueViolation as e:
            logging.error(f"Duplicate task creation for id {payload.metadata.id}: {e}")
            raise DuplicateTaskCreationException()


    async def updateTask(self, payload: WebhookPayload):
        if payload.metadata.isCompleted:
            logging.debug(f"updating task to complete for id {payload.metadata.id} and userId {payload.metadata.userId}")
            completed_date = payload.timestamp
            sql = "UPDATE meetperry.task SET completed_date = %s WHERE external_id = %s;"
            data = [completed_date, payload.metadata.id]
            self.postgres.execute(sql, data)

    async def deleteTask(self, payload: WebhookPayload):
        logging.debug(f"Deleting task for id {payload.metadata.id} and userId {payload.metadata.userId}")
        deleted_date = payload.timestamp
        sql = "UPDATE meetperry.task SET deleted_date = %s WHERE external_id = %s;"
        data = [deleted_date, payload.metadata.id]
        self.postgres.execute(sql, data)

    async def taskExists(self, payload: WebhookPayload):
        logging.debug(f"Retrieving task for id {payload.metadata.id}")
        sql = "SELECT EXISTS(SELECT 1 FROM meetperry.task WHERE external_id = %s);"
        data = [payload.metadata.id]
        return self.postgres.exists(sql, data)