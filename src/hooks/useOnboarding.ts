import { useState, useEffect } from 'react';

export interface OnboardingStep {
  id: string;
  title: string;
  description: string;
  target: string;
  position: 'top' | 'bottom' | 'left' | 'right';
}

const ONBOARDING_STEPS: OnboardingStep[] = [
  {
    id: 'dashboard',
    title: 'Welcome to GhostWorker',
    description: 'Your central hub for managing all customer communications across platforms.',
    target: '[data-tour="dashboard"]',
    position: 'bottom',
  },
  {
    id: 'inbox',
    title: 'Unified Inbox',
    description: 'All your messages from WhatsApp, Instagram, TikTok, and Email in one place.',
    target: '[data-tour="inbox"]',
    position: 'right',
  },
  {
    id: 'orders',
    title: 'Order Management',
    description: 'Track and manage all customer orders efficiently.',
    target: '[data-tour="orders"]',
    position: 'right',
  },
  {
    id: 'integrations',
    title: 'Connect Platforms',
    description: 'Link your messaging platforms to start receiving messages.',
    target: '[data-tour="integrations"]',
    position: 'right',
  },
  {
    id: 'command',
    title: 'Quick Actions',
    description: 'Press Cmd+K (or Ctrl+K) anytime to access quick commands.',
    target: '[data-tour="search"]',
    position: 'bottom',
  },
];

export function useOnboarding() {
  const [isActive, setIsActive] = useState(false);
  const [currentStep, setCurrentStep] = useState(0);
  const [hasCompleted, setHasCompleted] = useState(() => {
    return localStorage.getItem('ghostworker-onboarding-complete') === 'true';
  });

  useEffect(() => {
    if (!hasCompleted) {
      const timer = setTimeout(() => setIsActive(true), 1000);
      return () => clearTimeout(timer);
    }
  }, [hasCompleted]);

  const nextStep = () => {
    if (currentStep < ONBOARDING_STEPS.length - 1) {
      setCurrentStep((s) => s + 1);
    } else {
      completeOnboarding();
    }
  };

  const prevStep = () => {
    if (currentStep > 0) {
      setCurrentStep((s) => s - 1);
    }
  };

  const completeOnboarding = () => {
    setIsActive(false);
    setHasCompleted(true);
    localStorage.setItem('ghostworker-onboarding-complete', 'true');
  };

  const restartOnboarding = () => {
    setCurrentStep(0);
    setIsActive(true);
    setHasCompleted(false);
    localStorage.removeItem('ghostworker-onboarding-complete');
  };

  return {
    isActive,
    currentStep,
    steps: ONBOARDING_STEPS,
    currentStepData: ONBOARDING_STEPS[currentStep],
    nextStep,
    prevStep,
    completeOnboarding,
    restartOnboarding,
    hasCompleted,
  };
}
