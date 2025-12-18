import { useEffect, useCallback } from 'react';
import { websocket, WS_EVENTS } from '@/services/websocket';
import { toast } from 'sonner';

interface UseRealtimeOptions {
  onNewMessage?: (data: any) => void;
  onNewOrder?: (data: any) => void;
  onNotification?: (data: any) => void;
  onConversationUpdated?: (data: any) => void;
  showNotifications?: boolean;
}

export function useRealtime(options: UseRealtimeOptions = {}) {
  const {
    onNewMessage,
    onNewOrder,
    onNotification,
    onConversationUpdated,
    showNotifications = true,
  } = options;

  useEffect(() => {
    // Connect on mount
    websocket.connect();

    const unsubscribes: (() => void)[] = [];

    // Subscribe to events
    if (onNewMessage) {
      unsubscribes.push(
        websocket.subscribe(WS_EVENTS.NEW_MESSAGE, (data) => {
          onNewMessage(data);
          if (showNotifications) {
            toast.info('New message received', {
              description: `From ${data.customer_name || 'Customer'}`,
            });
          }
        })
      );
    }

    if (onNewOrder) {
      unsubscribes.push(
        websocket.subscribe(WS_EVENTS.NEW_ORDER, (data) => {
          onNewOrder(data);
          if (showNotifications) {
            toast.success('New order received', {
              description: `Order #${data.order_number || data.id}`,
            });
          }
        })
      );
    }

    if (onNotification) {
      unsubscribes.push(
        websocket.subscribe(WS_EVENTS.NOTIFICATION, onNotification)
      );
    }

    if (onConversationUpdated) {
      unsubscribes.push(
        websocket.subscribe(WS_EVENTS.CONVERSATION_UPDATED, onConversationUpdated)
      );
    }

    // Cleanup
    return () => {
      unsubscribes.forEach(unsub => unsub());
    };
  }, [onNewMessage, onNewOrder, onNotification, onConversationUpdated, showNotifications]);

  const sendMessage = useCallback((type: string, payload: any) => {
    websocket.send(type, payload);
  }, []);

  return {
    isConnected: websocket.isConnected,
    sendMessage,
  };
}

export default useRealtime;
