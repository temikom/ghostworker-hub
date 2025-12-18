import { API_CONFIG } from '@/config/api';

type MessageHandler = (data: any) => void;
type ConnectionHandler = () => void;

interface WebSocketMessage {
  type: string;
  payload: any;
}

class WebSocketService {
  private ws: WebSocket | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 1000;
  private handlers: Map<string, Set<MessageHandler>> = new Map();
  private connectionHandlers: Set<ConnectionHandler> = new Set();
  private disconnectionHandlers: Set<ConnectionHandler> = new Set();
  private isConnecting = false;

  get isConnected(): boolean {
    return this.ws?.readyState === WebSocket.OPEN;
  }

  connect(): void {
    if (this.isConnecting || this.isConnected) return;
    
    this.isConnecting = true;
    const token = sessionStorage.getItem('gw_session');
    const wsUrl = API_CONFIG.baseUrl.replace(/^http/, 'ws');
    
    try {
      this.ws = new WebSocket(`${wsUrl}/ws?token=${token || ''}`);
      
      this.ws.onopen = () => {
        console.log('[WebSocket] Connected');
        this.isConnecting = false;
        this.reconnectAttempts = 0;
        this.connectionHandlers.forEach(handler => handler());
      };
      
      this.ws.onmessage = (event) => {
        try {
          const message: WebSocketMessage = JSON.parse(event.data);
          this.handleMessage(message);
        } catch (error) {
          console.error('[WebSocket] Failed to parse message:', error);
        }
      };
      
      this.ws.onclose = (event) => {
        console.log('[WebSocket] Disconnected:', event.code, event.reason);
        this.isConnecting = false;
        this.ws = null;
        this.disconnectionHandlers.forEach(handler => handler());
        this.attemptReconnect();
      };
      
      this.ws.onerror = (error) => {
        console.error('[WebSocket] Error:', error);
        this.isConnecting = false;
      };
    } catch (error) {
      console.error('[WebSocket] Failed to connect:', error);
      this.isConnecting = false;
      this.attemptReconnect();
    }
  }

  private attemptReconnect(): void {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.log('[WebSocket] Max reconnect attempts reached');
      return;
    }

    this.reconnectAttempts++;
    const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1);
    
    console.log(`[WebSocket] Reconnecting in ${delay}ms (attempt ${this.reconnectAttempts})`);
    
    setTimeout(() => {
      if (!this.isConnected) {
        this.connect();
      }
    }, delay);
  }

  disconnect(): void {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
    this.reconnectAttempts = this.maxReconnectAttempts; // Prevent reconnection
  }

  private handleMessage(message: WebSocketMessage): void {
    const handlers = this.handlers.get(message.type);
    if (handlers) {
      handlers.forEach(handler => handler(message.payload));
    }
    
    // Also notify "all" handlers
    const allHandlers = this.handlers.get('*');
    if (allHandlers) {
      allHandlers.forEach(handler => handler(message));
    }
  }

  subscribe(type: string, handler: MessageHandler): () => void {
    if (!this.handlers.has(type)) {
      this.handlers.set(type, new Set());
    }
    this.handlers.get(type)!.add(handler);
    
    return () => {
      this.handlers.get(type)?.delete(handler);
    };
  }

  onConnect(handler: ConnectionHandler): () => void {
    this.connectionHandlers.add(handler);
    return () => this.connectionHandlers.delete(handler);
  }

  onDisconnect(handler: ConnectionHandler): () => void {
    this.disconnectionHandlers.add(handler);
    return () => this.disconnectionHandlers.delete(handler);
  }

  send(type: string, payload: any): void {
    if (!this.isConnected) {
      console.warn('[WebSocket] Not connected, cannot send message');
      return;
    }
    
    this.ws!.send(JSON.stringify({ type, payload }));
  }
}

// Singleton instance
export const websocket = new WebSocketService();

// React hook for using WebSocket
export function useWebSocket() {
  return websocket;
}

// Event types
export const WS_EVENTS = {
  // Conversations
  NEW_MESSAGE: 'new_message',
  CONVERSATION_UPDATED: 'conversation_updated',
  CONVERSATION_ASSIGNED: 'conversation_assigned',
  
  // Orders
  NEW_ORDER: 'new_order',
  ORDER_UPDATED: 'order_updated',
  
  // Notifications
  NOTIFICATION: 'notification',
  
  // System
  PING: 'ping',
  PONG: 'pong',
} as const;

export default websocket;
