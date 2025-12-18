import { useState, useEffect } from 'react';
import { useNavigate, useSearchParams, useLocation } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Ghost, Mail, CheckCircle, XCircle, Loader2, RefreshCw } from 'lucide-react';
import { toast } from 'sonner';
import { useAuth } from '@/contexts/AuthContext';

type VerificationStatus = 'pending' | 'verifying' | 'success' | 'error' | 'expired';

export default function VerifyEmail() {
  const [status, setStatus] = useState<VerificationStatus>('pending');
  const [isResending, setIsResending] = useState(false);
  const [countdown, setCountdown] = useState(0);
  const [searchParams] = useSearchParams();
  const location = useLocation();
  const navigate = useNavigate();
  const { verifyEmail, resendVerification } = useAuth();

  const token = searchParams.get('token');
  const email = location.state?.email || searchParams.get('email') || '';

  useEffect(() => {
    if (token) {
      // Auto-verify if token is in URL
      handleVerifyToken(token);
    }
  }, [token]);

  useEffect(() => {
    // Countdown timer for resend
    if (countdown > 0) {
      const timer = setTimeout(() => setCountdown(countdown - 1), 1000);
      return () => clearTimeout(timer);
    }
  }, [countdown]);

  const handleVerifyToken = async (verificationToken: string) => {
    setStatus('verifying');
    try {
      await verifyEmail(verificationToken);
      setStatus('success');
      // Redirect to dashboard after short delay
      setTimeout(() => navigate('/dashboard'), 3000);
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Verification failed';
      if (message.includes('expired')) {
        setStatus('expired');
      } else {
        setStatus('error');
      }
      toast.error(message);
    }
  };

  const handleResendVerification = async () => {
    if (!email || countdown > 0) return;
    
    setIsResending(true);
    try {
      await resendVerification(email);
      toast.success('Verification email sent! Please check your inbox.');
      setCountdown(60); // 60 second cooldown
    } catch (error) {
      toast.error(error instanceof Error ? error.message : 'Failed to resend email');
    } finally {
      setIsResending(false);
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-muted p-4">
      <div className="w-full max-w-md">
        <div className="rounded-xl border border-border bg-card p-8 shadow-sm text-center">
          <Ghost className="h-12 w-12 text-primary mb-6 mx-auto" />

          {/* Pending - Waiting for user to check email */}
          {status === 'pending' && (
            <>
              <div className="w-16 h-16 rounded-full bg-primary/10 flex items-center justify-center mx-auto mb-6">
                <Mail className="h-8 w-8 text-primary" />
              </div>
              <h1 className="text-2xl font-bold text-foreground mb-2">Verify your email</h1>
              <p className="text-muted-foreground text-sm mb-6">
                We sent a verification link to{' '}
                <span className="font-medium text-foreground">{email}</span>
              </p>
              <p className="text-muted-foreground text-sm mb-6">
                Click the link in the email to verify your account and access the dashboard.
              </p>

              <div className="space-y-3">
                <Button
                  variant="outline"
                  className="w-full"
                  onClick={handleResendVerification}
                  disabled={isResending || countdown > 0}
                >
                  {isResending ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      Sending...
                    </>
                  ) : countdown > 0 ? (
                    <>
                      <RefreshCw className="mr-2 h-4 w-4" />
                      Resend in {countdown}s
                    </>
                  ) : (
                    <>
                      <RefreshCw className="mr-2 h-4 w-4" />
                      Resend verification email
                    </>
                  )}
                </Button>

                <Button
                  variant="ghost"
                  className="w-full"
                  onClick={() => navigate('/login')}
                >
                  Back to sign in
                </Button>
              </div>

              <p className="text-xs text-muted-foreground mt-6">
                Didn't receive the email? Check your spam folder or make sure the email address is correct.
              </p>
            </>
          )}

          {/* Verifying */}
          {status === 'verifying' && (
            <>
              <Loader2 className="h-16 w-16 text-primary animate-spin mx-auto mb-6" />
              <h1 className="text-2xl font-bold text-foreground mb-2">Verifying your email...</h1>
              <p className="text-muted-foreground text-sm">
                Please wait while we verify your email address.
              </p>
            </>
          )}

          {/* Success */}
          {status === 'success' && (
            <>
              <div className="w-16 h-16 rounded-full bg-green-100 dark:bg-green-900/20 flex items-center justify-center mx-auto mb-6">
                <CheckCircle className="h-8 w-8 text-green-500" />
              </div>
              <h1 className="text-2xl font-bold text-foreground mb-2">Email verified!</h1>
              <p className="text-muted-foreground text-sm mb-6">
                Your email has been verified successfully. You'll be redirected to the dashboard shortly.
              </p>
              <Button className="w-full" onClick={() => navigate('/dashboard')}>
                Go to Dashboard
              </Button>
            </>
          )}

          {/* Error */}
          {status === 'error' && (
            <>
              <div className="w-16 h-16 rounded-full bg-destructive/10 flex items-center justify-center mx-auto mb-6">
                <XCircle className="h-8 w-8 text-destructive" />
              </div>
              <h1 className="text-2xl font-bold text-foreground mb-2">Verification failed</h1>
              <p className="text-muted-foreground text-sm mb-6">
                We couldn't verify your email. The link may be invalid or corrupted.
              </p>
              <div className="space-y-3">
                <Button
                  className="w-full"
                  onClick={handleResendVerification}
                  disabled={isResending || !email}
                >
                  {isResending ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      Sending...
                    </>
                  ) : (
                    'Request new verification link'
                  )}
                </Button>
                <Button variant="ghost" className="w-full" onClick={() => navigate('/login')}>
                  Back to sign in
                </Button>
              </div>
            </>
          )}

          {/* Expired */}
          {status === 'expired' && (
            <>
              <div className="w-16 h-16 rounded-full bg-amber-100 dark:bg-amber-900/20 flex items-center justify-center mx-auto mb-6">
                <XCircle className="h-8 w-8 text-amber-500" />
              </div>
              <h1 className="text-2xl font-bold text-foreground mb-2">Link expired</h1>
              <p className="text-muted-foreground text-sm mb-6">
                This verification link has expired. Please request a new one.
              </p>
              <div className="space-y-3">
                <Button
                  className="w-full"
                  onClick={handleResendVerification}
                  disabled={isResending || countdown > 0 || !email}
                >
                  {isResending ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      Sending...
                    </>
                  ) : countdown > 0 ? (
                    `Resend in ${countdown}s`
                  ) : (
                    'Send new verification link'
                  )}
                </Button>
                <Button variant="ghost" className="w-full" onClick={() => navigate('/login')}>
                  Back to sign in
                </Button>
              </div>
            </>
          )}
        </div>

        <p className="text-center text-xs text-muted-foreground mt-4">
          Protected by GhostWorker Security
        </p>
      </div>
    </div>
  );
}
