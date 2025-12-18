# Export all models for easy importing
from app.models.user import User, UserRoleAssignment, UserRole, Team
from app.models.conversation import Conversation, Message, ConversationTag, Platform, MessageStatus, MessageDirection
from app.models.customer import Customer, CustomerTag
from app.models.order import Order, OrderTimeline, OrderStatus
from app.models.tag import Tag, Template
from app.models.integration import Integration, WebhookEvent, IntegrationStatus
from app.models.analytics import AnalyticsSnapshot, Activity
from app.models.assistant import AssistantTask, AIConversation, Settings, TaskStatus

__all__ = [
    # User
    "User",
    "UserRoleAssignment",
    "UserRole",
    "Team",
    
    # Conversation
    "Conversation",
    "Message",
    "ConversationTag",
    "Platform",
    "MessageStatus",
    "MessageDirection",
    
    # Customer
    "Customer",
    "CustomerTag",
    
    # Order
    "Order",
    "OrderTimeline",
    "OrderStatus",
    
    # Tag & Template
    "Tag",
    "Template",
    
    # Integration
    "Integration",
    "WebhookEvent",
    "IntegrationStatus",
    
    # Analytics
    "AnalyticsSnapshot",
    "Activity",
    
    # Assistant
    "AssistantTask",
    "AIConversation",
    "Settings",
    "TaskStatus",
]
