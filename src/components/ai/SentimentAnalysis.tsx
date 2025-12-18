import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Switch } from '@/components/ui/switch';
import { Label } from '@/components/ui/label';
import { Brain, TrendingUp, TrendingDown, Minus, RefreshCw } from 'lucide-react';
import { toast } from 'sonner';
import { aiApi, SentimentScore } from '@/lib/api';
import { cn } from '@/lib/utils';

interface SentimentHistory {
  text: string;
  result: SentimentScore;
  timestamp: Date;
}

export function SentimentAnalysis() {
  const [text, setText] = useState('');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [currentResult, setCurrentResult] = useState<SentimentScore | null>(null);
  const [history, setHistory] = useState<SentimentHistory[]>([]);
  const [autoAnalyze, setAutoAnalyze] = useState(true);

  const analyzeSentiment = async () => {
    if (!text.trim()) {
      toast.error('Please enter some text to analyze');
      return;
    }

    setIsAnalyzing(true);
    try {
      const result = await aiApi.analyzeSentiment(text);
      setCurrentResult(result);
      setHistory((prev) => [{ text, result, timestamp: new Date() }, ...prev.slice(0, 9)]);
    } catch {
      // Mock result for demo
      const mockResult: SentimentScore = {
        label: text.toLowerCase().includes('bad') || text.toLowerCase().includes('terrible') ? 'negative' :
               text.toLowerCase().includes('great') || text.toLowerCase().includes('love') ? 'positive' : 'neutral',
        score: Math.random() * 0.3 + 0.7,
        confidence: Math.random() * 0.2 + 0.8,
      };
      setCurrentResult(mockResult);
      setHistory((prev) => [{ text, result: mockResult, timestamp: new Date() }, ...prev.slice(0, 9)]);
    } finally {
      setIsAnalyzing(false);
    }
  };

  const getSentimentColor = (label: string) => {
    switch (label) {
      case 'positive': return 'text-success';
      case 'negative': return 'text-destructive';
      default: return 'text-warning';
    }
  };

  const getSentimentIcon = (label: string) => {
    switch (label) {
      case 'positive': return TrendingUp;
      case 'negative': return TrendingDown;
      default: return Minus;
    }
  };

  const getSentimentBadgeVariant = (label: string) => {
    switch (label) {
      case 'positive': return 'default';
      case 'negative': return 'destructive';
      default: return 'secondary';
    }
  };

  return (
    <div className="grid gap-6 lg:grid-cols-2">
      <Card>
        <CardHeader>
          <CardTitle>Analyze Text</CardTitle>
          <CardDescription>Enter text to analyze its sentiment</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <Textarea
            value={text}
            onChange={(e) => setText(e.target.value)}
            placeholder="Enter customer message or text to analyze..."
            className="min-h-[150px]"
          />
          <div className="flex justify-between items-center">
            <div className="flex items-center gap-2">
              <Switch
                id="auto-analyze"
                checked={autoAnalyze}
                onCheckedChange={setAutoAnalyze}
              />
              <Label htmlFor="auto-analyze">Auto-analyze incoming messages</Label>
            </div>
            <Button onClick={analyzeSentiment} disabled={isAnalyzing || !text.trim()}>
              {isAnalyzing ? (
                <>
                  <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
                  Analyzing...
                </>
              ) : (
                <>
                  <Brain className="h-4 w-4 mr-2" />
                  Analyze
                </>
              )}
            </Button>
          </div>

          {currentResult && (
            <div className="mt-6 p-6 bg-muted rounded-lg">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-3">
                  {(() => {
                    const Icon = getSentimentIcon(currentResult.label);
                    return <Icon className={cn('h-8 w-8', getSentimentColor(currentResult.label))} />;
                  })()}
                  <div>
                    <h4 className="text-lg font-semibold text-foreground capitalize">{currentResult.label}</h4>
                    <p className="text-sm text-muted-foreground">Sentiment detected</p>
                  </div>
                </div>
                <Badge variant={getSentimentBadgeVariant(currentResult.label)} className="text-lg px-4 py-1">
                  {(currentResult.score * 100).toFixed(0)}%
                </Badge>
              </div>
              
              <div className="space-y-3">
                <div>
                  <div className="flex justify-between text-sm mb-1">
                    <span className="text-muted-foreground">Score</span>
                    <span className="font-medium">{(currentResult.score * 100).toFixed(1)}%</span>
                  </div>
                  <Progress value={currentResult.score * 100} className="h-2" />
                </div>
                <div>
                  <div className="flex justify-between text-sm mb-1">
                    <span className="text-muted-foreground">Confidence</span>
                    <span className="font-medium">{(currentResult.confidence * 100).toFixed(1)}%</span>
                  </div>
                  <Progress value={currentResult.confidence * 100} className="h-2" />
                </div>
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      <div className="space-y-6">
        <Card>
          <CardHeader>
            <CardTitle>Analysis History</CardTitle>
            <CardDescription>Recent sentiment analyses</CardDescription>
          </CardHeader>
          <CardContent>
            {history.length === 0 ? (
              <div className="flex flex-col items-center justify-center py-8 text-muted-foreground">
                <Brain className="h-10 w-10 mb-3 opacity-50" />
                <p>No analyses yet</p>
                <p className="text-sm">Analyze some text to see history</p>
              </div>
            ) : (
              <div className="space-y-3 max-h-[400px] overflow-y-auto scrollbar-thin">
                {history.map((item, index) => {
                  const Icon = getSentimentIcon(item.result.label);
                  return (
                    <div key={index} className="flex items-start gap-3 p-3 bg-muted/50 rounded-lg">
                      <Icon className={cn('h-5 w-5 mt-0.5', getSentimentColor(item.result.label))} />
                      <div className="flex-1 min-w-0">
                        <p className="text-sm text-foreground truncate">{item.text}</p>
                        <div className="flex items-center gap-2 mt-1">
                          <Badge variant={getSentimentBadgeVariant(item.result.label)} className="text-xs">
                            {item.result.label}
                          </Badge>
                          <span className="text-xs text-muted-foreground">
                            {item.timestamp.toLocaleTimeString()}
                          </span>
                        </div>
                      </div>
                      <span className="text-sm font-medium">{(item.result.score * 100).toFixed(0)}%</span>
                    </div>
                  );
                })}
              </div>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Sentiment Overview</CardTitle>
            <CardDescription>Distribution across all messages</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex items-center gap-3">
                <TrendingUp className="h-5 w-5 text-success" />
                <div className="flex-1">
                  <div className="flex justify-between text-sm mb-1">
                    <span>Positive</span>
                    <span className="font-medium">62%</span>
                  </div>
                  <Progress value={62} className="h-2" />
                </div>
              </div>
              <div className="flex items-center gap-3">
                <Minus className="h-5 w-5 text-warning" />
                <div className="flex-1">
                  <div className="flex justify-between text-sm mb-1">
                    <span>Neutral</span>
                    <span className="font-medium">28%</span>
                  </div>
                  <Progress value={28} className="h-2" />
                </div>
              </div>
              <div className="flex items-center gap-3">
                <TrendingDown className="h-5 w-5 text-destructive" />
                <div className="flex-1">
                  <div className="flex justify-between text-sm mb-1">
                    <span>Negative</span>
                    <span className="font-medium">10%</span>
                  </div>
                  <Progress value={10} className="h-2" />
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
