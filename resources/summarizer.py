from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Literal
from motor.motor_asyncio import AsyncIOMotorClient
from services.summarizerService import SummarizerService

client = AsyncIOMotorClient("mongodb+srv://Arvind:Arvind@guidantai.dptv6.mongodb.net/")
db = client["Guidant"]

summarizer_service = SummarizerService()

router = APIRouter()

class SummaryRequest(BaseModel):
    user_id: str
    task_id: str
    text: str
    summary_type: Literal["bullet", "paragraph", "auto_write"]

@router.post("/", tags=["Summarizer"])
async def summarize_endpoint(request: SummaryRequest):
    response = {"status": 200, "message": "success", "data": [], "error": ""}

    try:
        result = await summarizer_service.create_summary(
            user_id=request.user_id,
            task_id=request.task_id,
            text=request.text,
            summary_type=request.summary_type
        )
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["error"])
        response["data"] = result
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{user_id}", tags=["Summarizer"])
async def summaries_endpoint(user_id: str, task_id: Optional[str] = None):
    response = {"status": 200, "message": "success", "data": [], "error": ""}
    try:
        history = await summarizer_service.get_summary_history(user_id, task_id)
        response["data"] = history
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
