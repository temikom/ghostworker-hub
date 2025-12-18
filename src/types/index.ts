// ============= Core Types =============

// Platform Types
export type Platform = 'whatsapp' | 'instagram' | 'tiktok' | 'email' | 'facebook';
export type MessageDirection = 'inbound' | 'outbound';
export type MessageStatus = 'pending' | 'sent' | 'delivered' | 'read' | 'failed';
export type OrderStatus = 'pending' | 'processing' | 'shipped' | 'delivered' | 'cancelled';
export type IntegrationStatus = 'connected' | 'disconnected' | 'error';

// User & Auth Types
export interface User {
  id: string;
  email?: string;
  name: string;
  avatar_url?: string;
  is_verified?: boolean;
  two_factor_enabled?: boolean;
  role?: UserRole;
  team_id?: string;
}

export type UserRole = 'owner' | 'admin' | 'member' | 'viewer';

export interface Team {
  id: string;
  name: string;
  logo_url?: string;
  owner_id: string;
  settings: TeamSettings;
  created_at: string;
}

export interface TeamSettings {
  branding?: WhiteLabelSettings;
  features?: Record<string, boolean>;
}

export interface WhiteLabelSettings {
  logo_url?: string;
  primary_color?: string;
  secondary_color?: string;
  company_name?: string;
  custom_domain?: string;
  favicon_url?: string;
}

export interface TeamMember {
  id: string;
  user_id: string;
  team_id: string;
  role: UserRole;
  user: User;
  invited_at: string;
  joined_at?: string;
}

// Conversation Types
export interface Conversation {
  id: string;
  customer_id: string;
  customer_name: string;
  platform: Platform;
  last_message: string;
  last_message_time: string;
  unread_count: number;
  status: 'open' | 'closed' | 'pending';
  assigned_to?: string;
  sentiment?: SentimentScore;
  language?: string;
  tags?: string[];
}

export interface Message {
  id: string;
  conversation_id: string;
  content: string;
  sender: 'customer' | 'business';
  platform: Platform;
  timestamp: string;
  status?: MessageStatus;
  metadata?: MessageMetadata;
}

export interface MessageMetadata {
  sentiment?: SentimentScore;
  language?: string;
  translated_content?: string;
  voice_transcription?: string;
  ai_suggestions?: string[];
}

// AI Types
export interface SentimentScore {
  label: 'positive' | 'neutral' | 'negative';
  score: number;
  confidence: number;
}

export interface VoiceTranscription {
  id: string;
  message_id: string;
  audio_url: string;
  text: string;
  language: string;
  duration: number;
  created_at: string;
}

export interface Translation {
  original_text: string;
  translated_text: string;
  source_language: string;
  target_language: string;
}

export interface SmartRoutingRule {
  id: string;
  name: string;
  conditions: RoutingCondition[];
  action: RoutingAction;
  priority: number;
  is_active: boolean;
}

export interface RoutingCondition {
  field: 'sentiment' | 'platform' | 'language' | 'keyword' | 'customer_tag';
  operator: 'equals' | 'contains' | 'greater_than' | 'less_than';
  value: string;
}

export interface RoutingAction {
  type: 'assign_to_user' | 'assign_to_team' | 'add_tag' | 'send_auto_reply' | 'escalate';
  target_id?: string;
  template_id?: string;
}

// Automation Types
export interface Workflow {
  id: string;
  name: string;
  description?: string;
  trigger: WorkflowTrigger;
  nodes: WorkflowNode[];
  connections: WorkflowConnection[];
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface WorkflowTrigger {
  type: 'message_received' | 'order_created' | 'tag_added' | 'schedule' | 'webhook';
  config: Record<string, unknown>;
}

export interface WorkflowNode {
  id: string;
  type: 'condition' | 'action' | 'delay' | 'ai_response' | 'send_message' | 'update_tag' | 'create_order';
  position: { x: number; y: number };
  data: Record<string, unknown>;
}

export interface WorkflowConnection {
  id: string;
  source_id: string;
  target_id: string;
  source_handle?: string;
  target_handle?: string;
}

export interface ChatbotFlow {
  id: string;
  name: string;
  description?: string;
  nodes: ChatbotNode[];
  connections: WorkflowConnection[];
  is_active: boolean;
  platforms: Platform[];
  created_at: string;
}

export interface ChatbotNode {
  id: string;
  type: 'start' | 'message' | 'question' | 'menu' | 'condition' | 'action' | 'end';
  position: { x: number; y: number };
  data: ChatbotNodeData;
}

export interface ChatbotNodeData {
  text?: string;
  options?: { label: string; value: string }[];
  variable?: string;
  condition?: { field: string; operator: string; value: string };
  action?: { type: string; config: Record<string, unknown> };
}

export interface ScheduledMessage {
  id: string;
  name: string;
  content: string;
  recipients: MessageRecipient[];
  schedule: MessageSchedule;
  platforms: Platform[];
  status: 'draft' | 'scheduled' | 'sent' | 'cancelled';
  sent_count?: number;
  created_at: string;
}

export interface MessageRecipient {
  type: 'all' | 'tag' | 'segment' | 'individual';
  value?: string;
  customer_ids?: string[];
}

export interface MessageSchedule {
  type: 'once' | 'recurring';
  send_at?: string;
  timezone?: string;
  recurrence?: {
    frequency: 'daily' | 'weekly' | 'monthly';
    days?: number[];
    time: string;
  };
}

export interface AutoResponder {
  id: string;
  name: string;
  trigger: AutoResponderTrigger;
  response: AutoResponderResponse;
  platforms: Platform[];
  is_active: boolean;
  created_at: string;
}

export interface AutoResponderTrigger {
  type: 'keyword' | 'first_message' | 'no_agent' | 'outside_hours';
  keywords?: string[];
  delay_seconds?: number;
}

export interface AutoResponderResponse {
  type: 'text' | 'template' | 'ai_generated';
  content?: string;
  template_id?: string;
  ai_prompt?: string;
}

// Commerce Types
export interface Product {
  id: string;
  name: string;
  description?: string;
  price: number;
  currency: string;
  images: string[];
  category?: string;
  sku?: string;
  stock_quantity?: number;
  is_active: boolean;
  metadata?: Record<string, unknown>;
  created_at: string;
}

export interface Order {
  id: string;
  customer_id: string;
  customer_name: string;
  items: OrderItem[];
  status: OrderStatus;
  total: number;
  currency: string;
  shipping_address?: Address;
  payment_status?: 'pending' | 'paid' | 'failed' | 'refunded';
  payment_method?: string;
  notes?: string;
  created_at: string;
  updated_at: string;
}

export interface OrderItem {
  id: string;
  product_id: string;
  name: string;
  quantity: number;
  price: number;
  total: number;
}

export interface Address {
  line1: string;
  line2?: string;
  city: string;
  state?: string;
  postal_code: string;
  country: string;
}

export interface Invoice {
  id: string;
  order_id?: string;
  customer_id: string;
  customer_name: string;
  items: InvoiceItem[];
  subtotal: number;
  tax: number;
  total: number;
  currency: string;
  status: 'draft' | 'sent' | 'paid' | 'overdue' | 'cancelled';
  due_date?: string;
  paid_at?: string;
  pdf_url?: string;
  created_at: string;
}

export interface InvoiceItem {
  description: string;
  quantity: number;
  unit_price: number;
  total: number;
}

export interface PaymentConfig {
  provider: 'stripe' | 'paypal' | 'manual';
  is_configured: boolean;
  public_key?: string;
  webhook_url?: string;
}

export interface OrderNotification {
  id: string;
  order_id: string;
  type: 'order_created' | 'order_updated' | 'payment_received' | 'shipped' | 'delivered';
  channel: 'email' | 'sms' | 'whatsapp' | 'in_app';
  status: 'pending' | 'sent' | 'failed';
  sent_at?: string;
}

// Customer Types
export interface Customer {
  id: string;
  name: string;
  email?: string;
  phone?: string;
  platform: Platform;
  platform_id: string;
  avatar_url?: string;
  tags: string[];
  notes?: string;
  total_orders: number;
  total_spent: number;
  last_contact?: string;
  created_at: string;
}

// Analytics Types
export interface AnalyticsData {
  period: string;
  messages_sent: number;
  messages_received: number;
  response_time_avg: number;
  conversations_opened: number;
  conversations_closed: number;
  orders_created: number;
  revenue: number;
  sentiment_distribution: Record<string, number>;
  platform_distribution: Record<string, number>;
}

export interface DashboardStats {
  messages_today: number;
  messages_change: number;
  orders_total: number;
  orders_change: number;
  active_automations: number;
  connected_platforms: number;
  response_time_avg: string;
  satisfaction_score: number;
}

// Integration Types
export interface Integration {
  id: string;
  platform: Platform;
  status: IntegrationStatus;
  connected_at?: string;
  config?: Record<string, unknown>;
}

// Template Types
export interface Template {
  id: string;
  name: string;
  content: string;
  category?: string;
  variables?: string[];
  platforms?: Platform[];
  is_active: boolean;
  usage_count: number;
  created_at: string;
}

// Tag Types
export interface Tag {
  id: string;
  name: string;
  color: string;
  description?: string;
  usage_count: number;
}
