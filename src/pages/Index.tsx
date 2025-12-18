import { Link } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Ghost, MessageSquare, ShoppingBag, Zap, ArrowRight, CheckCircle } from 'lucide-react';
import { PlatformIcon } from '@/components/icons/PlatformIcon';

const features = [
  {
    icon: MessageSquare,
    title: 'Unified Inbox',
    description: 'All your customer messages from WhatsApp, Instagram, TikTok, and Email in one place.',
  },
  {
    icon: ShoppingBag,
    title: 'Order Management',
    description: 'Track and manage all your orders with automated status updates.',
  },
  {
    icon: Zap,
    title: 'AI Automation',
    description: 'Let AI handle repetitive tasks and respond to common queries automatically.',
  },
];

const platforms = ['whatsapp', 'instagram', 'tiktok', 'email'] as const;

const steps = [
  { number: '01', title: 'Connect', description: 'Link your messaging platforms in minutes' },
  { number: '02', title: 'Automate', description: 'Set up AI-powered responses and workflows' },
  { number: '03', title: 'Grow', description: 'Scale your business without scaling your team' },
];

export default function Index() {
  return (
    <div className="min-h-screen bg-background">
      {/* Navigation */}
      <nav className="border-b border-border bg-card/50 backdrop-blur-sm sticky top-0 z-50">
        <div className="container mx-auto px-4 h-16 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Ghost className="h-8 w-8 text-primary" />
            <span className="text-xl font-bold text-primary">GhostWorker</span>
          </div>
          <div className="flex items-center gap-4">
            <Link to="/login">
              <Button variant="ghost">Log in</Button>
            </Link>
            <Link to="/signup">
              <Button>Get Started</Button>
            </Link>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="py-20 lg:py-32">
        <div className="container mx-auto px-4">
          <div className="max-w-3xl mx-auto text-center">
            <h1 className="text-4xl md:text-5xl lg:text-6xl font-bold text-foreground leading-tight">
              Automate Your Customer Messages
            </h1>
            <p className="mt-6 text-lg text-muted-foreground max-w-2xl mx-auto">
              Connect WhatsApp, Instagram, TikTok, and Email. Manage all conversations, orders, and tasks in one simple dashboard.
            </p>
            <div className="mt-8 flex flex-col sm:flex-row items-center justify-center gap-4">
              <Link to="/signup">
                <Button size="lg" className="w-full sm:w-auto">
                  Start Free Trial
                  <ArrowRight className="ml-2 h-4 w-4" />
                </Button>
              </Link>
              <Link to="/login">
                <Button size="lg" variant="outline" className="w-full sm:w-auto">
                  View Demo
                </Button>
              </Link>
            </div>
            <div className="mt-12 flex items-center justify-center gap-6">
              {platforms.map((platform) => (
                <PlatformIcon key={platform} platform={platform} className="h-8 w-8 opacity-60" />
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 bg-muted/50">
        <div className="container mx-auto px-4">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-foreground">Everything You Need</h2>
            <p className="mt-4 text-muted-foreground">
              Powerful tools to automate and grow your business
            </p>
          </div>
          <div className="grid gap-8 md:grid-cols-3 max-w-5xl mx-auto">
            {features.map((feature) => (
              <div
                key={feature.title}
                className="bg-card rounded-xl p-6 border border-border hover:border-secondary/50 transition-colors"
              >
                <feature.icon className="h-10 w-10 text-secondary mb-4" />
                <h3 className="text-xl font-semibold text-foreground">{feature.title}</h3>
                <p className="mt-2 text-muted-foreground">{feature.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* How It Works Section */}
      <section className="py-20">
        <div className="container mx-auto px-4">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-foreground">How It Works</h2>
            <p className="mt-4 text-muted-foreground">Get started in three simple steps</p>
          </div>
          <div className="grid gap-8 md:grid-cols-3 max-w-4xl mx-auto">
            {steps.map((step) => (
              <div key={step.number} className="text-center">
                <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-primary/10 text-primary text-2xl font-bold mb-4">
                  {step.number}
                </div>
                <h3 className="text-xl font-semibold text-foreground">{step.title}</h3>
                <p className="mt-2 text-muted-foreground">{step.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Pricing Section */}
      <section className="py-20 bg-muted/50">
        <div className="container mx-auto px-4">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-foreground">Simple Pricing</h2>
            <p className="mt-4 text-muted-foreground">Start free, upgrade when you need</p>
          </div>
          <div className="max-w-md mx-auto">
            <div className="bg-card rounded-xl p-8 border border-border">
              <div className="text-center">
                <h3 className="text-2xl font-bold text-foreground">Pro Plan</h3>
                <div className="mt-4">
                  <span className="text-4xl font-bold text-foreground">$29</span>
                  <span className="text-muted-foreground">/month</span>
                </div>
              </div>
              <ul className="mt-8 space-y-4">
                {[
                  'Unlimited messages',
                  'All platform integrations',
                  'AI automation',
                  'Order management',
                  'Priority support',
                ].map((item) => (
                  <li key={item} className="flex items-center gap-3">
                    <CheckCircle className="h-5 w-5 text-success" />
                    <span className="text-foreground">{item}</span>
                  </li>
                ))}
              </ul>
              <Link to="/signup" className="block mt-8">
                <Button className="w-full" size="lg">
                  Start Free Trial
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20">
        <div className="container mx-auto px-4">
          <div className="max-w-2xl mx-auto text-center">
            <h2 className="text-3xl font-bold text-foreground">
              Ready to Automate Your Business?
            </h2>
            <p className="mt-4 text-muted-foreground">
              Join thousands of businesses using GhostWorker to save time and grow faster.
            </p>
            <Link to="/signup" className="inline-block mt-8">
              <Button size="lg">
                Get Started Free
                <ArrowRight className="ml-2 h-4 w-4" />
              </Button>
            </Link>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-border py-8">
        <div className="container mx-auto px-4">
          <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
            <div className="flex items-center gap-2">
              <Ghost className="h-6 w-6 text-primary" />
              <span className="font-semibold text-foreground">GhostWorker</span>
              <span className="text-sm text-muted-foreground">by Temi Kom</span>
            </div>
            <p className="text-sm text-muted-foreground">
              © {new Date().getFullYear()} Temi Kom. All rights reserved.
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}
