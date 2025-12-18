// Configure this to your FastAPI backend URL
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const API_V1 = `${API_BASE_URL}/api/v1`;

async function request<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const token = sessionStorage.getItem('gw_session');
  
  const headers: HeadersInit = {
    'Content-Type': 'application/json',
    ...(token && { Authorization: `Bearer ${token}` }),
    ...options?.headers,
  };

  const response = await fetch(`${API_V1}${endpoint}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Request failed' }));
    throw new Error(error.detail || error.message || 'Request failed');
  }

  return response.json();
}

// Re-export types from types/index.ts
export type {
  User,
  Team,
  TeamMember,
  UserRole,
  Conversation,
  Message,
  Integration,
  Order,
  OrderItem,
  Product,
  Invoice,
  Customer,
  Workflow,
  ChatbotFlow,
  ScheduledMessage,
  AutoResponder,
  SmartRoutingRule,
  Template,
  Tag,
  AnalyticsData,
  DashboardStats,
  SentimentScore,
  VoiceTranscription,
  Translation,
  WhiteLabelSettings,
} from '@/types';

// Auth API
export const authApi = {
  register: (data: { email: string; password: string; name: string }) =>
    request<{ token?: string; user?: User; requires_verification?: boolean }>('/auth/register', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
  
  login: (data: { email: string; password: string }) =>
    request<{ token?: string; user?: User; requires_2fa?: boolean; temp_token?: string; requires_verification?: boolean }>('/auth/login', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
  
  me: () => request<User>('/auth/me'),

  checkEmail: (data: { email: string }) =>
    request<{ exists: boolean }>('/auth/check-email', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  verify2FA: (data: { temp_token: string; code: string }) =>
    request<{ token: string; user: User }>('/auth/2fa/login', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  verifyEmail: (data: { token: string }) =>
    request<{ token: string; user: User }>('/auth/verify-email', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  resendVerification: (data: { email: string }) =>
    request<{ message: string }>('/auth/resend-verification', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
};

// Conversations API
export const conversationsApi = {
  list: (filters?: { platform?: string; status?: string; assigned_to?: string }) =>
    request<Conversation[]>(`/conversations${filters ? `?${new URLSearchParams(filters as Record<string, string>)}` : ''}`),
  get: (id: string) => request<Conversation>(`/conversations/${id}`),
  getMessages: (conversationId: string) => request<Message[]>(`/messages/${conversationId}`),
  sendMessage: (data: { conversation_id: string; content: string; platform: string }) =>
    request<Message>('/messages/send', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
  assign: (conversationId: string, userId: string) =>
    request<Conversation>(`/conversations/${conversationId}/assign`, {
      method: 'POST',
      body: JSON.stringify({ user_id: userId }),
    }),
  close: (conversationId: string) =>
    request<Conversation>(`/conversations/${conversationId}/close`, { method: 'POST' }),
};

// Integrations API
export const integrationsApi = {
  list: () => request<Integration[]>('/integrations'),
  connect: (data: { platform: string; credentials: Record<string, string> }) =>
    request<Integration>('/integrations/connect', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
  disconnect: (platform: string) =>
    request<{ success: boolean }>('/integrations/disconnect', {
      method: 'POST',
      body: JSON.stringify({ platform }),
    }),
  test: (platform: string) =>
    request<{ success: boolean; message: string }>(`/integrations/${platform}/test`, { method: 'POST' }),
};

// Orders API
export const ordersApi = {
  list: (filters?: { status?: string; customer_id?: string }) =>
    request<Order[]>(`/orders${filters ? `?${new URLSearchParams(filters as Record<string, string>)}` : ''}`),
  get: (id: string) => request<Order>(`/orders/${id}`),
  create: (data: Partial<Order>) =>
    request<Order>('/orders', { method: 'POST', body: JSON.stringify(data) }),
  update: (id: string, data: Partial<Order>) =>
    request<Order>(`/orders/${id}`, { method: 'PUT', body: JSON.stringify(data) }),
  updateStatus: (data: { order_id: string; status: string }) =>
    request<Order>('/orders/update-status', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
};

// Products API
export const productsApi = {
  list: (filters?: { category?: string; is_active?: boolean }) =>
    request<Product[]>(`/products${filters ? `?${new URLSearchParams(filters as Record<string, string>)}` : ''}`),
  get: (id: string) => request<Product>(`/products/${id}`),
  create: (data: Partial<Product>) =>
    request<Product>('/products', { method: 'POST', body: JSON.stringify(data) }),
  update: (id: string, data: Partial<Product>) =>
    request<Product>(`/products/${id}`, { method: 'PUT', body: JSON.stringify(data) }),
  delete: (id: string) =>
    request<{ success: boolean }>(`/products/${id}`, { method: 'DELETE' }),
};

// Invoices API
export const invoicesApi = {
  list: (filters?: { status?: string; customer_id?: string }) =>
    request<Invoice[]>(`/invoices${filters ? `?${new URLSearchParams(filters as Record<string, string>)}` : ''}`),
  get: (id: string) => request<Invoice>(`/invoices/${id}`),
  create: (data: Partial<Invoice>) =>
    request<Invoice>('/invoices', { method: 'POST', body: JSON.stringify(data) }),
  update: (id: string, data: Partial<Invoice>) =>
    request<Invoice>(`/invoices/${id}`, { method: 'PUT', body: JSON.stringify(data) }),
  send: (id: string) =>
    request<Invoice>(`/invoices/${id}/send`, { method: 'POST' }),
  markPaid: (id: string) =>
    request<Invoice>(`/invoices/${id}/mark-paid`, { method: 'POST' }),
  downloadPdf: (id: string) => `${API_V1}/invoices/${id}/pdf`,
};

// Customers API
export const customersApi = {
  list: (filters?: { tag?: string; platform?: string }) =>
    request<Customer[]>(`/customers${filters ? `?${new URLSearchParams(filters as Record<string, string>)}` : ''}`),
  get: (id: string) => request<Customer>(`/customers/${id}`),
  update: (id: string, data: Partial<Customer>) =>
    request<Customer>(`/customers/${id}`, { method: 'PUT', body: JSON.stringify(data) }),
  addTag: (id: string, tag: string) =>
    request<Customer>(`/customers/${id}/tags`, { method: 'POST', body: JSON.stringify({ tag }) }),
  removeTag: (id: string, tag: string) =>
    request<Customer>(`/customers/${id}/tags/${tag}`, { method: 'DELETE' }),
};

// AI API
export const aiApi = {
  transcribeVoice: (audioFile: File) => {
    const formData = new FormData();
    formData.append('audio', audioFile);
    return fetch(`${API_V1}/ai/transcribe`, {
      method: 'POST',
      headers: { Authorization: `Bearer ${sessionStorage.getItem('gw_session')}` },
      body: formData,
    }).then(r => r.json()) as Promise<{ text: string; language: string; duration: number }>;
  },
  analyzeSentiment: (text: string) =>
    request<SentimentScore>('/ai/sentiment', { method: 'POST', body: JSON.stringify({ text }) }),
  translate: (text: string, targetLanguage: string, sourceLanguage?: string) =>
    request<Translation>('/ai/translate', {
      method: 'POST',
      body: JSON.stringify({ text, target_language: targetLanguage, source_language: sourceLanguage }),
    }),
  generateReply: (conversationId: string, context?: string) =>
    request<{ reply: string }>('/ai/generate-reply', {
      method: 'POST',
      body: JSON.stringify({ conversation_id: conversationId, context }),
    }),
  suggestActions: (conversationId: string) =>
    request<{ actions: string[] }>('/ai/suggest-actions', {
      method: 'POST',
      body: JSON.stringify({ conversation_id: conversationId }),
    }),
};

// Smart Routing API
export const routingApi = {
  list: () => request<SmartRoutingRule[]>('/routing/rules'),
  create: (data: Partial<SmartRoutingRule>) =>
    request<SmartRoutingRule>('/routing/rules', { method: 'POST', body: JSON.stringify(data) }),
  update: (id: string, data: Partial<SmartRoutingRule>) =>
    request<SmartRoutingRule>(`/routing/rules/${id}`, { method: 'PUT', body: JSON.stringify(data) }),
  delete: (id: string) =>
    request<{ success: boolean }>(`/routing/rules/${id}`, { method: 'DELETE' }),
  reorder: (ruleIds: string[]) =>
    request<{ success: boolean }>('/routing/rules/reorder', { method: 'POST', body: JSON.stringify({ rule_ids: ruleIds }) }),
};

// Workflows API
export const workflowsApi = {
  list: () => request<Workflow[]>('/workflows'),
  get: (id: string) => request<Workflow>(`/workflows/${id}`),
  create: (data: Partial<Workflow>) =>
    request<Workflow>('/workflows', { method: 'POST', body: JSON.stringify(data) }),
  update: (id: string, data: Partial<Workflow>) =>
    request<Workflow>(`/workflows/${id}`, { method: 'PUT', body: JSON.stringify(data) }),
  delete: (id: string) =>
    request<{ success: boolean }>(`/workflows/${id}`, { method: 'DELETE' }),
  activate: (id: string) =>
    request<Workflow>(`/workflows/${id}/activate`, { method: 'POST' }),
  deactivate: (id: string) =>
    request<Workflow>(`/workflows/${id}/deactivate`, { method: 'POST' }),
};

// Chatbot Flows API
export const chatbotApi = {
  list: () => request<ChatbotFlow[]>('/chatbots'),
  get: (id: string) => request<ChatbotFlow>(`/chatbots/${id}`),
  create: (data: Partial<ChatbotFlow>) =>
    request<ChatbotFlow>('/chatbots', { method: 'POST', body: JSON.stringify(data) }),
  update: (id: string, data: Partial<ChatbotFlow>) =>
    request<ChatbotFlow>(`/chatbots/${id}`, { method: 'PUT', body: JSON.stringify(data) }),
  delete: (id: string) =>
    request<{ success: boolean }>(`/chatbots/${id}`, { method: 'DELETE' }),
  activate: (id: string) =>
    request<ChatbotFlow>(`/chatbots/${id}/activate`, { method: 'POST' }),
};

// Scheduled Messages API
export const scheduledMessagesApi = {
  list: () => request<ScheduledMessage[]>('/scheduled-messages'),
  get: (id: string) => request<ScheduledMessage>(`/scheduled-messages/${id}`),
  create: (data: Partial<ScheduledMessage>) =>
    request<ScheduledMessage>('/scheduled-messages', { method: 'POST', body: JSON.stringify(data) }),
  update: (id: string, data: Partial<ScheduledMessage>) =>
    request<ScheduledMessage>(`/scheduled-messages/${id}`, { method: 'PUT', body: JSON.stringify(data) }),
  delete: (id: string) =>
    request<{ success: boolean }>(`/scheduled-messages/${id}`, { method: 'DELETE' }),
  cancel: (id: string) =>
    request<ScheduledMessage>(`/scheduled-messages/${id}/cancel`, { method: 'POST' }),
};

// Auto Responders API
export const autoRespondersApi = {
  list: () => request<AutoResponder[]>('/auto-responders'),
  get: (id: string) => request<AutoResponder>(`/auto-responders/${id}`),
  create: (data: Partial<AutoResponder>) =>
    request<AutoResponder>('/auto-responders', { method: 'POST', body: JSON.stringify(data) }),
  update: (id: string, data: Partial<AutoResponder>) =>
    request<AutoResponder>(`/auto-responders/${id}`, { method: 'PUT', body: JSON.stringify(data) }),
  delete: (id: string) =>
    request<{ success: boolean }>(`/auto-responders/${id}`, { method: 'DELETE' }),
  toggle: (id: string, isActive: boolean) =>
    request<AutoResponder>(`/auto-responders/${id}/toggle`, { method: 'POST', body: JSON.stringify({ is_active: isActive }) }),
};

// Templates API
export const templatesApi = {
  list: () => request<Template[]>('/templates'),
  get: (id: string) => request<Template>(`/templates/${id}`),
  create: (data: Partial<Template>) =>
    request<Template>('/templates', { method: 'POST', body: JSON.stringify(data) }),
  update: (id: string, data: Partial<Template>) =>
    request<Template>(`/templates/${id}`, { method: 'PUT', body: JSON.stringify(data) }),
  delete: (id: string) =>
    request<{ success: boolean }>(`/templates/${id}`, { method: 'DELETE' }),
};

// Tags API
export const tagsApi = {
  list: () => request<Tag[]>('/tags'),
  create: (data: Partial<Tag>) =>
    request<Tag>('/tags', { method: 'POST', body: JSON.stringify(data) }),
  update: (id: string, data: Partial<Tag>) =>
    request<Tag>(`/tags/${id}`, { method: 'PUT', body: JSON.stringify(data) }),
  delete: (id: string) =>
    request<{ success: boolean }>(`/tags/${id}`, { method: 'DELETE' }),
};

// Team API
export const teamApi = {
  get: () => request<Team>('/team'),
  update: (data: Partial<Team>) =>
    request<Team>('/team', { method: 'PUT', body: JSON.stringify(data) }),
  getMembers: () => request<TeamMember[]>('/team/members'),
  inviteMember: (email: string, role: string) =>
    request<{ success: boolean }>('/team/invite', { method: 'POST', body: JSON.stringify({ email, role }) }),
  updateMemberRole: (memberId: string, role: string) =>
    request<TeamMember>(`/team/members/${memberId}/role`, { method: 'PUT', body: JSON.stringify({ role }) }),
  removeMember: (memberId: string) =>
    request<{ success: boolean }>(`/team/members/${memberId}`, { method: 'DELETE' }),
  updateBranding: (branding: WhiteLabelSettings) =>
    request<Team>('/team/branding', { method: 'PUT', body: JSON.stringify(branding) }),
};

// Analytics API
export const analyticsApi = {
  getDashboardStats: () => request<DashboardStats>('/analytics/dashboard'),
  getAnalytics: (period: 'day' | 'week' | 'month' | 'year', startDate?: string, endDate?: string) =>
    request<AnalyticsData[]>(`/analytics?period=${period}${startDate ? `&start_date=${startDate}` : ''}${endDate ? `&end_date=${endDate}` : ''}`),
  getConversationStats: () =>
    request<{ total: number; by_platform: Record<string, number>; by_status: Record<string, number> }>('/analytics/conversations'),
  getRevenueStats: (period: 'day' | 'week' | 'month' | 'year') =>
    request<{ total: number; change: number; by_period: { date: string; amount: number }[] }>(`/analytics/revenue?period=${period}`),
  exportReport: (type: 'conversations' | 'orders' | 'customers', format: 'csv' | 'xlsx') =>
    `${API_V1}/analytics/export?type=${type}&format=${format}`,
};

// Payments API
export const paymentsApi = {
  getConfig: () => request<PaymentConfig>('/payments/config'),
  updateConfig: (data: Partial<PaymentConfig>) =>
    request<PaymentConfig>('/payments/config', { method: 'PUT', body: JSON.stringify(data) }),
  createCheckoutSession: (orderId: string) =>
    request<{ checkout_url: string }>('/payments/checkout', { method: 'POST', body: JSON.stringify({ order_id: orderId }) }),
  refund: (paymentId: string, amount?: number) =>
    request<{ success: boolean }>('/payments/refund', { method: 'POST', body: JSON.stringify({ payment_id: paymentId, amount }) }),
};

// Notifications API
export const notificationsApi = {
  list: () => request<OrderNotification[]>('/notifications'),
  getSettings: () =>
    request<{ email: boolean; push: boolean; triggers: Record<string, boolean> }>('/notifications/settings'),
  updateSettings: (settings: Record<string, boolean>) =>
    request<{ success: boolean }>('/notifications/settings', { method: 'PUT', body: JSON.stringify(settings) }),
};

// Assistant API
export const assistantApi = {
  getTasks: () => request<Task[]>('/assistant/tasks'),
  createTask: (data: { title: string; description?: string }) =>
    request<Task>('/assistant/tasks', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
  chat: (message: string) =>
    request<{ response: string }>('/assistant/chat', {
      method: 'POST',
      body: JSON.stringify({ message }),
    }),
};

// Types that need to be defined locally for backward compatibility
import type {
  User,
  Team,
  TeamMember,
  Conversation,
  Message,
  Integration,
  Order,
  OrderItem,
  Product,
  Invoice,
  Customer,
  Workflow,
  ChatbotFlow,
  ScheduledMessage,
  AutoResponder,
  SmartRoutingRule,
  Template,
  Tag,
  AnalyticsData,
  DashboardStats,
  SentimentScore,
  Translation,
  WhiteLabelSettings,
  PaymentConfig,
  OrderNotification,
} from '@/types';

export interface Task {
  id: string;
  title: string;
  description?: string;
  status: 'pending' | 'in_progress' | 'completed';
  created_at: string;
}
