from typing import List, Dict, Optional
from datetime import datetime
from bson import ObjectId
import requests
import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

class ChatbotService:
    def __init__(self):
        self.azure_endpoint = "https://guidant.openai.azure.com/openai/deployments/gpt-35-turbo/chat/completions"
        self.api_version = "2024-02-15-preview"
        self.headers = {
            "Content-Type": "application/json",
            "api-key": os.getenv("AZURE_API_KEY")  # Store this in .env file
        }
        
        mongo_url = os.getenv("URL", "mongodb+srv://Arvind:Arvind@guidantai.dptv6.mongodb.net/")
        client = AsyncIOMotorClient(mongo_url)
        self.db = client.Guidant
        self.collection = self.db.Chatbot
        
    async def create_session(self, user_id: str) -> str:
        """Create a new chat session"""
        session_id = ObjectId() 
        session = {
            "_id": session_id,
            "user_id": user_id,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "messages": []
        }
        await self.collection.insert_one(session)
        return str(session_id)

    async def get_session(self, session_id: ObjectId) -> Optional[Dict]:
        """Retrieve a chat session"""
        session = await self.collection.find_one({"_id": ObjectId(session_id)})
        if session:
            session["_id"] = str(session["_id"])
        return session
    async def get_user_sessions(self, user_id: str) -> List[Dict]:
        """Get all chat sessions for a user"""
        cursor = self.collection.find({"user_id": user_id})
        return await cursor.to_list(length=None)

    def _prepare_messages(self, chat_history: List[Dict]) -> List[Dict]:
        """Prepare messages for OpenAI API"""
        return [
            {"role": msg["role"], "content": msg["content"]}
            for msg in chat_history
        ]

    async def send_message(self, session_id: str, user_message: str) -> Dict:
        """Send message and get response"""
        session = await self.get_session(session_id)
        if not session:
            raise ValueError("Invalid session ID")

        new_message = {
            "role": "user",
            "content": user_message,
            "timestamp": datetime.utcnow()
        }

        messages = self._prepare_messages(session["messages"] + [new_message])
        
        payload = {
            "messages": messages,
            "n": 1,
            "max_tokens": 800,
            "temperature": 0.7,
            "top_p": 0.95,
        }

        url = f"{self.azure_endpoint}?api-version={self.api_version}"
        response = requests.post(url, headers=self.headers, json=payload)
        
        if response.status_code != 200:
            raise Exception(f"Azure OpenAI API error: {response.text}")

        assistant_response = response.json()["choices"][0]["message"]["content"]
        
        assistant_message = {
            "role": "assistant",
            "content": assistant_response,
            "timestamp": datetime.utcnow()
        }

        await self.collection.update_one(
            {"_id": ObjectId(session_id)},
            {
                "$push": {"messages": {"$each": [new_message, assistant_message]}},
                "$set": {"updated_at": datetime.utcnow()}
            }
        )

        return {
            "session_id": session_id,
            "response": assistant_message["content"],
            "timestamp": assistant_message["timestamp"]
        }

    async def delete_session(self, session_id: str) -> bool:
        """Delete a chat session"""
        result = await self.chat_sessions.delete_one({"_id": ObjectId(session_id)})
        return result.deleted_count > 0

    async def clear_session_history(self, session_id: str) -> bool:
        """Clear messages from a chat session while maintaining the session"""
        result = await self.chat_sessions.update_one(
            {"_id": ObjectId(session_id)},
            {
                "$set": {
                    "messages": [],
                    "updated_at": datetime.utcnow()
                }
            }
        )
        return result.modified_count > 0
