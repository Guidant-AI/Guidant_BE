from typing import Dict, List, Literal, Optional
from datetime import datetime
from bson import ObjectId
import requests
import os
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

load_dotenv()

class SummarizerService:
    def __init__(self):
        self.azure_endpoint = "https://guidant.openai.azure.com/openai/deployments/gpt-35-turbo/chat/completions"
        self.api_version = "2024-02-15-preview"
        self.headers = {
            "Content-Type": "application/json",
            "api-key": os.getenv("AZURE_API_KEY")
        }

        
        mongo_url = os.getenv("URL", "mongodb+srv://Arvind:Arvind@guidantai.dptv6.mongodb.net/")
        client = AsyncIOMotorClient(mongo_url)
        self.db = client.Guidant
        self.collection = self.db.Summarizer

    async def generate_summary(
        self,
        text: str,
        summary_type: Literal["bullet", "paragraph", "auto_write"]
    ) -> Dict:
        try:
            # Create appropriate prompt based on summary type
            if summary_type == "bullet":
                prompt = f"""Create a bullet-point summary of the following text. 
                Focus on key points and main ideas.
                Format as a list with '-' bullets.
                Keep each point concise (max 15 words per point).
                Include 5-7 main points.

                Text to summarize:
                {text}"""
            elif summary_type == "paragraph":
                prompt = f"""Create a coherent paragraph summary of the following text.
                Capture main ideas and key arguments.
                Keep it concise (max 150 words).
                Use clear transitions between ideas.
                Maintain the original text's tone.

                Text to summarize:
                {text}"""
            else:  # auto_write
                prompt = f"""Rewrite and expand the following text while maintaining its core message.
                Add relevant examples and explanations.
                Use a natural, engaging writing style.
                Organize ideas logically with proper transitions.
                Aim for approximately 50% more content than the original.

                Text to expand:
                {text}"""

            # Prepare payload for Azure OpenAI
            payload = {
                "messages": [
                    {"role": "system", "content": "You are an expert summarizer."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.3,
                "max_tokens": 800,
                "top_p": 0.7,
            }

            url = f"{self.azure_endpoint}?api-version={self.api_version}"
            response = requests.post(url, headers=self.headers, json=payload)
            
            if response.status_code != 200:
                raise Exception(f"Azure OpenAI API error: {response.text}")

            summary = response.json()["choices"][0]["message"]["content"]
            
            return {
                "success": True,
                "content": summary,
                "original_length": len(text),
                "new_length": len(summary)
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    async def create_summary(
        self,
        user_id: str,
        task_id: str,
        text: str,
        summary_type: Literal["bullet", "paragraph", "auto_write"]
    ) -> Dict:
        """Generate and store summary based on type"""
        try:
            # Generate the summary
            summary_result = await self.generate_summary(text, summary_type)
            
            if not summary_result["success"]:
                return summary_result
            
            # Prepare document for MongoDB
            summary_doc = {
                "user_id": user_id,
                "task_id": task_id,
                "original_text": text,
                "summary": summary_result["content"],
                "summary_type": summary_type,
                "metadata": {
                    "original_length": summary_result["original_length"],
                    "summary_length": summary_result["new_length"]
                },
                "created_at": datetime.utcnow()
            }
            
            result = await self.collection.insert_one(summary_doc)
            summary_doc["_id"] = str(result.inserted_id)
            
            return {
                "success": True,
                "summary_id": str(result.inserted_id),
                "content": summary_result["content"],
                "type": summary_type,
                "timestamp": summary_doc["created_at"]
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    async def get_summary_history(self, user_id: str, task_id: Optional[str] = None) -> List[Dict]:
        """Get summary history for a user, optionally filtered by task_id"""
        query = {"user_id": user_id}
        if task_id:
            query["task_id"] = task_id

        try:
            cursor = self.collection.find(query)
            history = []
            async for document in cursor:
                document["_id"] = str(document["_id"])
                history.append(document)

            return history

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
