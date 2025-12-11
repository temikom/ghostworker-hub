import { useState, useEffect, useRef } from 'react';
import { DashboardLayout } from '@/components/layout/DashboardLayout';
import { PlatformIcon } from '@/components/icons/PlatformIcon';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Send, Search, Zap, User } from 'lucide-react';
import { cn } from '@/lib/utils';
import { Conversation, Message, conversationsApi } from '@/lib/api';
import { toast } from 'sonner';
import { QuickReplyTemplates, QuickReplyTemplate } from '@/components/QuickReplyTemplates';
import { ConversationTags, ConversationTag } from '@/components/ConversationTags';
import { BulkActions, SelectCheckbox } from '@/components/BulkActions';
import { useKeyboardShortcuts } from '@/hooks/useKeyboardShortcuts';

export default function Inbox() {
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [selectedConversation, setSelectedConversation] = useState<Conversation | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [newMessage, setNewMessage] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [templatesOpen, setTemplatesOpen] = useState(false);
  const [selectedIds, setSelectedIds] = useState<string[]>([]);
  const [conversationTags, setConversationTags] = useState<Record<string, ConversationTag[]>>({});
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const filteredConversations = conversations.filter((c) =>
    c.customer_name.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const currentIndex = selectedConversation 
    ? filteredConversations.findIndex(c => c.id === selectedConversation.id)
    : -1;

  useKeyboardShortcuts({
    onNextItem: () => {
      if (currentIndex < filteredConversations.length - 1) {
        setSelectedConversation(filteredConversations[currentIndex + 1]);
      }
    },
    onPrevItem: () => {
      if (currentIndex > 0) {
        setSelectedConversation(filteredConversations[currentIndex - 1]);
      }
    },
    onReply: () => inputRef.current?.focus(),
  });

  useEffect(() => {
    loadConversations();
    const interval = setInterval(loadConversations, 2000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    if (selectedConversation) loadMessages(selectedConversation.id);
  }, [selectedConversation]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const loadConversations = async () => {
    try {
      const data = await conversationsApi.list();
      setConversations(data);
    } catch {}
  };

  const loadMessages = async (conversationId: string) => {
    try {
      const data = await conversationsApi.getMessages(conversationId);
      setMessages(data);
    } catch {
      toast.error('Failed to load messages');
    }
  };

  const handleSendMessage = async () => {
    if (!newMessage.trim() || !selectedConversation) return;
    setIsLoading(true);
    try {
      await conversationsApi.sendMessage({
        conversation_id: selectedConversation.id,
        content: newMessage,
        platform: selectedConversation.platform,
      });
      setNewMessage('');
      loadMessages(selectedConversation.id);
    } catch {
      toast.error('Failed to send message');
    } finally {
      setIsLoading(false);
    }
  };

  const handleTemplateSelect = (template: QuickReplyTemplate) => {
    setNewMessage(template.content);
    inputRef.current?.focus();
  };

  const toggleSelect = (id: string) => {
    setSelectedIds(prev => prev.includes(id) ? prev.filter(i => i !== id) : [...prev, id]);
  };

  const formatTime = (timestamp: string) => {
    return new Date(timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  return (
    <DashboardLayout>
      <div className="flex h-[calc(100vh-8rem)] rounded-xl border border-border bg-card overflow-hidden">
        <div className="w-full max-w-sm border-r border-border flex flex-col">
          <div className="p-4 border-b border-border">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input placeholder="Search conversations..." value={searchQuery} onChange={(e) => setSearchQuery(e.target.value)} className="pl-9" />
            </div>
          </div>

          <BulkActions
            items={filteredConversations}
            selectedIds={selectedIds}
            onSelectAll={() => setSelectedIds(filteredConversations.map(c => c.id))}
            onDeselectAll={() => setSelectedIds([])}
            onMarkAsRead={() => { setSelectedIds([]); toast.success('Marked as read'); }}
            onArchive={() => { setSelectedIds([]); toast.success('Archived'); }}
            getItemId={(c) => c.id}
          />

          <div className="flex-1 overflow-y-auto scrollbar-thin">
            {filteredConversations.length === 0 ? (
              <div className="flex flex-col items-center justify-center h-full text-muted-foreground p-4">
                <p className="text-center">No conversations yet</p>
              </div>
            ) : (
              filteredConversations.map((conversation) => (
                <button
                  key={conversation.id}
                  onClick={() => setSelectedConversation(conversation)}
                  className={cn('w-full p-4 text-left border-b border-border hover:bg-muted transition-colors', selectedConversation?.id === conversation.id && 'bg-muted')}
                >
                  <div className="flex items-center gap-3">
                    <SelectCheckbox checked={selectedIds.includes(conversation.id)} onChange={() => toggleSelect(conversation.id)} />
                    <PlatformIcon platform={conversation.platform} />
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center justify-between">
                        <span className="font-medium text-foreground truncate">{conversation.customer_name}</span>
                        <span className="text-xs text-muted-foreground">{formatTime(conversation.last_message_time)}</span>
                      </div>
                      <p className="text-sm text-muted-foreground truncate">{conversation.last_message}</p>
                      <ConversationTags
                        conversationId={conversation.id}
                        selectedTags={conversationTags[conversation.id] || []}
                        onTagsChange={(tags) => setConversationTags(prev => ({ ...prev, [conversation.id]: tags }))}
                        compact
                      />
                    </div>
                    {conversation.unread_count > 0 && (
                      <span className="flex h-5 w-5 items-center justify-center rounded-full bg-secondary text-xs text-secondary-foreground">{conversation.unread_count}</span>
                    )}
                  </div>
                </button>
              ))
            )}
          </div>
        </div>

        <div className="flex-1 flex flex-col">
          {selectedConversation ? (
            <>
              <div className="flex items-center justify-between gap-3 p-4 border-b border-border">
                <div className="flex items-center gap-3">
                  <PlatformIcon platform={selectedConversation.platform} />
                  <div>
                    <div className="font-medium text-foreground">{selectedConversation.customer_name}</div>
                    <div className="text-sm text-muted-foreground capitalize">{selectedConversation.platform}</div>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <ConversationTags
                    conversationId={selectedConversation.id}
                    selectedTags={conversationTags[selectedConversation.id] || []}
                    onTagsChange={(tags) => setConversationTags(prev => ({ ...prev, [selectedConversation.id]: tags }))}
                  />
                  <Button variant="ghost" size="icon" onClick={() => toast.info('View customer profile')}>
                    <User className="h-4 w-4" />
                  </Button>
                </div>
              </div>

              <div className="flex-1 overflow-y-auto p-4 space-y-4 scrollbar-thin">
                {messages.map((message) => (
                  <div key={message.id} className={cn('flex', message.sender === 'business' ? 'justify-end' : 'justify-start')}>
                    <div className={cn('max-w-[70%] rounded-lg px-4 py-2', message.sender === 'business' ? 'bg-primary text-primary-foreground' : 'bg-muted text-foreground')}>
                      <p>{message.content}</p>
                      <p className={cn('text-xs mt-1', message.sender === 'business' ? 'text-primary-foreground/70' : 'text-muted-foreground')}>{formatTime(message.timestamp)}</p>
                    </div>
                  </div>
                ))}
                <div ref={messagesEndRef} />
              </div>

              <div className="p-4 border-t border-border">
                <div className="flex gap-2">
                  <Button variant="outline" size="icon" onClick={() => setTemplatesOpen(true)} title="Quick replies">
                    <Zap className="h-4 w-4" />
                  </Button>
                  <Input
                    ref={inputRef}
                    placeholder="Type a message... (R to focus)"
                    value={newMessage}
                    onChange={(e) => setNewMessage(e.target.value)}
                    onKeyDown={(e) => e.key === 'Enter' && handleSendMessage()}
                    disabled={isLoading}
                  />
                  <Button onClick={handleSendMessage} disabled={isLoading || !newMessage.trim()}>
                    <Send className="h-4 w-4" />
                  </Button>
                </div>
              </div>
            </>
          ) : (
            <div className="flex-1 flex flex-col items-center justify-center text-muted-foreground">
              <p className="text-lg">Select a conversation</p>
              <p className="text-sm">Use J/K to navigate, R to reply</p>
            </div>
          )}
        </div>
      </div>

      <QuickReplyTemplates open={templatesOpen} onOpenChange={setTemplatesOpen} onSelect={handleTemplateSelect} />
    </DashboardLayout>
  );
}
