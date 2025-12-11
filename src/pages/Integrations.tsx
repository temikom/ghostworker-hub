import { useState, useEffect } from 'react';
import { DashboardLayout } from '@/components/layout/DashboardLayout';
import { PlatformIcon } from '@/components/icons/PlatformIcon';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Badge } from '@/components/ui/badge';
import { Integration, integrationsApi } from '@/lib/api';
import { toast } from 'sonner';

type Platform = 'whatsapp' | 'instagram' | 'tiktok' | 'email';

interface IntegrationConfig {
  platform: Platform;
  title: string;
  description: string;
  fields: { name: string; label: string; type: string; placeholder: string }[];
}

const integrationConfigs: IntegrationConfig[] = [
  {
    platform: 'whatsapp',
    title: 'WhatsApp Cloud API',
    description: 'Connect your WhatsApp Business account',
    fields: [
      { name: 'phone_id', label: 'Phone ID', type: 'text', placeholder: 'Enter Phone ID' },
      { name: 'access_token', label: 'Access Token', type: 'password', placeholder: 'Enter Access Token' },
      { name: 'verify_token', label: 'Verify Token', type: 'text', placeholder: 'Enter Verify Token' },
    ],
  },
  {
    platform: 'instagram',
    title: 'Instagram Messaging API',
    description: 'Connect your Instagram Business account',
    fields: [
      { name: 'access_token', label: 'Access Token', type: 'password', placeholder: 'Enter Access Token' },
    ],
  },
  {
    platform: 'tiktok',
    title: 'TikTok Business Messages',
    description: 'Connect your TikTok Business account',
    fields: [
      { name: 'app_id', label: 'App ID', type: 'text', placeholder: 'Enter App ID' },
      { name: 'secret', label: 'App Secret', type: 'password', placeholder: 'Enter App Secret' },
    ],
  },
  {
    platform: 'email',
    title: 'Email (SMTP)',
    description: 'Connect your email via SMTP',
    fields: [
      { name: 'host', label: 'SMTP Host', type: 'text', placeholder: 'smtp.example.com' },
      { name: 'port', label: 'Port', type: 'text', placeholder: '587' },
      { name: 'username', label: 'Username', type: 'text', placeholder: 'Enter username' },
      { name: 'password', label: 'Password', type: 'password', placeholder: 'Enter password' },
    ],
  },
];

export default function Integrations() {
  const [integrations, setIntegrations] = useState<Integration[]>([]);
  const [selectedPlatform, setSelectedPlatform] = useState<IntegrationConfig | null>(null);
  const [credentials, setCredentials] = useState<Record<string, string>>({});
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    loadIntegrations();
  }, []);

  const loadIntegrations = async () => {
    try {
      const data = await integrationsApi.list();
      setIntegrations(data);
    } catch (error) {
      // Silent fail - will show default disconnected state
    }
  };

  const getIntegrationStatus = (platform: Platform): 'connected' | 'disconnected' => {
    const integration = integrations.find((i) => i.platform === platform);
    return integration?.status || 'disconnected';
  };

  const handleConnect = async () => {
    if (!selectedPlatform) return;

    setIsLoading(true);
    try {
      await integrationsApi.connect({
        platform: selectedPlatform.platform,
        credentials,
      });
      toast.success(`${selectedPlatform.title} connected successfully`);
      setSelectedPlatform(null);
      setCredentials({});
      loadIntegrations();
    } catch (error) {
      toast.error(error instanceof Error ? error.message : 'Failed to connect');
    } finally {
      setIsLoading(false);
    }
  };

  const handleDisconnect = async (platform: Platform) => {
    try {
      await integrationsApi.disconnect(platform);
      toast.success('Integration disconnected');
      loadIntegrations();
    } catch (error) {
      toast.error('Failed to disconnect');
    }
  };

  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div>
          <h2 className="text-2xl font-bold text-foreground">Integrations</h2>
          <p className="text-muted-foreground">Connect your messaging platforms</p>
        </div>

        <div className="grid gap-4 sm:grid-cols-2">
          {integrationConfigs.map((config) => {
            const status = getIntegrationStatus(config.platform);
            const isConnected = status === 'connected';

            return (
              <Card key={config.platform}>
                <CardHeader className="flex flex-row items-center justify-between pb-2">
                  <div className="flex items-center gap-3">
                    <PlatformIcon platform={config.platform} className="h-8 w-8" />
                    <div>
                      <CardTitle className="text-base">{config.title}</CardTitle>
                      <p className="text-sm text-muted-foreground">{config.description}</p>
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="flex items-center justify-between">
                    <Badge
                      variant={isConnected ? 'default' : 'secondary'}
                      className={isConnected ? 'bg-success text-success-foreground' : ''}
                    >
                      {isConnected ? 'Connected' : 'Not Connected'}
                    </Badge>
                    {isConnected ? (
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handleDisconnect(config.platform)}
                      >
                        Disconnect
                      </Button>
                    ) : (
                      <Button size="sm" onClick={() => setSelectedPlatform(config)}>
                        Connect
                      </Button>
                    )}
                  </div>
                </CardContent>
              </Card>
            );
          })}
        </div>

        {/* Connect Modal */}
        <Dialog open={!!selectedPlatform} onOpenChange={() => setSelectedPlatform(null)}>
          <DialogContent>
            <DialogHeader>
              <DialogTitle className="flex items-center gap-3">
                {selectedPlatform && (
                  <>
                    <PlatformIcon platform={selectedPlatform.platform} className="h-6 w-6" />
                    Connect {selectedPlatform.title}
                  </>
                )}
              </DialogTitle>
            </DialogHeader>

            <form
              onSubmit={(e) => {
                e.preventDefault();
                handleConnect();
              }}
              className="space-y-4"
            >
              {selectedPlatform?.fields.map((field) => (
                <div key={field.name} className="space-y-2">
                  <Label htmlFor={field.name}>{field.label}</Label>
                  <Input
                    id={field.name}
                    type={field.type}
                    placeholder={field.placeholder}
                    value={credentials[field.name] || ''}
                    onChange={(e) =>
                      setCredentials({ ...credentials, [field.name]: e.target.value })
                    }
                    required
                  />
                </div>
              ))}

              <div className="flex justify-end gap-2">
                <Button type="button" variant="outline" onClick={() => setSelectedPlatform(null)}>
                  Cancel
                </Button>
                <Button type="submit" disabled={isLoading}>
                  {isLoading ? 'Connecting...' : 'Connect'}
                </Button>
              </div>
            </form>
          </DialogContent>
        </Dialog>
      </div>
    </DashboardLayout>
  );
}
