# Export all schemas
from app.schemas.user import (
    UserBase, UserCreate, UserUpdate, UserResponse, UserWithRoles,
    LoginRequest, TokenResponse, RefreshTokenRequest,
    ForgotPasswordRequest, ResetPasswordRequest,
    TeamBase, TeamCreate, TeamUpdate, TeamResponse, TeamWithMembers
)
from app.schemas.conversation import (
    ConversationBase, ConversationCreate, ConversationUpdate, ConversationResponse,
    ConversationWithCustomer, ConversationListResponse,
    MessageBase, MessageCreate, SendMessageRequest, MessageResponse, MessageListResponse,
    InboxItem, InboxResponse
)
from app.schemas.customer import (
    CustomerBase, CustomerCreate, CustomerUpdate, CustomerResponse,
    CustomerWithActivity, CustomerListResponse,
    ActivityResponse, CustomerActivityResponse
)
from app.schemas.order import (
    OrderItem, AddressSchema,
    OrderBase, OrderCreate, OrderUpdate, UpdateOrderStatus, OrderResponse,
    OrderWithCustomer, OrderListResponse, OrderTimelineItem, OrderDetailResponse
)
from app.schemas.tag import (
    TagBase, TagCreate, TagUpdate, TagResponse, TagListResponse, AttachTagRequest,
    TemplateBase, TemplateCreate, TemplateUpdate, TemplateResponse, TemplateListResponse
)
from app.schemas.integration import (
    IntegrationCredentials, IntegrationConnect, IntegrationDisconnect,
    IntegrationResponse, IntegrationListResponse,
    AnalyticsQuery, MessageAnalytics, ResponseTimeAnalytics, ChannelDistribution,
    TopCustomer, OrdersSummary, AnalyticsDashboard
)
from app.schemas.ai import (
    AIReplyRequest, AIReplyResponse,
    AISuggestRequest, AISuggestion, AISuggestResponse,
    AISummarizeRequest, AISummarizeResponse,
    AIExtractOrderRequest, AIExtractOrderResponse,
    AICategorizeRequest, AICategorizeResponse,
    AIChatRequest, AIChatResponse,
    TaskBase, TaskCreate, TaskUpdate, TaskResponse, TaskListResponse
)
from app.schemas.webhook import (
    N8NTriggerRequest, N8NTriggerResponse, N8NWorkflow, N8NWorkflowList, N8NWebhookPayload,
    WhatsAppWebhook, InstagramWebhook, TikTokWebhook, WebhookResponse
)
