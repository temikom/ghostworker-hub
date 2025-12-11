import { useEffect, useState, useRef } from 'react';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { X, ChevronLeft, ChevronRight } from 'lucide-react';
import { useOnboarding, OnboardingStep } from '@/hooks/useOnboarding';
import { cn } from '@/lib/utils';

export function OnboardingTour() {
  const {
    isActive,
    currentStep,
    steps,
    currentStepData,
    nextStep,
    prevStep,
    completeOnboarding,
  } = useOnboarding();

  const [position, setPosition] = useState({ top: 0, left: 0 });
  const [targetRect, setTargetRect] = useState<DOMRect | null>(null);

  useEffect(() => {
    const handleRestartTour = () => {
      // This is handled by the useOnboarding hook
    };
    window.addEventListener('restart-tour', handleRestartTour);
    return () => window.removeEventListener('restart-tour', handleRestartTour);
  }, []);

  useEffect(() => {
    if (!isActive || !currentStepData) return;

    const updatePosition = () => {
      const target = document.querySelector(currentStepData.target);
      if (target) {
        const rect = target.getBoundingClientRect();
        setTargetRect(rect);

        const tooltipWidth = 320;
        const tooltipHeight = 180;
        const padding = 16;

        let top = 0;
        let left = 0;

        switch (currentStepData.position) {
          case 'top':
            top = rect.top - tooltipHeight - padding;
            left = rect.left + rect.width / 2 - tooltipWidth / 2;
            break;
          case 'bottom':
            top = rect.bottom + padding;
            left = rect.left + rect.width / 2 - tooltipWidth / 2;
            break;
          case 'left':
            top = rect.top + rect.height / 2 - tooltipHeight / 2;
            left = rect.left - tooltipWidth - padding;
            break;
          case 'right':
            top = rect.top + rect.height / 2 - tooltipHeight / 2;
            left = rect.right + padding;
            break;
        }

        // Keep within viewport
        top = Math.max(padding, Math.min(top, window.innerHeight - tooltipHeight - padding));
        left = Math.max(padding, Math.min(left, window.innerWidth - tooltipWidth - padding));

        setPosition({ top, left });
      }
    };

    updatePosition();
    window.addEventListener('resize', updatePosition);
    window.addEventListener('scroll', updatePosition);

    return () => {
      window.removeEventListener('resize', updatePosition);
      window.removeEventListener('scroll', updatePosition);
    };
  }, [isActive, currentStepData]);

  if (!isActive || !currentStepData) return null;

  return (
    <>
      {/* Overlay */}
      <div className="fixed inset-0 z-[100] bg-foreground/50">
        {/* Spotlight cutout */}
        {targetRect && (
          <div
            className="absolute bg-transparent rounded-lg shadow-[0_0_0_9999px_rgba(0,0,0,0.5)]"
            style={{
              top: targetRect.top - 4,
              left: targetRect.left - 4,
              width: targetRect.width + 8,
              height: targetRect.height + 8,
            }}
          />
        )}
      </div>

      {/* Tooltip */}
      <Card
        className="fixed z-[101] w-80 p-4 shadow-lg"
        style={{ top: position.top, left: position.left }}
      >
        <button
          onClick={completeOnboarding}
          className="absolute top-2 right-2 text-muted-foreground hover:text-foreground"
        >
          <X className="h-4 w-4" />
        </button>

        <div className="pr-6">
          <h3 className="font-semibold text-foreground">{currentStepData.title}</h3>
          <p className="text-sm text-muted-foreground mt-2">{currentStepData.description}</p>
        </div>

        <div className="flex items-center justify-between mt-4">
          <div className="flex gap-1">
            {steps.map((_, index) => (
              <div
                key={index}
                className={cn(
                  'w-2 h-2 rounded-full transition-colors',
                  index === currentStep ? 'bg-secondary' : 'bg-muted'
                )}
              />
            ))}
          </div>

          <div className="flex gap-2">
            {currentStep > 0 && (
              <Button variant="outline" size="sm" onClick={prevStep}>
                <ChevronLeft className="h-4 w-4 mr-1" />
                Back
              </Button>
            )}
            <Button size="sm" onClick={nextStep}>
              {currentStep === steps.length - 1 ? (
                'Finish'
              ) : (
                <>
                  Next
                  <ChevronRight className="h-4 w-4 ml-1" />
                </>
              )}
            </Button>
          </div>
        </div>
      </Card>
    </>
  );
}
