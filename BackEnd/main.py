# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from checkin import router as checkin_router
from chat import router as chat_router # <--- CHANGE/ADD THIS LINE

app = FastAPI()

# Your origins list and CORSMiddleware setup
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(checkin_router, prefix="/api", tags=["checkin"])
app.include_router(chat_router, prefix="/api", tags=["chat"]) # <--- AND ADD THIS LINE