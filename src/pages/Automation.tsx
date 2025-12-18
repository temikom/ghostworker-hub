import { useState } from 'react';
import { DashboardLayout } from '@/components/layout/DashboardLayout';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Switch } from '@/components/ui/switch';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { 
  Zap,
  Plus,
  Play,
  Pause,
  Trash2,
  Clock,
  MessageSquare,
  Bot,
  GitBranch,
  Settings
} from 'lucide-react';
import { toast } from 'sonner';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';

interface Workflow {
  id: string;
  name: string;
  description: string;
  trigger: string;
  isActive: boolean;
  lastRun?: string;
  runs: number;
}

interface AutoResponder {
  id: string;
  name: string;
  trigger: string;
  response: string;
  isActive: boolean;
}

interface ScheduledMessage {
  id: string;
  name: string;
  message: string;
  schedule: string;
  platform: string;
  isActive: boolean;
}

export default function Automation() {
  const [workflows, setWorkflows] = useState<Workflow[]>([
    {
      id: '1',
      name: 'New Order Notification',
      description: 'Send notification when a new order is placed',
      trigger: 'order.created',
      isActive: true,
      lastRun: '2 hours ago',
      runs: 45,
    },
    {
      id: '2',
      name: 'Welcome Message',
      description: 'Send welcome message to new customers',
      trigger: 'customer.created',
      isActive: true,
      lastRun: '30 minutes ago',
      runs: 120,
    },
  ]);

  const [autoResponders, setAutoResponders] = useState<AutoResponder[]>([
    {
      id: '1',
      name: 'Business Hours',
      trigger: 'outside_hours',
      response: 'Thanks for reaching out! We are currently closed. Our business hours are 9 AM - 6 PM. We will respond as soon as possible.',
      isActive: true,
    },
    {
      id: '2',
      name: 'FAQ - Shipping',
      trigger: 'keyword:shipping',
      response: 'We offer free shipping on orders over $50. Standard shipping takes 3-5 business days.',
      isActive: false,
    },
  ]);

  const [scheduledMessages, setScheduledMessages] = useState<ScheduledMessage[]>([]);

  const [newAutoResponder, setNewAutoResponder] = useState({
    name: '',
    trigger: '',
    response: '',
  });

  const toggleWorkflow = (id: string) => {
    setWorkflows(workflows.map(w => 
      w.id === id ? { ...w, isActive: !w.isActive } : w
    ));
    toast.success('Workflow updated');
  };

  const toggleAutoResponder = (id: string) => {
    setAutoResponders(autoResponders.map(a => 
      a.id === id ? { ...a, isActive: !a.isActive } : a
    ));
    toast.success('Auto-responder updated');
  };

  const handleCreateAutoResponder = () => {
    if (!newAutoResponder.name || !newAutoResponder.trigger || !newAutoResponder.response) {
      toast.error('Please fill in all fields');
      return;
    }

    setAutoResponders([
      ...autoResponders,
      {
        id: Date.now().toString(),
        ...newAutoResponder,
        isActive: true,
      },
    ]);
    setNewAutoResponder({ name: '', trigger: '', response: '' });
    toast.success('Auto-responder created');
  };

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-semibold text-foreground flex items-center gap-2">
              <Zap className="h-7 w-7 text-warning" />
              Automation
            </h1>
            <p className="text-muted-foreground mt-1">
              Automate your workflows and customer responses
            </p>
          </div>
        </div>

        <Tabs defaultValue="workflows" className="space-y-6">
          <TabsList>
            <TabsTrigger value="workflows">Workflows</TabsTrigger>
            <TabsTrigger value="auto-responders">Auto-Responders</TabsTrigger>
            <TabsTrigger value="scheduled">Scheduled Messages</TabsTrigger>
            <TabsTrigger value="chatbots">Chatbots</TabsTrigger>
          </TabsList>

          {/* Workflows Tab */}
          <TabsContent value="workflows">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-lg font-medium">Active Workflows</h2>
              <Button>
                <Plus className="h-4 w-4 mr-2" />
                Create Workflow
              </Button>
            </div>

            {workflows.length === 0 ? (
              <Card>
                <CardContent className="py-12 text-center">
                  <GitBranch className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
                  <h3 className="text-lg font-medium">No workflows yet</h3>
                  <p className="text-muted-foreground mt-1 mb-4">
                    Create your first workflow to automate tasks
                  </p>
                  <Button>
                    <Plus className="h-4 w-4 mr-2" />
                    Create Workflow
                  </Button>
                </CardContent>
              </Card>
            ) : (
              <div className="grid gap-4">
                {workflows.map((workflow) => (
                  <Card key={workflow.id}>
                    <CardContent className="p-6">
                      <div className="flex items-start justify-between">
                        <div className="flex items-start gap-4">
                          <div className={`p-2 rounded-lg ${workflow.isActive ? 'bg-success/10' : 'bg-muted'}`}>
                            <GitBranch className={`h-5 w-5 ${workflow.isActive ? 'text-success' : 'text-muted-foreground'}`} />
                          </div>
                          <div>
                            <h3 className="font-medium flex items-center gap-2">
                              {workflow.name}
                              <Badge variant={workflow.isActive ? 'default' : 'secondary'}>
                                {workflow.isActive ? 'Active' : 'Paused'}
                              </Badge>
                            </h3>
                            <p className="text-sm text-muted-foreground mt-1">{workflow.description}</p>
                            <div className="flex items-center gap-4 mt-2 text-xs text-muted-foreground">
                              <span>Trigger: {workflow.trigger}</span>
                              <span>•</span>
                              <span>{workflow.runs} runs</span>
                              {workflow.lastRun && (
                                <>
                                  <span>•</span>
                                  <span>Last run: {workflow.lastRun}</span>
                                </>
                              )}
                            </div>
                          </div>
                        </div>
                        <div className="flex items-center gap-2">
                          <Button
                            variant="ghost"
                            size="icon"
                            onClick={() => toggleWorkflow(workflow.id)}
                          >
                            {workflow.isActive ? <Pause className="h-4 w-4" /> : <Play className="h-4 w-4" />}
                          </Button>
                          <Button variant="ghost" size="icon">
                            <Settings className="h-4 w-4" />
                          </Button>
                          <Button variant="ghost" size="icon" className="text-destructive">
                            <Trash2 className="h-4 w-4" />
                          </Button>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            )}
          </TabsContent>

          {/* Auto-Responders Tab */}
          <TabsContent value="auto-responders">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-lg font-medium">Auto-Responders</h2>
              <Dialog>
                <DialogTrigger asChild>
                  <Button>
                    <Plus className="h-4 w-4 mr-2" />
                    Create Auto-Responder
                  </Button>
                </DialogTrigger>
                <DialogContent>
                  <DialogHeader>
                    <DialogTitle>Create Auto-Responder</DialogTitle>
                  </DialogHeader>
                  <div className="space-y-4">
                    <div className="space-y-2">
                      <Label>Name</Label>
                      <Input
                        placeholder="e.g., After Hours Message"
                        value={newAutoResponder.name}
                        onChange={(e) => setNewAutoResponder({ ...newAutoResponder, name: e.target.value })}
                      />
                    </div>
                    <div className="space-y-2">
                      <Label>Trigger</Label>
                      <Input
                        placeholder="e.g., outside_hours or keyword:shipping"
                        value={newAutoResponder.trigger}
                        onChange={(e) => setNewAutoResponder({ ...newAutoResponder, trigger: e.target.value })}
                      />
                    </div>
                    <div className="space-y-2">
                      <Label>Response Message</Label>
                      <Textarea
                        placeholder="Enter the auto-response message..."
                        rows={4}
                        value={newAutoResponder.response}
                        onChange={(e) => setNewAutoResponder({ ...newAutoResponder, response: e.target.value })}
                      />
                    </div>
                    <Button className="w-full" onClick={handleCreateAutoResponder}>
                      Create Auto-Responder
                    </Button>
                  </div>
                </DialogContent>
              </Dialog>
            </div>

            <div className="grid gap-4">
              {autoResponders.map((responder) => (
                <Card key={responder.id}>
                  <CardContent className="p-6">
                    <div className="flex items-start justify-between">
                      <div className="flex items-start gap-4">
                        <div className={`p-2 rounded-lg ${responder.isActive ? 'bg-secondary/10' : 'bg-muted'}`}>
                          <MessageSquare className={`h-5 w-5 ${responder.isActive ? 'text-secondary' : 'text-muted-foreground'}`} />
                        </div>
                        <div className="flex-1">
                          <h3 className="font-medium flex items-center gap-2">
                            {responder.name}
                            <Badge variant={responder.isActive ? 'default' : 'secondary'}>
                              {responder.isActive ? 'Active' : 'Paused'}
                            </Badge>
                          </h3>
                          <p className="text-xs text-muted-foreground mt-1">Trigger: {responder.trigger}</p>
                          <p className="text-sm text-muted-foreground mt-2 bg-muted p-3 rounded-lg">
                            {responder.response}
                          </p>
                        </div>
                      </div>
                      <Switch
                        checked={responder.isActive}
                        onCheckedChange={() => toggleAutoResponder(responder.id)}
                      />
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </TabsContent>

          {/* Scheduled Messages Tab */}
          <TabsContent value="scheduled">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-lg font-medium">Scheduled Messages</h2>
              <Button>
                <Plus className="h-4 w-4 mr-2" />
                Schedule Message
              </Button>
            </div>

            <Card>
              <CardContent className="py-12 text-center">
                <Clock className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
                <h3 className="text-lg font-medium">No scheduled messages</h3>
                <p className="text-muted-foreground mt-1 mb-4">
                  Schedule messages to be sent at specific times
                </p>
                <Button>
                  <Plus className="h-4 w-4 mr-2" />
                  Schedule First Message
                </Button>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Chatbots Tab */}
          <TabsContent value="chatbots">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-lg font-medium">Chatbots</h2>
              <Button>
                <Plus className="h-4 w-4 mr-2" />
                Create Chatbot
              </Button>
            </div>

            <Card>
              <CardContent className="py-12 text-center">
                <Bot className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
                <h3 className="text-lg font-medium">No chatbots yet</h3>
                <p className="text-muted-foreground mt-1 mb-4">
                  Create AI-powered chatbots to handle customer inquiries
                </p>
                <Button>
                  <Plus className="h-4 w-4 mr-2" />
                  Create First Chatbot
                </Button>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </DashboardLayout>
  );
}
