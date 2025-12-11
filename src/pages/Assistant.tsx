import { useState, useEffect, useRef } from 'react';
import { DashboardLayout } from '@/components/layout/DashboardLayout';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Plus, Send, CheckCircle, Clock, Circle, Bot } from 'lucide-react';
import { cn } from '@/lib/utils';
import { Task, assistantApi } from '@/lib/api';
import { toast } from 'sonner';

interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
}

const statusIcons: Record<string, typeof Circle> = {
  pending: Circle,
  in_progress: Clock,
  completed: CheckCircle,
};

const statusColors: Record<string, string> = {
  pending: 'text-muted-foreground',
  in_progress: 'text-warning',
  completed: 'text-success',
};

export default function Assistant() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [newTask, setNewTask] = useState('');
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([]);
  const [chatInput, setChatInput] = useState('');
  const [isAddingTask, setIsAddingTask] = useState(false);
  const [isChatting, setIsChatting] = useState(false);
  const chatEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    loadTasks();
  }, []);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [chatMessages]);

  const loadTasks = async () => {
    try {
      const data = await assistantApi.getTasks();
      setTasks(data);
    } catch (error) {
      // Silent fail
    }
  };

  const handleAddTask = async () => {
    if (!newTask.trim()) return;

    setIsAddingTask(true);
    try {
      await assistantApi.createTask({ title: newTask });
      toast.success('Task added');
      setNewTask('');
      loadTasks();
    } catch (error) {
      toast.error('Failed to add task');
    } finally {
      setIsAddingTask(false);
    }
  };

  const handleChat = async () => {
    if (!chatInput.trim()) return;

    const userMessage = chatInput;
    setChatMessages((prev) => [...prev, { role: 'user', content: userMessage }]);
    setChatInput('');
    setIsChatting(true);

    try {
      const { response } = await assistantApi.chat(userMessage);
      setChatMessages((prev) => [...prev, { role: 'assistant', content: response }]);
    } catch (error) {
      setChatMessages((prev) => [
        ...prev,
        { role: 'assistant', content: 'Sorry, I encountered an error. Please try again.' },
      ]);
    } finally {
      setIsChatting(false);
    }
  };

  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div>
          <h2 className="text-2xl font-bold text-foreground">Personal Assistant</h2>
          <p className="text-muted-foreground">Manage tasks and chat with AI</p>
        </div>

        <div className="grid gap-6 lg:grid-cols-2">
          {/* Tasks */}
          <Card className="lg:row-span-2">
            <CardHeader>
              <CardTitle className="text-lg">Tasks</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {/* Add Task */}
              <div className="flex gap-2">
                <Input
                  placeholder="Add a new task..."
                  value={newTask}
                  onChange={(e) => setNewTask(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && handleAddTask()}
                  disabled={isAddingTask}
                />
                <Button onClick={handleAddTask} disabled={isAddingTask || !newTask.trim()}>
                  <Plus className="h-4 w-4" />
                </Button>
              </div>

              {/* Task List */}
              <div className="space-y-2 max-h-96 overflow-y-auto scrollbar-thin">
                {tasks.length === 0 ? (
                  <div className="text-center py-8 text-muted-foreground">
                    <p>No tasks yet</p>
                    <p className="text-sm">Add a task to get started</p>
                  </div>
                ) : (
                  tasks.map((task) => {
                    const StatusIcon = statusIcons[task.status];
                    return (
                      <div
                        key={task.id}
                        className="flex items-start gap-3 p-3 rounded-lg border border-border hover:bg-muted/50 transition-colors"
                      >
                        <StatusIcon className={cn('h-5 w-5 mt-0.5', statusColors[task.status])} />
                        <div className="flex-1 min-w-0">
                          <p className="font-medium text-foreground">{task.title}</p>
                          {task.description && (
                            <p className="text-sm text-muted-foreground">{task.description}</p>
                          )}
                        </div>
                        <Badge variant="secondary" className="text-xs">
                          {task.status.replace('_', ' ')}
                        </Badge>
                      </div>
                    );
                  })
                )}
              </div>
            </CardContent>
          </Card>

          {/* AI Chat */}
          <Card className="flex flex-col h-[500px]">
            <CardHeader className="pb-3">
              <CardTitle className="text-lg flex items-center gap-2">
                <Bot className="h-5 w-5 text-secondary" />
                AI Assistant
              </CardTitle>
            </CardHeader>
            <CardContent className="flex-1 flex flex-col min-h-0">
              {/* Chat Messages */}
              <div className="flex-1 overflow-y-auto space-y-3 mb-4 scrollbar-thin">
                {chatMessages.length === 0 ? (
                  <div className="flex flex-col items-center justify-center h-full text-muted-foreground">
                    <Bot className="h-12 w-12 mb-3 opacity-50" />
                    <p>Start a conversation</p>
                    <p className="text-sm">Ask me anything about your business</p>
                  </div>
                ) : (
                  chatMessages.map((msg, index) => (
                    <div
                      key={index}
                      className={cn(
                        'flex',
                        msg.role === 'user' ? 'justify-end' : 'justify-start'
                      )}
                    >
                      <div
                        className={cn(
                          'max-w-[80%] rounded-lg px-4 py-2',
                          msg.role === 'user'
                            ? 'bg-primary text-primary-foreground'
                            : 'bg-muted text-foreground'
                        )}
                      >
                        {msg.content}
                      </div>
                    </div>
                  ))
                )}
                {isChatting && (
                  <div className="flex justify-start">
                    <div className="bg-muted rounded-lg px-4 py-2">
                      <div className="flex space-x-1">
                        <div className="w-2 h-2 bg-muted-foreground rounded-full animate-bounce" />
                        <div className="w-2 h-2 bg-muted-foreground rounded-full animate-bounce [animation-delay:0.2s]" />
                        <div className="w-2 h-2 bg-muted-foreground rounded-full animate-bounce [animation-delay:0.4s]" />
                      </div>
                    </div>
                  </div>
                )}
                <div ref={chatEndRef} />
              </div>

              {/* Chat Input */}
              <div className="flex gap-2">
                <Input
                  placeholder="Ask the assistant..."
                  value={chatInput}
                  onChange={(e) => setChatInput(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && handleChat()}
                  disabled={isChatting}
                />
                <Button onClick={handleChat} disabled={isChatting || !chatInput.trim()}>
                  <Send className="h-4 w-4" />
                </Button>
              </div>
            </CardContent>
          </Card>

          {/* Task Suggestions */}
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-lg">Suggested Tasks</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                {['Connect WhatsApp integration', 'Set up email templates', 'Review pending orders'].map(
                  (suggestion, index) => (
                    <button
                      key={index}
                      onClick={() => setNewTask(suggestion)}
                      className="w-full text-left p-3 rounded-lg border border-border hover:bg-muted/50 transition-colors text-sm"
                    >
                      {suggestion}
                    </button>
                  )
                )}
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </DashboardLayout>
  );
}
