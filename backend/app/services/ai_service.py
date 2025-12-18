from typing import List, Optional
import openai
from app.core.config import settings


class AIService:
    def __init__(self):
        self.client = openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.OPENAI_MODEL
    
    async def generate_reply(self, messages: List, context: Optional[str] = None) -> dict:
        conversation = "\n".join([f"{m.direction}: {m.content}" for m in messages])
        
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a helpful customer service assistant. Generate a professional, friendly reply."},
                {"role": "user", "content": f"Conversation:\n{conversation}\n\nGenerate a reply:"}
            ],
            max_tokens=500
        )
        
        return {
            "content": response.choices[0].message.content,
            "confidence": 85,
            "alternatives": []
        }
    
    async def suggest_actions(self, messages: List) -> List[dict]:
        return [
            {"action": "reply", "description": "Send a response", "priority": "high"},
            {"action": "tag", "description": "Add relevant tags", "priority": "medium"}
        ]
    
    async def summarize_conversation(self, messages: List) -> dict:
        conversation = "\n".join([f"{m.direction}: {m.content}" for m in messages])
        
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "Summarize this conversation concisely."},
                {"role": "user", "content": conversation}
            ],
            max_tokens=300
        )
        
        return {
            "summary": response.choices[0].message.content,
            "key_points": [],
            "sentiment": "neutral"
        }
    
    async def extract_order_intent(self, content: str) -> dict:
        return {"has_order_intent": False, "items": [], "total_estimate": None, "confidence": 50}
    
    async def categorize_message(self, content: str) -> dict:
        return {"category": "general", "subcategory": None, "confidence": 70, "tags": []}
    
    async def chat(self, message: str) -> str:
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are GhostWorker AI assistant. Help with business tasks."},
                {"role": "user", "content": message}
            ],
            max_tokens=500
        )
        return response.choices[0].message.content
