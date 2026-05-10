# fastapi sir is here, who will handle the chat messages and serves the frontend
# alos convo memory
# get FETCH, post SEND


import os
import sys
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# add server/ to path so agent and swiggy modules resolve correctly
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'server'))

from agent import run_agent
from swiggy import reset_cart

app = FastAPI()

# allow frontend to talk to backend without CORS issues
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

# serve the public folder as static files
app.mount("/static", StaticFiles(directory="public"), name="static")

# conversation history for the current session
# stores all messages so the agent has full context
conversation_history = []

class Message(BaseModel):
    user: str
    message: str

@app.get("/")
def root():
    # serve the chat UI
    return FileResponse("public/index.html")

@app.post("/chat")
async def chat(msg: Message):
    # add user message to history with their name
    conversation_history.append({
        "role": "user",
        "content": f"{msg.user} says: {msg.message}"
    })

    # run the agent with full history
    reply = run_agent(conversation_history)

    # add agent reply to history so context is preserved
    conversation_history.append({
        "role": "assistant",
        "content": reply
    })

    return {"reply": reply}


@app.post("/reset")
async def reset():
    # clears everything — useful between demo takes
    conversation_history.clear()
    reset_cart()
    return {"status": "session reset"}


@app.get("/history")
async def get_history():
    # handy for debugging, can remove before recording demo
    return {"history": conversation_history}