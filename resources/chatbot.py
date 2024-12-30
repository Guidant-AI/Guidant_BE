from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
from services.chatbotService import ChatbotService

router = APIRouter()

chatbot_service = ChatbotService()

class CreateSessionRequest(BaseModel):
    user_id: str

class SendMessageRequest(BaseModel):
    session_id: str
    user_message: str

class ChatbotResponse(BaseModel):
    session_id: str
    response: str
    timestamp: datetime

class DeleteSessionRequest(BaseModel):
    session_id: str

class ClearHistoryRequest(BaseModel):
    session_id: str

@router.post("/create_session", response_model=dict, summary="Create a new chat session")
async def create_session(request: CreateSessionRequest):
    response = {"status": 200, "message": "success", "data": [], "error": ""}
    try:
        session_id = await chatbot_service.create_session(request.user_id)
        response["data"] = {"session_id": session_id}
        return response
    except Exception as e:
        response.update({"status": 500, "message": "failure", "error": str(e)})
        return response

@router.get("/get_session/{session_id}", response_model=dict, summary="Retrieve chat session")
async def get_session(session_id: str):
    response = {"status": 200, "message": "success", "data": [], "error": ""}
    try:
        session = await chatbot_service.get_session(session_id)
        if not session:
            response.update({"status": 404, "message": "failure", "error": "Session not found"})
        else:
            response["data"] = session
        return response
    except Exception as e:
        response.update({"status": 500, "message": "failure", "error": str(e)})
        return response

@router.get("/get_user_sessions/{user_id}", response_model=dict, summary="Retrieve all user chat sessions")
async def get_user_sessions(user_id: str):
    response = {"status": 200, "message": "success", "data": [], "error": ""}
    try:
        sessions = await chatbot_service.get_user_sessions(user_id)
        response["data"] = sessions
        return response
    except Exception as e:
        response.update({"status": 500, "message": "failure", "error": str(e)})
        return response

@router.post("/send_message", response_model=dict, summary="Send a message to the chatbot")
async def send_message(request: SendMessageRequest):
    """
    Send a user message to the chatbot and get a response.
    """
    response = {"status": 200, "message": "success", "data": [], "error": ""}

    try:
        answer = await chatbot_service.send_message(request.session_id, request.user_message)
        response["data"] = answer 
        return response
    except ValueError as e:
        response["status"] = 400
        response["message"] = "Bad Request"
        response["error"] = str(e)
        return response
    except Exception as e:
        response["status"] = 500
        response["message"] = "Internal Server Error"
        response["error"] = str(e)
        return response
@router.delete("/delete_session", response_model=dict, summary="Delete a chat session")
async def delete_session(request: DeleteSessionRequest):
    response = {"status": 200, "message": "success", "data": [], "error": ""}
    try:
        result = await chatbot_service.delete_session(request.session_id)
        if not result:
            response.update({"status": 404, "message": "failure", "error": "Session not found"})
        else:
            response["data"] = {"deleted": True}
        return response
    except Exception as e:
        response.update({"status": 500, "message": "failure", "error": str(e)})
        return response

@router.post("/clear_history", response_model=dict, summary="Clear chat session history")
async def clear_history(request: ClearHistoryRequest):
    response = {"status": 200, "message": "success", "data": [], "error": ""}
    try:
        result = await chatbot_service.clear_session_history(request.session_id)
        if not result:
            response.update({"status": 404, "message": "failure", "error": "Session not found"})
        else:
            response["data"] = {"history_cleared": True}
        return response
    except Exception as e:
        response.update({"status": 500, "message": "failure", "error": str(e)})
        return response
