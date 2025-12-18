import { useState, useRef } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Badge } from '@/components/ui/badge';
import { Mic, MicOff, Upload, Play, Pause, Copy, Download } from 'lucide-react';
import { toast } from 'sonner';
import { aiApi } from '@/lib/api';

interface TranscriptionResult {
  text: string;
  language: string;
  duration: number;
  confidence?: number;
}

export function VoiceTranscription() {
  const [isRecording, setIsRecording] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [transcription, setTranscription] = useState<TranscriptionResult | null>(null);
  const [audioUrl, setAudioUrl] = useState<string | null>(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const audioRef = useRef<HTMLAudioElement>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<Blob[]>([]);

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;
      chunksRef.current = [];

      mediaRecorder.ondataavailable = (e) => {
        if (e.data.size > 0) chunksRef.current.push(e.data);
      };

      mediaRecorder.onstop = async () => {
        const blob = new Blob(chunksRef.current, { type: 'audio/webm' });
        const url = URL.createObjectURL(blob);
        setAudioUrl(url);
        await processAudio(blob);
        stream.getTracks().forEach((track) => track.stop());
      };

      mediaRecorder.start();
      setIsRecording(true);
    } catch (error) {
      toast.error('Failed to access microphone');
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    }
  };

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    if (!file.type.startsWith('audio/')) {
      toast.error('Please upload an audio file');
      return;
    }

    const url = URL.createObjectURL(file);
    setAudioUrl(url);
    await processAudio(file);
  };

  const processAudio = async (audioBlob: Blob | File) => {
    setIsProcessing(true);
    try {
      const file = audioBlob instanceof File ? audioBlob : new File([audioBlob], 'recording.webm', { type: audioBlob.type });
      const result = await aiApi.transcribeVoice(file);
      setTranscription({
        text: result.text,
        language: result.language,
        duration: result.duration,
      });
      toast.success('Transcription complete');
    } catch (error) {
      toast.error('Failed to transcribe audio');
    } finally {
      setIsProcessing(false);
    }
  };

  const togglePlayback = () => {
    if (!audioRef.current) return;
    if (isPlaying) {
      audioRef.current.pause();
    } else {
      audioRef.current.play();
    }
    setIsPlaying(!isPlaying);
  };

  const copyTranscription = () => {
    if (transcription) {
      navigator.clipboard.writeText(transcription.text);
      toast.success('Copied to clipboard');
    }
  };

  const downloadTranscription = () => {
    if (transcription) {
      const blob = new Blob([transcription.text], { type: 'text/plain' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'transcription.txt';
      a.click();
      URL.revokeObjectURL(url);
    }
  };

  return (
    <div className="grid gap-6 lg:grid-cols-2">
      <Card>
        <CardHeader>
          <CardTitle>Voice Input</CardTitle>
          <CardDescription>Record or upload audio to transcribe</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex flex-col items-center gap-4 p-8 border-2 border-dashed border-border rounded-lg">
            <div className="flex gap-4">
              <Button
                variant={isRecording ? 'destructive' : 'default'}
                size="lg"
                onClick={isRecording ? stopRecording : startRecording}
                disabled={isProcessing}
              >
                {isRecording ? (
                  <>
                    <MicOff className="h-5 w-5 mr-2" />
                    Stop Recording
                  </>
                ) : (
                  <>
                    <Mic className="h-5 w-5 mr-2" />
                    Start Recording
                  </>
                )}
              </Button>
              
              <Button
                variant="outline"
                size="lg"
                onClick={() => fileInputRef.current?.click()}
                disabled={isProcessing || isRecording}
              >
                <Upload className="h-5 w-5 mr-2" />
                Upload Audio
              </Button>
            </div>

            <input
              ref={fileInputRef}
              type="file"
              accept="audio/*"
              className="hidden"
              onChange={handleFileUpload}
            />

            {isRecording && (
              <div className="flex items-center gap-2 text-destructive">
                <span className="animate-pulse h-3 w-3 bg-destructive rounded-full" />
                Recording...
              </div>
            )}

            {isProcessing && (
              <div className="flex items-center gap-2 text-muted-foreground">
                <div className="animate-spin h-4 w-4 border-2 border-primary border-t-transparent rounded-full" />
                Processing...
              </div>
            )}
          </div>

          {audioUrl && (
            <div className="flex items-center gap-3 p-4 bg-muted rounded-lg">
              <Button variant="ghost" size="icon" onClick={togglePlayback}>
                {isPlaying ? <Pause className="h-5 w-5" /> : <Play className="h-5 w-5" />}
              </Button>
              <audio
                ref={audioRef}
                src={audioUrl}
                onEnded={() => setIsPlaying(false)}
                className="hidden"
              />
              <div className="flex-1 h-2 bg-border rounded-full overflow-hidden">
                <div className="h-full bg-primary w-1/3" />
              </div>
              {transcription && (
                <span className="text-sm text-muted-foreground">
                  {Math.floor(transcription.duration / 60)}:{String(Math.floor(transcription.duration % 60)).padStart(2, '0')}
                </span>
              )}
            </div>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            Transcription
            {transcription && (
              <div className="flex gap-2">
                <Button variant="ghost" size="icon" onClick={copyTranscription}>
                  <Copy className="h-4 w-4" />
                </Button>
                <Button variant="ghost" size="icon" onClick={downloadTranscription}>
                  <Download className="h-4 w-4" />
                </Button>
              </div>
            )}
          </CardTitle>
          <CardDescription>
            {transcription ? (
              <div className="flex gap-2">
                <Badge variant="secondary">{transcription.language.toUpperCase()}</Badge>
                <Badge variant="outline">{transcription.duration.toFixed(1)}s</Badge>
              </div>
            ) : (
              'Transcribed text will appear here'
            )}
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Textarea
            value={transcription?.text || ''}
            placeholder="Record or upload audio to see transcription..."
            className="min-h-[200px] resize-none"
            readOnly
          />
        </CardContent>
      </Card>

      <Card className="lg:col-span-2">
        <CardHeader>
          <CardTitle>Settings</CardTitle>
          <CardDescription>Configure voice transcription behavior</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <div className="p-4 border border-border rounded-lg">
              <h4 className="font-medium text-foreground">Auto-Transcribe</h4>
              <p className="text-sm text-muted-foreground">Automatically transcribe voice messages</p>
              <Badge className="mt-2">Enabled</Badge>
            </div>
            <div className="p-4 border border-border rounded-lg">
              <h4 className="font-medium text-foreground">Language Detection</h4>
              <p className="text-sm text-muted-foreground">Automatically detect spoken language</p>
              <Badge className="mt-2">Enabled</Badge>
            </div>
            <div className="p-4 border border-border rounded-lg">
              <h4 className="font-medium text-foreground">Save Transcripts</h4>
              <p className="text-sm text-muted-foreground">Store transcriptions with messages</p>
              <Badge className="mt-2">Enabled</Badge>
            </div>
            <div className="p-4 border border-border rounded-lg">
              <h4 className="font-medium text-foreground">Quality</h4>
              <p className="text-sm text-muted-foreground">Transcription accuracy level</p>
              <Badge variant="secondary" className="mt-2">High</Badge>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
