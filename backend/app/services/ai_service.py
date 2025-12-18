"""Enhanced AI Service with Voice, Sentiment, Translation, and Routing"""
from typing import List, Optional, Dict, Any
import openai
import httpx
from app.core.config import settings


class AIService:
    def __init__(self):
        self.client = openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.OPENAI_MODEL
    
    async def generate_reply(self, messages: List, context: Optional[str] = None) -> dict:
        """Generate AI reply for conversation"""
        conversation = "\n".join([f"{m.direction}: {m.content}" for m in messages])
        
        system_prompt = """You are a helpful customer service assistant. Generate a professional, friendly reply.
        Consider the conversation context and customer sentiment when responding."""
        
        if context:
            system_prompt += f"\n\nAdditional context: {context}"
        
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
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
        """Suggest actions based on conversation"""
        conversation = "\n".join([f"{m.direction}: {m.content}" for m in messages[-5:]])
        
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "Analyze this conversation and suggest 3-5 actionable next steps. Return as JSON array with 'action' and 'description' fields."},
                {"role": "user", "content": conversation}
            ],
            max_tokens=300,
            response_format={"type": "json_object"}
        )
        
        try:
            import json
            result = json.loads(response.choices[0].message.content)
            return result.get("actions", [])
        except:
            return [
                {"action": "reply", "description": "Send a response", "priority": "high"},
                {"action": "tag", "description": "Add relevant tags", "priority": "medium"}
            ]
    
    async def summarize_conversation(self, messages: List) -> dict:
        """Summarize conversation with key points"""
        conversation = "\n".join([f"{m.direction}: {m.content}" for m in messages])
        
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "Summarize this conversation. Include: summary, key_points (list), sentiment (positive/neutral/negative), and action_items (list)."},
                {"role": "user", "content": conversation}
            ],
            max_tokens=400,
            response_format={"type": "json_object"}
        )
        
        try:
            import json
            return json.loads(response.choices[0].message.content)
        except:
            return {
                "summary": response.choices[0].message.content,
                "key_points": [],
                "sentiment": "neutral",
                "action_items": []
            }
    
    async def transcribe_voice(self, audio_file) -> dict:
        """Transcribe voice message using Whisper"""
        response = await self.client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
            response_format="verbose_json"
        )
        
        return {
            "text": response.text,
            "language": response.language,
            "duration": response.duration,
            "confidence": 0.95
        }
    
    async def analyze_sentiment(self, text: str) -> dict:
        """Analyze text sentiment"""
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": """Analyze the sentiment of this text. Return JSON with:
                - label: "positive", "neutral", or "negative"
                - score: confidence score 0-1
                - confidence: overall confidence 0-1
                - keywords: list of sentiment-indicating words"""},
                {"role": "user", "content": text}
            ],
            max_tokens=150,
            response_format={"type": "json_object"}
        )
        
        try:
            import json
            return json.loads(response.choices[0].message.content)
        except:
            return {"label": "neutral", "score": 0.5, "confidence": 0.5, "keywords": []}
    
    async def translate_text(self, text: str, target_language: str, source_language: Optional[str] = None) -> dict:
        """Translate text to target language"""
        source_hint = f" from {source_language}" if source_language else ""
        
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": f"Translate the following text{source_hint} to {target_language}. Return JSON with: translated_text, source_language (detected if not provided), target_language"},
                {"role": "user", "content": text}
            ],
            max_tokens=500,
            response_format={"type": "json_object"}
        )
        
        try:
            import json
            result = json.loads(response.choices[0].message.content)
            return {
                "original_text": text,
                "translated_text": result.get("translated_text", ""),
                "source_language": result.get("source_language", source_language or "auto"),
                "target_language": target_language
            }
        except:
            return {
                "original_text": text,
                "translated_text": text,
                "source_language": "unknown",
                "target_language": target_language
            }
    
    async def detect_language(self, text: str) -> str:
        """Detect the language of text"""
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "Detect the language of this text. Return only the ISO 639-1 language code (e.g., 'en', 'es', 'fr')."},
                {"role": "user", "content": text}
            ],
            max_tokens=10
        )
        return response.choices[0].message.content.strip().lower()[:2]
    
    async def extract_order_intent(self, content: str) -> dict:
        """Extract order intent from message"""
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": """Analyze if this message contains purchase intent. Return JSON with:
                - has_order_intent: boolean
                - items: list of {name, quantity, estimated_price}
                - total_estimate: number or null
                - confidence: 0-100"""},
                {"role": "user", "content": content}
            ],
            max_tokens=300,
            response_format={"type": "json_object"}
        )
        
        try:
            import json
            return json.loads(response.choices[0].message.content)
        except:
            return {"has_order_intent": False, "items": [], "total_estimate": None, "confidence": 50}
    
    async def categorize_message(self, content: str) -> dict:
        """Categorize message type"""
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": """Categorize this customer message. Return JSON with:
                - category: one of [inquiry, complaint, order, support, feedback, greeting, other]
                - subcategory: more specific category
                - confidence: 0-100
                - tags: list of relevant tags
                - priority: low/medium/high/urgent"""},
                {"role": "user", "content": content}
            ],
            max_tokens=200,
            response_format={"type": "json_object"}
        )
        
        try:
            import json
            return json.loads(response.choices[0].message.content)
        except:
            return {"category": "general", "subcategory": None, "confidence": 70, "tags": [], "priority": "medium"}
    
    async def generate_auto_response(self, trigger_type: str, context: dict) -> str:
        """Generate auto-response based on trigger"""
        prompts = {
            "first_message": "Generate a friendly welcome message for a new customer.",
            "no_agent": "Generate a message explaining that all agents are busy and we'll respond soon.",
            "outside_hours": "Generate a message explaining we're currently closed and will respond during business hours.",
            "keyword": f"Generate a helpful response about: {context.get('keyword', 'general inquiry')}"
        }
        
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a friendly customer service bot. Keep responses concise and helpful."},
                {"role": "user", "content": prompts.get(trigger_type, "Generate a helpful response.")}
            ],
            max_tokens=200
        )
        return response.choices[0].message.content
    
    async def chat(self, message: str, conversation_history: Optional[List[dict]] = None) -> str:
        """General chat with AI assistant"""
        messages = [
            {"role": "system", "content": "You are GhostWorker AI assistant. Help with business tasks, answer questions, and provide insights."}
        ]
        
        if conversation_history:
            messages.extend(conversation_history)
        
        messages.append({"role": "user", "content": message})
        
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            max_tokens=500
        )
        return response.choices[0].message.content


# Singleton instance
ai_service = AIService()
