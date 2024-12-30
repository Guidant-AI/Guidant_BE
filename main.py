from fastapi import FastAPI
from resources.test import router
from resources.auth import router as auth_router 
from resources.profile import router as profile_router
from resources.summarizer import router as summarizer_router
from resources.chatbot import router as chatbot_router

app = FastAPI(title="Root API")

app.include_router(router, prefix="/api", tags=["Test"])
app.include_router(auth_router, prefix="/api/auth", tags=["Auth"])
app.include_router(profile_router, prefix="/api/update-profile", tags=["Profile"])
app.include_router(summarizer_router, prefix="/api/summarizer", tags=["Summarizer"])
app.include_router(chatbot_router, prefix="/api/chatbot", tags=["Chatbot"])


@app.get("/")
def root():
    return {"status": 200, "message": "success", "data": [], "error": ""}

