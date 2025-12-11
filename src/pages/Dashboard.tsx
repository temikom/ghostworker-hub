import { DashboardLayout } from '@/components/layout/DashboardLayout';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { MessageSquare, ShoppingBag, Zap, Plug } from 'lucide-react';

const stats = [
  { title: 'Messages Today', value: '0', icon: MessageSquare, change: '+0%' },
  { title: 'Total Orders', value: '0', icon: ShoppingBag, change: '+0%' },
  { title: 'Active Automations', value: '0', icon: Zap, change: '+0%' },
  { title: 'Connected Platforms', value: '0', icon: Plug, change: '0 of 4' },
];

export default function Dashboard() {
  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div>
          <h2 className="text-2xl font-bold text-foreground">Dashboard</h2>
          <p className="text-muted-foreground">Overview of your business automation</p>
        </div>

        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {stats.map((stat) => (
            <Card key={stat.title}>
              <CardHeader className="flex flex-row items-center justify-between pb-2">
                <CardTitle className="text-sm font-medium text-muted-foreground">
                  {stat.title}
                </CardTitle>
                <stat.icon className="h-5 w-5 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold text-foreground">{stat.value}</div>
                <p className="text-xs text-muted-foreground mt-1">{stat.change}</p>
              </CardContent>
            </Card>
          ))}
        </div>

        <div className="grid gap-6 lg:grid-cols-2">
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Recent Activity</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex flex-col items-center justify-center py-8 text-muted-foreground">
                <MessageSquare className="h-12 w-12 mb-3 opacity-50" />
                <p>No recent activity</p>
                <p className="text-sm">Connect your platforms to start receiving messages</p>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Quick Actions</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <button className="w-full rounded-lg border border-border p-4 text-left hover:bg-muted transition-colors">
                <div className="font-medium text-foreground">Connect WhatsApp</div>
                <div className="text-sm text-muted-foreground">Set up WhatsApp Cloud API</div>
              </button>
              <button className="w-full rounded-lg border border-border p-4 text-left hover:bg-muted transition-colors">
                <div className="font-medium text-foreground">Connect Instagram</div>
                <div className="text-sm text-muted-foreground">Set up Instagram Messaging</div>
              </button>
              <button className="w-full rounded-lg border border-border p-4 text-left hover:bg-muted transition-colors">
                <div className="font-medium text-foreground">View Documentation</div>
                <div className="text-sm text-muted-foreground">Learn how to use GhostWorker</div>
              </button>
            </CardContent>
          </Card>
        </div>
      </div>
    </DashboardLayout>
  );
}
