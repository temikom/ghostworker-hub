const API_BASE_URL = '/api';

async function request<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const token = localStorage.getItem('token');
  
  const headers: HeadersInit = {
    'Content-Type': 'application/json',
    ...(token && { Authorization: `Bearer ${token}` }),
    ...options?.headers,
  };

  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ message: 'Request failed' }));
    throw new Error(error.message || 'Request failed');
  }

  return response.json();
}

// Auth API
export const authApi = {
  register: (data: { email: string; password: string; name: string }) =>
    request<{ token: string; user: User }>('/auth/register', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
  
  login: (data: { email: string; password: string }) =>
    request<{ token: string; user: User }>('/auth/login', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
  
  me: () => request<User>('/auth/me'),
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
  email: string;
  name: string;
}

export interface Conversation {
  id: string;
  customer_name: string;
  platform: 'whatsapp' | 'instagram' | 'tiktok' | 'email';
  last_message: string;
  last_message_time: string;
  unread_count: number;
}

export interface Message {
  id: string;
  conversation_id: string;
  content: string;
  sender: 'customer' | 'business';
  platform: 'whatsapp' | 'instagram' | 'tiktok' | 'email';
  timestamp: string;
}

export interface Integration {
  id: string;
  platform: 'whatsapp' | 'instagram' | 'tiktok' | 'email';
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
