import { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Ghost, ArrowLeft, Shield, AlertTriangle, Eye, EyeOff, Loader2 } from 'lucide-react';
import { toast } from 'sonner';
import { z } from 'zod';
import { Alert, AlertDescription } from '@/components/ui/alert';

const emailSchema = z.string().email('Please enter a valid email address');
const passwordSchema = z.string().min(8, 'Password must be at least 8 characters');

type AuthStep = 'email' | 'password' | '2fa';

export default function Login() {
  const [step, setStep] = useState<AuthStep>('email');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [twoFactorCode, setTwoFactorCode] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [errors, setErrors] = useState<{ email?: string; password?: string; code?: string }>({});
  const [isLoading, setIsLoading] = useState(false);
  const [tempToken, setTempToken] = useState<string | null>(null);
  const [securityAlert, setSecurityAlert] = useState<string | null>(null);
  const { login, socialLogin, verify2FA, checkEmail } = useAuth();
  const navigate = useNavigate();

  // Check for security alerts from URL params
  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const alert = params.get('security_alert');
    if (alert) {
      setSecurityAlert(decodeURIComponent(alert));
    }
  }, []);

  const handleEmailSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrors({});

    const result = emailSchema.safeParse(email);
    if (!result.success) {
      setErrors({ email: result.error.errors[0].message });
      return;
    }

    setIsLoading(true);
    try {
      // Check if email exists and get auth requirements
      const response = await checkEmail(email);
      if (response.exists) {
        setStep('password');
      } else {
        // Email not found - suggest signup
        toast.error('No account found with this email. Please sign up first.');
      }
    } catch {
      // For security, proceed to password step anyway
      setStep('password');
    } finally {
      setIsLoading(false);
    }
  };

  const handlePasswordSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrors({});

    const result = passwordSchema.safeParse(password);
    if (!result.success) {
      setErrors({ password: result.error.errors[0].message });
      return;
    }

    setIsLoading(true);
    try {
      const response = await login(email, password);
      
      // Check if 2FA is required
      if (response.requires2FA && response.tempToken) {
        setTempToken(response.tempToken);
        setStep('2fa');
      } else if (response.requiresVerification) {
        // Redirect to email verification
        navigate('/verify-email', { state: { email } });
      } else {
        // Successful login
        navigate('/dashboard');
      }
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Login failed';
      if (message.includes('locked')) {
        setSecurityAlert('Your account has been temporarily locked due to multiple failed attempts. Please try again later or reset your password.');
      } else {
        toast.error(message);
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handle2FASubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrors({});

    if (twoFactorCode.length !== 6) {
      setErrors({ code: 'Please enter a 6-digit code' });
      return;
    }

    setIsLoading(true);
    try {
      await verify2FA(tempToken!, twoFactorCode);
      navigate('/dashboard');
    } catch (error) {
      toast.error(error instanceof Error ? error.message : 'Invalid verification code');
    } finally {
      setIsLoading(false);
    }
  };

  const handleSocialLogin = async (provider: 'google' | 'microsoft' | 'facebook') => {
    setIsLoading(true);
    try {
      await socialLogin(provider);
    } catch (error) {
      toast.error(error instanceof Error ? error.message : `${provider} login failed`);
    } finally {
      setIsLoading(false);
    }
  };

  const goBack = () => {
    if (step === 'password') {
      setPassword('');
      setStep('email');
    } else if (step === '2fa') {
      setTwoFactorCode('');
      setStep('password');
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-muted p-4">
      <div className="w-full max-w-md">
        <div className="rounded-xl border border-border bg-card p-8 shadow-sm">
          {/* Security Alert Banner */}
          {securityAlert && (
            <Alert variant="destructive" className="mb-6">
              <AlertTriangle className="h-4 w-4" />
              <AlertDescription>{securityAlert}</AlertDescription>
            </Alert>
          )}

          {/* Header */}
          <div className="mb-8 flex flex-col items-center relative">
            {step !== 'email' && (
              <button
                onClick={goBack}
                className="absolute left-0 top-0 p-2 text-muted-foreground hover:text-foreground transition-colors"
                aria-label="Go back"
              >
                <ArrowLeft className="h-5 w-5" />
              </button>
            )}
            <Ghost className="h-12 w-12 text-primary mb-3" />
            <h1 className="text-2xl font-bold text-foreground">
              {step === 'email' && 'Sign in'}
              {step === 'password' && 'Welcome back'}
              {step === '2fa' && 'Two-factor authentication'}
            </h1>
            <p className="text-muted-foreground text-sm mt-1 text-center">
              {step === 'email' && 'Enter your email to continue'}
              {step === 'password' && email}
              {step === '2fa' && 'Enter the code from your authenticator app'}
            </p>
          </div>

          {/* Email Step */}
          {step === 'email' && (
            <>
              {/* Social Login Buttons */}
              <div className="space-y-3 mb-6">
                <Button
                  type="button"
                  variant="outline"
                  className="w-full flex items-center justify-center gap-3 h-11"
                  onClick={() => handleSocialLogin('google')}
                  disabled={isLoading}
                >
                  <svg viewBox="0 0 24 24" className="w-5 h-5" fill="currentColor">
                    <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4"/>
                    <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"/>
                    <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" fill="#FBBC05"/>
                    <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335"/>
                  </svg>
                  Continue with Google
                </Button>

                <Button
                  type="button"
                  variant="outline"
                  className="w-full flex items-center justify-center gap-3 h-11"
                  onClick={() => handleSocialLogin('microsoft')}
                  disabled={isLoading}
                >
                  <svg viewBox="0 0 24 24" className="w-5 h-5">
                    <path fill="#F25022" d="M1 1h10v10H1z"/>
                    <path fill="#00A4EF" d="M1 13h10v10H1z"/>
                    <path fill="#7FBA00" d="M13 1h10v10H13z"/>
                    <path fill="#FFB900" d="M13 13h10v10H13z"/>
                  </svg>
                  Continue with Microsoft
                </Button>

                <Button
                  type="button"
                  variant="outline"
                  className="w-full flex items-center justify-center gap-3 h-11"
                  onClick={() => handleSocialLogin('facebook')}
                  disabled={isLoading}
                >
                  <svg viewBox="0 0 24 24" className="w-5 h-5 text-[#1877F2]" fill="currentColor">
                    <path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/>
                  </svg>
                  Continue with Facebook
                </Button>
              </div>

              <div className="relative mb-6">
                <div className="absolute inset-0 flex items-center">
                  <div className="w-full border-t border-border"></div>
                </div>
                <div className="relative flex justify-center text-xs uppercase">
                  <span className="bg-card px-2 text-muted-foreground">Or continue with email</span>
                </div>
              </div>

              <form onSubmit={handleEmailSubmit} className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="email">Email address</Label>
                  <Input
                    id="email"
                    type="email"
                    placeholder="you@example.com"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className={errors.email ? 'border-destructive' : ''}
                    autoComplete="email"
                    autoFocus
                    required
                  />
                  {errors.email && <p className="text-xs text-destructive">{errors.email}</p>}
                </div>

                <Button type="submit" className="w-full h-11" disabled={isLoading}>
                  {isLoading ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      Checking...
                    </>
                  ) : (
                    'Continue'
                  )}
                </Button>
              </form>
            </>
          )}

          {/* Password Step */}
          {step === 'password' && (
            <form onSubmit={handlePasswordSubmit} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="password">Password</Label>
                <div className="relative">
                  <Input
                    id="password"
                    type={showPassword ? 'text' : 'password'}
                    placeholder="Enter your password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className={`pr-10 ${errors.password ? 'border-destructive' : ''}`}
                    autoComplete="current-password"
                    autoFocus
                    required
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
                    tabIndex={-1}
                  >
                    {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                  </button>
                </div>
                {errors.password && <p className="text-xs text-destructive">{errors.password}</p>}
              </div>

              <div className="flex justify-end">
                <Link to="/forgot-password" className="text-sm text-secondary hover:underline">
                  Forgot password?
                </Link>
              </div>

              <Button type="submit" className="w-full h-11" disabled={isLoading}>
                {isLoading ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Signing in...
                  </>
                ) : (
                  'Sign in'
                )}
              </Button>

              {/* Security notice */}
              <div className="flex items-center gap-2 text-xs text-muted-foreground mt-4 p-3 bg-muted rounded-lg">
                <Shield className="h-4 w-4 flex-shrink-0" />
                <span>Your connection is encrypted and secure</span>
              </div>
            </form>
          )}

          {/* 2FA Step */}
          {step === '2fa' && (
            <form onSubmit={handle2FASubmit} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="2fa-code">Verification code</Label>
                <Input
                  id="2fa-code"
                  type="text"
                  inputMode="numeric"
                  pattern="[0-9]*"
                  maxLength={6}
                  placeholder="000000"
                  value={twoFactorCode}
                  onChange={(e) => setTwoFactorCode(e.target.value.replace(/\D/g, ''))}
                  className={`text-center text-2xl tracking-widest ${errors.code ? 'border-destructive' : ''}`}
                  autoFocus
                  required
                />
                {errors.code && <p className="text-xs text-destructive text-center">{errors.code}</p>}
              </div>

              <Button type="submit" className="w-full h-11" disabled={isLoading || twoFactorCode.length !== 6}>
                {isLoading ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Verifying...
                  </>
                ) : (
                  'Verify'
                )}
              </Button>

              <p className="text-xs text-center text-muted-foreground">
                Can't access your authenticator?{' '}
                <button type="button" className="text-secondary hover:underline">
                  Use backup code
                </button>
              </p>
            </form>
          )}

          {step === 'email' && (
            <p className="mt-6 text-center text-sm text-muted-foreground">
              Don't have an account?{' '}
              <Link to="/signup" className="text-secondary hover:underline font-medium">
                Sign up
              </Link>
            </p>
          )}
        </div>

        {/* Security footer */}
        <p className="text-center text-xs text-muted-foreground mt-4">
          Protected by GhostWorker Security
        </p>
      </div>
    </div>
  );
}
