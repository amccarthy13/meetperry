from pydantic import BaseModel


class WebhookMetadata(BaseModel):
    userId: str
    id: str
    content: str
    isCompleted: bool

class WebhookPayload(BaseModel):
    event: str
    timestamp: str
    metadata: WebhookMetadata

