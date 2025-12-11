import { useState, useEffect } from 'react';
import { DashboardLayout } from '@/components/layout/DashboardLayout';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, LineChart, Line, PieChart, Pie, Cell } from 'recharts';
import { MessageSquare, Clock, TrendingUp, Users } from 'lucide-react';

interface AnalyticsData {
  messageVolume: { date: string; messages: number }[];
  responseTime: { date: string; avgTime: number }[];
  platformBreakdown: { platform: string; count: number; color: string }[];
  stats: {
    totalMessages: number;
    avgResponseTime: number;
    totalConversations: number;
    newCustomers: number;
  };
}

export default function Analytics() {
  const [timeRange, setTimeRange] = useState('7d');
  const [data, setData] = useState<AnalyticsData | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    loadAnalytics();
  }, [timeRange]);

  const loadAnalytics = async () => {
    setIsLoading(true);
    try {
      const response = await fetch(`/api/analytics?range=${timeRange}`);
      if (response.ok) {
        const analytics = await response.json();
        setData(analytics);
      }
    } catch {
      // API not connected yet
    } finally {
      setIsLoading(false);
    }
  };

  const PLATFORM_COLORS = {
    whatsapp: 'hsl(142 70% 45%)',
    instagram: 'hsl(340 75% 55%)',
    tiktok: 'hsl(0 0% 10%)',
    email: 'hsl(205 100% 50%)',
  };

  const stats = [
    {
      title: 'Total Messages',
      value: data?.stats.totalMessages || 0,
      icon: MessageSquare,
      change: '+12%',
    },
    {
      title: 'Avg Response Time',
      value: data?.stats.avgResponseTime ? `${data.stats.avgResponseTime}m` : '0m',
      icon: Clock,
      change: '-8%',
    },
    {
      title: 'Active Conversations',
      value: data?.stats.totalConversations || 0,
      icon: TrendingUp,
      change: '+5%',
    },
    {
      title: 'New Customers',
      value: data?.stats.newCustomers || 0,
      icon: Users,
      change: '+15%',
    },
  ];

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-semibold text-foreground">Analytics</h1>
            <p className="text-muted-foreground mt-1">Track your messaging performance</p>
          </div>
          <Select value={timeRange} onValueChange={setTimeRange}>
            <SelectTrigger className="w-32">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="24h">Last 24h</SelectItem>
              <SelectItem value="7d">Last 7 days</SelectItem>
              <SelectItem value="30d">Last 30 days</SelectItem>
              <SelectItem value="90d">Last 90 days</SelectItem>
            </SelectContent>
          </Select>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {stats.map((stat) => (
            <Card key={stat.title}>
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <stat.icon className="h-5 w-5 text-muted-foreground" />
                  <span className="text-xs text-success font-medium">{stat.change}</span>
                </div>
                <p className="text-2xl font-semibold text-foreground mt-3">{stat.value}</p>
                <p className="text-sm text-muted-foreground mt-1">{stat.title}</p>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Charts Row */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Message Volume Chart */}
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Message Volume</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="h-64">
                {data?.messageVolume && data.messageVolume.length > 0 ? (
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={data.messageVolume}>
                      <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
                      <XAxis dataKey="date" stroke="hsl(var(--muted-foreground))" fontSize={12} />
                      <YAxis stroke="hsl(var(--muted-foreground))" fontSize={12} />
                      <Tooltip
                        contentStyle={{
                          backgroundColor: 'hsl(var(--card))',
                          border: '1px solid hsl(var(--border))',
                          borderRadius: '8px',
                        }}
                      />
                      <Bar dataKey="messages" fill="hsl(var(--secondary))" radius={[4, 4, 0, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                ) : (
                  <div className="h-full flex items-center justify-center text-muted-foreground">
                    <p className="text-sm">No message data available</p>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>

          {/* Response Time Chart */}
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Response Time (minutes)</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="h-64">
                {data?.responseTime && data.responseTime.length > 0 ? (
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={data.responseTime}>
                      <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
                      <XAxis dataKey="date" stroke="hsl(var(--muted-foreground))" fontSize={12} />
                      <YAxis stroke="hsl(var(--muted-foreground))" fontSize={12} />
                      <Tooltip
                        contentStyle={{
                          backgroundColor: 'hsl(var(--card))',
                          border: '1px solid hsl(var(--border))',
                          borderRadius: '8px',
                        }}
                      />
                      <Line
                        type="monotone"
                        dataKey="avgTime"
                        stroke="hsl(var(--primary))"
                        strokeWidth={2}
                        dot={{ fill: 'hsl(var(--primary))' }}
                      />
                    </LineChart>
                  </ResponsiveContainer>
                ) : (
                  <div className="h-full flex items-center justify-center text-muted-foreground">
                    <p className="text-sm">No response time data available</p>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Platform Breakdown */}
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Platform Breakdown</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
              <div className="h-64">
                {data?.platformBreakdown && data.platformBreakdown.length > 0 ? (
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                      <Pie
                        data={data.platformBreakdown}
                        cx="50%"
                        cy="50%"
                        innerRadius={60}
                        outerRadius={100}
                        paddingAngle={2}
                        dataKey="count"
                      >
                        {data.platformBreakdown.map((entry, index) => (
                          <Cell key={index} fill={entry.color} />
                        ))}
                      </Pie>
                      <Tooltip
                        contentStyle={{
                          backgroundColor: 'hsl(var(--card))',
                          border: '1px solid hsl(var(--border))',
                          borderRadius: '8px',
                        }}
                      />
                    </PieChart>
                  </ResponsiveContainer>
                ) : (
                  <div className="h-full flex items-center justify-center text-muted-foreground">
                    <p className="text-sm">No platform data available</p>
                  </div>
                )}
              </div>

              <div className="flex flex-col justify-center space-y-4">
                {(data?.platformBreakdown || []).map((platform) => (
                  <div key={platform.platform} className="flex items-center gap-3">
                    <div
                      className="w-4 h-4 rounded-full"
                      style={{ backgroundColor: platform.color }}
                    />
                    <span className="text-sm text-foreground capitalize flex-1">
                      {platform.platform}
                    </span>
                    <span className="text-sm font-medium text-foreground">{platform.count}</span>
                  </div>
                ))}
                {(!data?.platformBreakdown || data.platformBreakdown.length === 0) && (
                  <p className="text-sm text-muted-foreground">
                    Connect your platforms to see breakdown
                  </p>
                )}
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </DashboardLayout>
  );
}
