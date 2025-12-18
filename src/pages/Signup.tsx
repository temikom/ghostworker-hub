import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Checkbox } from '@/components/ui/checkbox';
import { Ghost, ArrowLeft, Shield, Check, X, Eye, EyeOff, Loader2 } from 'lucide-react';
import { toast } from 'sonner';
import { z } from 'zod';

const emailSchema = z.string().email('Please enter a valid email address');
const nameSchema = z.string().min(2, 'Name must be at least 2 characters').max(100, 'Name is too long');
const passwordSchema = z.string()
  .min(8, 'Password must be at least 8 characters')
  .regex(/[A-Z]/, 'Must contain uppercase letter')
  .regex(/[a-z]/, 'Must contain lowercase letter')
  .regex(/[0-9]/, 'Must contain a number')
  .regex(/[^A-Za-z0-9]/, 'Must contain special character');

type SignupStep = 'email' | 'name' | 'password' | 'verification-sent';

interface PasswordRequirement {
  label: string;
  test: (password: string) => boolean;
}

const passwordRequirements: PasswordRequirement[] = [
  { label: 'At least 8 characters', test: (p) => p.length >= 8 },
  { label: 'One uppercase letter', test: (p) => /[A-Z]/.test(p) },
  { label: 'One lowercase letter', test: (p) => /[a-z]/.test(p) },
  { label: 'One number', test: (p) => /[0-9]/.test(p) },
  { label: 'One special character', test: (p) => /[^A-Za-z0-9]/.test(p) },
];

export default function Signup() {
  const [step, setStep] = useState<SignupStep>('email');
  const [email, setEmail] = useState('');
  const [name, setName] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [agreedToTerms, setAgreedToTerms] = useState(false);
  const [errors, setErrors] = useState<{ email?: string; name?: string; password?: string; confirm?: string }>({});
  const [isLoading, setIsLoading] = useState(false);
  const { register, socialLogin, checkEmail } = useAuth();
  const navigate = useNavigate();

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
      const response = await checkEmail(email);
      if (response.exists) {
        toast.error('An account with this email already exists. Please sign in instead.');
        return;
      }
      setStep('name');
    } catch {
      // Proceed anyway for security
      setStep('name');
    } finally {
      setIsLoading(false);
    }
  };

  const handleNameSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrors({});

    const result = nameSchema.safeParse(name);
    if (!result.success) {
      setErrors({ name: result.error.errors[0].message });
      return;
    }

    setStep('password');
  };

  const handlePasswordSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrors({});

    const passwordResult = passwordSchema.safeParse(password);
    if (!passwordResult.success) {
      setErrors({ password: passwordResult.error.errors[0].message });
      return;
    }

    if (password !== confirmPassword) {
      setErrors({ confirm: 'Passwords do not match' });
      return;
    }

    if (!agreedToTerms) {
      toast.error('Please agree to the Terms of Service and Privacy Policy');
      return;
    }

    setIsLoading(true);
    try {
      await register(email, password, name);
      setStep('verification-sent');
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Registration failed';
      if (message.toLowerCase().includes('already')) {
        toast.error('An account with this email already exists. Please sign in instead.');
      } else {
        toast.error(message);
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handleSocialLogin = async (provider: 'google' | 'microsoft' | 'facebook') => {
    setIsLoading(true);
    try {
      await socialLogin(provider);
    } catch (error) {
      toast.error(error instanceof Error ? error.message : `${provider} signup failed`);
    } finally {
      setIsLoading(false);
    }
  };

  const goBack = () => {
    if (step === 'name') {
      setStep('email');
    } else if (step === 'password') {
      setStep('name');
    }
  };

  const allPasswordRequirementsMet = passwordRequirements.every((req) => req.test(password));

  return (
    <div className="flex min-h-screen items-center justify-center bg-muted p-4">
      <div className="w-full max-w-md">
        <div className="rounded-xl border border-border bg-card p-8 shadow-sm">
          {/* Header */}
          <div className="mb-8 flex flex-col items-center relative">
            {(step === 'name' || step === 'password') && (
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
              {step === 'email' && 'Create account'}
              {step === 'name' && 'What\'s your name?'}
              {step === 'password' && 'Create password'}
              {step === 'verification-sent' && 'Verify your email'}
            </h1>
            <p className="text-muted-foreground text-sm mt-1 text-center">
              {step === 'email' && 'Get started with GhostWorker'}
              {step === 'name' && email}
              {step === 'password' && 'Choose a strong password'}
              {step === 'verification-sent' && `We sent a verification link to ${email}`}
            </p>
          </div>

          {/* Verification Sent Step */}
          {step === 'verification-sent' && (
            <div className="space-y-6 text-center">
              <div className="w-16 h-16 rounded-full bg-primary/10 flex items-center justify-center mx-auto">
                <Shield className="h-8 w-8 text-primary" />
              </div>
              
              <div className="space-y-2">
                <p className="text-sm text-muted-foreground">
                  Please check your email and click the verification link to activate your account.
                </p>
                <p className="text-xs text-muted-foreground">
                  Didn't receive the email? Check your spam folder or{' '}
                  <button type="button" className="text-secondary hover:underline">
                    resend verification
                  </button>
                </p>
              </div>

              <Button
                variant="outline"
                className="w-full"
                onClick={() => navigate('/login')}
              >
                Return to sign in
              </Button>
            </div>
          )}

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

          {/* Name Step */}
          {step === 'name' && (
            <form onSubmit={handleNameSubmit} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="name">Full name</Label>
                <Input
                  id="name"
                  type="text"
                  placeholder="John Doe"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  className={errors.name ? 'border-destructive' : ''}
                  autoComplete="name"
                  autoFocus
                  required
                />
                {errors.name && <p className="text-xs text-destructive">{errors.name}</p>}
              </div>

              <Button type="submit" className="w-full h-11">
                Continue
              </Button>
            </form>
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
                    placeholder="Create a strong password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className={`pr-10 ${errors.password ? 'border-destructive' : ''}`}
                    autoComplete="new-password"
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
                
                {/* Password strength indicators */}
                <div className="space-y-1.5 mt-3">
                  {passwordRequirements.map((req, index) => (
                    <div key={index} className="flex items-center gap-2 text-xs">
                      {req.test(password) ? (
                        <Check className="h-3.5 w-3.5 text-green-500" />
                      ) : (
                        <X className="h-3.5 w-3.5 text-muted-foreground" />
                      )}
                      <span className={req.test(password) ? 'text-green-500' : 'text-muted-foreground'}>
                        {req.label}
                      </span>
                    </div>
                  ))}
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="confirm-password">Confirm password</Label>
                <Input
                  id="confirm-password"
                  type={showPassword ? 'text' : 'password'}
                  placeholder="Confirm your password"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  className={errors.confirm ? 'border-destructive' : ''}
                  autoComplete="new-password"
                  required
                />
                {errors.confirm && <p className="text-xs text-destructive">{errors.confirm}</p>}
                {confirmPassword && password === confirmPassword && (
                  <p className="text-xs text-green-500 flex items-center gap-1">
                    <Check className="h-3 w-3" /> Passwords match
                  </p>
                )}
              </div>

              <div className="flex items-start space-x-2">
                <Checkbox
                  id="terms"
                  checked={agreedToTerms}
                  onCheckedChange={(checked) => setAgreedToTerms(checked as boolean)}
                />
                <label
                  htmlFor="terms"
                  className="text-xs text-muted-foreground leading-tight cursor-pointer"
                >
                  I agree to the{' '}
                  <Link to="/terms" className="text-secondary hover:underline">Terms of Service</Link>
                  {' '}and{' '}
                  <Link to="/privacy" className="text-secondary hover:underline">Privacy Policy</Link>
                </label>
              </div>

              <Button 
                type="submit" 
                className="w-full h-11" 
                disabled={isLoading || !allPasswordRequirementsMet || !agreedToTerms}
              >
                {isLoading ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Creating account...
                  </>
                ) : (
                  'Create account'
                )}
              </Button>

              {/* Security notice */}
              <div className="flex items-center gap-2 text-xs text-muted-foreground mt-4 p-3 bg-muted rounded-lg">
                <Shield className="h-4 w-4 flex-shrink-0" />
                <span>Your password is encrypted and never stored in plain text</span>
              </div>
            </form>
          )}

          {step === 'email' && (
            <p className="mt-6 text-center text-sm text-muted-foreground">
              Already have an account?{' '}
              <Link to="/login" className="text-secondary hover:underline font-medium">
                Sign in
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
