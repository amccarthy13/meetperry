
from fastapi import APIRouter, Request, HTTPException
from starlette import status

from exceptions.webhook import DuplicateTaskCreationException, InvalidEventStatusException, TaskNotFoundException, \
    TaskInvalidStatusException
from managers.webhook import WebhookManager
from schemas.webhook import WebhookPayload

webhook_router = APIRouter()

@webhook_router.post("/webhook",
                     summary="Accept webhook requests from the TODO service",
                     status_code=status.HTTP_202_ACCEPTED,
                     name="webhook:accept:post")
async def webhook_accept(request: Request, webhook: WebhookPayload):
    mgr = WebhookManager(postgres=request.app.state.postgres)
    try:
        await mgr.processWebhook(webhook)
    except DuplicateTaskCreationException:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Duplicate task creation")
    except InvalidEventStatusException:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid event status")
    except TaskNotFoundException:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    except TaskInvalidStatusException:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid event status")
