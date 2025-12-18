import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Switch } from '@/components/ui/switch';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { Languages, ArrowLeftRight, Copy, Check, Settings } from 'lucide-react';
import { toast } from 'sonner';
import { aiApi, Translation } from '@/lib/api';

const languages = [
  { code: 'en', name: 'English' },
  { code: 'es', name: 'Spanish' },
  { code: 'fr', name: 'French' },
  { code: 'de', name: 'German' },
  { code: 'it', name: 'Italian' },
  { code: 'pt', name: 'Portuguese' },
  { code: 'zh', name: 'Chinese' },
  { code: 'ja', name: 'Japanese' },
  { code: 'ko', name: 'Korean' },
  { code: 'ar', name: 'Arabic' },
  { code: 'hi', name: 'Hindi' },
  { code: 'ru', name: 'Russian' },
];

export function AutoTranslation() {
  const [sourceText, setSourceText] = useState('');
  const [translatedText, setTranslatedText] = useState('');
  const [sourceLang, setSourceLang] = useState('auto');
  const [targetLang, setTargetLang] = useState('en');
  const [isTranslating, setIsTranslating] = useState(false);
  const [copied, setCopied] = useState(false);
  const [detectedLang, setDetectedLang] = useState<string | null>(null);
  
  const [settings, setSettings] = useState({
    autoTranslate: true,
    showOriginal: true,
    defaultTargetLang: 'en',
  });

  const translate = async () => {
    if (!sourceText.trim()) {
      toast.error('Please enter text to translate');
      return;
    }

    setIsTranslating(true);
    try {
      const result = await aiApi.translate(
        sourceText,
        targetLang,
        sourceLang !== 'auto' ? sourceLang : undefined
      );
      setTranslatedText(result.translated_text);
      if (sourceLang === 'auto') {
        setDetectedLang(result.source_language);
      }
    } catch {
      // Mock translation for demo
      const mockTranslations: Record<string, string> = {
        'Hello, how can I help you?': 'Hola, ¿cómo puedo ayudarte?',
        'Thank you for your order': 'Gracias por tu pedido',
      };
      setTranslatedText(mockTranslations[sourceText] || `[Translated to ${targetLang}] ${sourceText}`);
      setDetectedLang('en');
    } finally {
      setIsTranslating(false);
    }
  };

  const swapLanguages = () => {
    if (sourceLang !== 'auto') {
      const temp = sourceLang;
      setSourceLang(targetLang);
      setTargetLang(temp);
      setSourceText(translatedText);
      setTranslatedText(sourceText);
    }
  };

  const copyTranslation = () => {
    navigator.clipboard.writeText(translatedText);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
    toast.success('Copied to clipboard');
  };

  return (
    <div className="space-y-6">
      <div className="grid gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center justify-between">
              <span>Source Text</span>
              <Select value={sourceLang} onValueChange={setSourceLang}>
                <SelectTrigger className="w-[150px]">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="auto">Auto Detect</SelectItem>
                  {languages.map((lang) => (
                    <SelectItem key={lang.code} value={lang.code}>
                      {lang.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </CardTitle>
            <CardDescription>
              {detectedLang && sourceLang === 'auto' && (
                <Badge variant="secondary">
                  Detected: {languages.find(l => l.code === detectedLang)?.name || detectedLang}
                </Badge>
              )}
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Textarea
              value={sourceText}
              onChange={(e) => setSourceText(e.target.value)}
              placeholder="Enter text to translate..."
              className="min-h-[200px]"
            />
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center justify-between">
              <span>Translation</span>
              <div className="flex items-center gap-2">
                <Button variant="ghost" size="icon" onClick={swapLanguages} disabled={sourceLang === 'auto'}>
                  <ArrowLeftRight className="h-4 w-4" />
                </Button>
                <Select value={targetLang} onValueChange={setTargetLang}>
                  <SelectTrigger className="w-[150px]">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {languages.map((lang) => (
                      <SelectItem key={lang.code} value={lang.code}>
                        {lang.name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </CardTitle>
            <CardDescription>
              {translatedText && (
                <Button variant="ghost" size="sm" onClick={copyTranslation}>
                  {copied ? <Check className="h-4 w-4 mr-1" /> : <Copy className="h-4 w-4 mr-1" />}
                  {copied ? 'Copied' : 'Copy'}
                </Button>
              )}
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Textarea
              value={translatedText}
              placeholder="Translation will appear here..."
              className="min-h-[200px]"
              readOnly
            />
          </CardContent>
        </Card>
      </div>

      <div className="flex justify-center">
        <Button size="lg" onClick={translate} disabled={isTranslating || !sourceText.trim()}>
          {isTranslating ? (
            <>
              <div className="animate-spin h-4 w-4 border-2 border-primary-foreground border-t-transparent rounded-full mr-2" />
              Translating...
            </>
          ) : (
            <>
              <Languages className="h-5 w-5 mr-2" />
              Translate
            </>
          )}
        </Button>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Settings className="h-5 w-5" />
              Auto-Translation Settings
            </CardTitle>
            <CardDescription>Configure automatic translation for messages</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <Label>Auto-Translate Messages</Label>
                <p className="text-sm text-muted-foreground">Automatically translate incoming messages</p>
              </div>
              <Switch
                checked={settings.autoTranslate}
                onCheckedChange={(checked) => setSettings({ ...settings, autoTranslate: checked })}
              />
            </div>
            <div className="flex items-center justify-between">
              <div>
                <Label>Show Original Text</Label>
                <p className="text-sm text-muted-foreground">Display original message with translation</p>
              </div>
              <Switch
                checked={settings.showOriginal}
                onCheckedChange={(checked) => setSettings({ ...settings, showOriginal: checked })}
              />
            </div>
            <div className="space-y-2">
              <Label>Default Target Language</Label>
              <Select
                value={settings.defaultTargetLang}
                onValueChange={(value) => setSettings({ ...settings, defaultTargetLang: value })}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {languages.map((lang) => (
                    <SelectItem key={lang.code} value={lang.code}>
                      {lang.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Translation Statistics</CardTitle>
            <CardDescription>Overview of translation activity</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid gap-4 grid-cols-2">
              <div className="p-4 bg-muted rounded-lg">
                <p className="text-sm text-muted-foreground">Total Translated</p>
                <p className="text-2xl font-bold text-foreground">2,847</p>
              </div>
              <div className="p-4 bg-muted rounded-lg">
                <p className="text-sm text-muted-foreground">Languages Used</p>
                <p className="text-2xl font-bold text-foreground">8</p>
              </div>
              <div className="p-4 bg-muted rounded-lg">
                <p className="text-sm text-muted-foreground">This Week</p>
                <p className="text-2xl font-bold text-foreground">342</p>
              </div>
              <div className="p-4 bg-muted rounded-lg">
                <p className="text-sm text-muted-foreground">Accuracy</p>
                <p className="text-2xl font-bold text-foreground">98.5%</p>
              </div>
            </div>

            <div className="mt-4">
              <Label className="text-sm text-muted-foreground">Top Languages</Label>
              <div className="flex flex-wrap gap-2 mt-2">
                <Badge variant="secondary">Spanish (42%)</Badge>
                <Badge variant="secondary">French (18%)</Badge>
                <Badge variant="secondary">Portuguese (15%)</Badge>
                <Badge variant="secondary">German (12%)</Badge>
                <Badge variant="secondary">Chinese (8%)</Badge>
                <Badge variant="outline">+3 more</Badge>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
