import { useState } from 'react';
import { DashboardLayout } from '@/components/layout/DashboardLayout';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { VoiceTranscription } from '@/components/ai/VoiceTranscription';
import { SmartRouting } from '@/components/ai/SmartRouting';
import { SentimentAnalysis } from '@/components/ai/SentimentAnalysis';
import { AutoTranslation } from '@/components/ai/AutoTranslation';
import { Mic, Route, Brain, Languages } from 'lucide-react';

export default function AIFeatures() {
  const [activeTab, setActiveTab] = useState('transcription');

  const features = [
    { id: 'transcription', label: 'Voice Transcription', icon: Mic, component: VoiceTranscription },
    { id: 'routing', label: 'Smart Routing', icon: Route, component: SmartRouting },
    { id: 'sentiment', label: 'Sentiment Analysis', icon: Brain, component: SentimentAnalysis },
    { id: 'translation', label: 'Auto-Translation', icon: Languages, component: AutoTranslation },
  ];

  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div>
          <h2 className="text-2xl font-bold text-foreground">AI Features</h2>
          <p className="text-muted-foreground">Enhance your customer interactions with AI</p>
        </div>

        <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
          <TabsList className="grid w-full grid-cols-4">
            {features.map((feature) => (
              <TabsTrigger key={feature.id} value={feature.id} className="flex items-center gap-2">
                <feature.icon className="h-4 w-4" />
                <span className="hidden sm:inline">{feature.label}</span>
              </TabsTrigger>
            ))}
          </TabsList>

          {features.map((feature) => (
            <TabsContent key={feature.id} value={feature.id}>
              <feature.component />
            </TabsContent>
          ))}
        </Tabs>
      </div>
    </DashboardLayout>
  );
}
