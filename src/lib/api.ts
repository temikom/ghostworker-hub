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

// Auth API Response Types
interface LoginResponse {
  token?: string;
  user?: User;
  requires_2fa?: boolean;
  temp_token?: string;
  requires_verification?: boolean;
}

interface RegisterResponse {
  token?: string;
  user?: User;
  requires_verification?: boolean;
}

// Auth API
export const authApi = {
  register: (data: { email: string; password: string; name: string }) =>
    request<RegisterResponse>('/auth/register', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
  
  login: (data: { email: string; password: string }) =>
    request<LoginResponse>('/auth/login', {
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
  list: () => request<Conversation[]>('/conversations'),
  get: (id: string) => request<Conversation>(`/conversations/${id}`),
  getMessages: (conversationId: string) => request<Message[]>(`/messages/${conversationId}`),
  sendMessage: (data: { conversation_id: string; content: string; platform: string }) =>
    request<Message>('/messages/send', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
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
};

// Orders API
export const ordersApi = {
  list: () => request<Order[]>('/orders'),
  get: (id: string) => request<Order>(`/orders/${id}`),
  updateStatus: (data: { order_id: string; status: string }) =>
    request<Order>('/orders/update-status', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
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

// Types
export interface User {
  id: string;
  email?: string;
  name: string;
  avatar_url?: string;
  is_verified?: boolean;
  two_factor_enabled?: boolean;
}

export interface Conversation {
  id: string;
  customer_name: string;
  platform: 'whatsapp' | 'instagram' | 'tiktok' | 'email' | 'facebook';
  last_message: string;
  last_message_time: string;
  unread_count: number;
}

export interface Message {
  id: string;
  conversation_id: string;
  content: string;
  sender: 'customer' | 'business';
  platform: 'whatsapp' | 'instagram' | 'tiktok' | 'email' | 'facebook';
  timestamp: string;
}

export interface Integration {
  id: string;
  platform: 'whatsapp' | 'instagram' | 'tiktok' | 'email' | 'facebook';
  status: 'connected' | 'disconnected';
  connected_at?: string;
}


export interface Order {
  id: string;
  customer_name: string;
  items: OrderItem[];
  status: 'pending' | 'processing' | 'shipped' | 'delivered' | 'cancelled';
  total: number;
  created_at: string;
}

export interface OrderItem {
  name: string;
  quantity: number;
  price: number;
}

export interface Task {
  id: string;
  title: string;
  description?: string;
  status: 'pending' | 'in_progress' | 'completed';
  created_at: string;
}
