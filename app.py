import asyncio
import logging
import os
from datetime import datetime, timedelta, timezone

from uvicorn import Server, Config
from fastapi import FastAPI

from managers.report import ReportManager
from resources.postgres import PostgreSQL
from routes.webhook import webhook_router


NAME = "meet-perry"
HTTP_PORT = int(os.getenv("HTTP_PORT", "8000"))
REPORT_INTERVAL_SECONDS = int(os.getenv("REPORT_INTERVAL_SECONDS", "15"))

async def report_scheduler(app: FastAPI):
    logging.info(f"Report scheduler started using {REPORT_INTERVAL_SECONDS} second intervals.")
    last_run = datetime.now(timezone.utc) - timedelta(seconds=REPORT_INTERVAL_SECONDS)

    while True:
        try:
            reporter = ReportManager(postgres=app.state.postgres)
            end_time = await reporter.doReport(last_run)
            last_run = end_time
        except Exception as e:
            logging.exception("Report generation failed with exception: %s", e)
        await asyncio.sleep(REPORT_INTERVAL_SECONDS)

def get_application() -> FastAPI:
    app = FastAPI()

    postgres = PostgreSQL()
    postgres.set_db_connection()
    setattr(app.state, "postgres", postgres)
    app.include_router(webhook_router)
    return app

app = get_application()

async def main():
    asyncio.create_task(report_scheduler(app))

    logging.info(f"Starting up {NAME}")
    server = Server(Config(app, host="0.0.0.0", port=HTTP_PORT, lifespan="on"))
    await server.serve()

if __name__ == "__main__":
    asyncio.run(main())
