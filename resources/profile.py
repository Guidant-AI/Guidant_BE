from fastapi import APIRouter, HTTPException, Depends
from pymongo import MongoClient
from models.user import Profile
from bson import ObjectId
from typing import Optional 
from datetime import datetime

router = APIRouter()

client = MongoClient("mongodb+srv://Arvind:Arvind@guidantai.dptv6.mongodb.net/")
db = client["Guidant"]
user_collection = db["User_details"]

@router.put("/{user_id}")
async def update_profile(user_id: str, request: Profile):
    """Update profile for the user by user_id"""
    try:
        user = user_collection.find_one({"_id": ObjectId(user_id)})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        update_data = request.dict(exclude_unset=True)
        update_data["updated_on"] = datetime.utcnow()

        is_complete = True
        for field in ["first_name", "last_name", "class_name", "city", "state", "gender", "email"]:
            if not update_data.get(field):
                is_complete = False
                break
        
        update_data["isComplete"] = is_complete

        result = user_collection.update_one({"_id": ObjectId(user_id)}, {"$set": update_data})

        if result.modified_count == 0:
            raise HTTPException(status_code=400, detail="No changes made to the profile")

        return {"success": True, "message": "Profile updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))