from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from agent_service import agent_query
from todo_service import get_tasks
from email_reminder_service import check_and_send_reminders
import asyncio

app = FastAPI()


async def reminder_background_task():
    """רץ ברקע ובודק תזכורות כל 5 דקות"""
    while True:
        check_and_send_reminders()
        await asyncio.sleep(300)  # 5 דקות


@app.on_event("startup")
async def startup_event():
    asyncio.create_task(reminder_background_task())

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Todo Agent API"}


class MessageRequest(BaseModel):
    message: str


@app.post("/agent")
async def agent(request: MessageRequest):
    return await agent_query(request.message)


@app.get("/tasks")
async def tasks():
    return get_tasks()