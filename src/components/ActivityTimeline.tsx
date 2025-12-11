import { MessageSquare, ShoppingBag, Plug, User, Bot, Settings } from 'lucide-react';
import { PlatformIcon } from '@/components/icons/PlatformIcon';
import { cn } from '@/lib/utils';

export interface ActivityItem {
  id: string;
  type: 'message_sent' | 'message_received' | 'order_created' | 'order_updated' | 'integration_connected' | 'integration_disconnected' | 'task_created' | 'task_completed' | 'settings_updated';
  title: string;
  description: string;
  platform?: 'whatsapp' | 'instagram' | 'tiktok' | 'email';
  timestamp: string;
  metadata?: Record<string, string>;
}

interface ActivityTimelineProps {
  activities: ActivityItem[];
  maxItems?: number;
}

export function ActivityTimeline({ activities, maxItems }: ActivityTimelineProps) {
  const displayActivities = maxItems ? activities.slice(0, maxItems) : activities;

  const getIcon = (activity: ActivityItem) => {
    if (activity.platform) {
      return <PlatformIcon platform={activity.platform} className="h-4 w-4" />;
    }

    switch (activity.type) {
      case 'message_sent':
      case 'message_received':
        return <MessageSquare className="h-4 w-4" />;
      case 'order_created':
      case 'order_updated':
        return <ShoppingBag className="h-4 w-4" />;
      case 'integration_connected':
      case 'integration_disconnected':
        return <Plug className="h-4 w-4" />;
      case 'task_created':
      case 'task_completed':
        return <Bot className="h-4 w-4" />;
      case 'settings_updated':
        return <Settings className="h-4 w-4" />;
      default:
        return <User className="h-4 w-4" />;
    }
  };

  const getIconColor = (type: ActivityItem['type']) => {
    switch (type) {
      case 'message_sent':
        return 'bg-primary text-primary-foreground';
      case 'message_received':
        return 'bg-secondary text-secondary-foreground';
      case 'order_created':
        return 'bg-success text-success-foreground';
      case 'order_updated':
        return 'bg-warning text-warning-foreground';
      case 'integration_connected':
        return 'bg-success text-success-foreground';
      case 'integration_disconnected':
        return 'bg-destructive text-destructive-foreground';
      case 'task_completed':
        return 'bg-success text-success-foreground';
      default:
        return 'bg-muted text-muted-foreground';
    }
  };

  const formatTime = (timestamp: string) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 7) return `${diffDays}d ago`;
    return date.toLocaleDateString();
  };

  if (displayActivities.length === 0) {
    return (
      <div className="text-center py-8 text-muted-foreground">
        <User className="h-8 w-8 mx-auto mb-2 opacity-50" />
        <p className="text-sm">No activity yet</p>
      </div>
    );
  }

  return (
    <div className="relative">
      {/* Timeline line */}
      <div className="absolute left-4 top-0 bottom-0 w-px bg-border" />

      <div className="space-y-4">
        {displayActivities.map((activity, index) => (
          <div key={activity.id} className="relative flex gap-4 pl-1">
            {/* Icon */}
            <div
              className={cn(
                'relative z-10 flex h-8 w-8 items-center justify-center rounded-full',
                getIconColor(activity.type)
              )}
            >
              {getIcon(activity)}
            </div>

            {/* Content */}
            <div className="flex-1 min-w-0 pb-4">
              <div className="flex items-center justify-between gap-2">
                <p className="text-sm font-medium text-foreground">{activity.title}</p>
                <span className="text-xs text-muted-foreground flex-shrink-0">
                  {formatTime(activity.timestamp)}
                </span>
              </div>
              <p className="text-sm text-muted-foreground mt-0.5">{activity.description}</p>
              {activity.metadata && Object.keys(activity.metadata).length > 0 && (
                <div className="flex flex-wrap gap-2 mt-2">
                  {Object.entries(activity.metadata).map(([key, value]) => (
                    <span
                      key={key}
                      className="text-xs bg-muted text-muted-foreground px-2 py-0.5 rounded"
                    >
                      {key}: {value}
                    </span>
                  ))}
                </div>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
