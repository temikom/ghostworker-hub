import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  CommandDialog,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
  CommandSeparator,
} from '@/components/ui/command';
import {
  LayoutDashboard,
  Inbox,
  ShoppingBag,
  Plug,
  Bot,
  Settings,
  Users,
  BarChart3,
  Search,
  Moon,
  Sun,
  MessageSquare,
  Bell,
  HelpCircle,
} from 'lucide-react';
import { useTheme } from '@/hooks/useTheme';

interface CommandPaletteProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export function CommandPalette({ open, onOpenChange }: CommandPaletteProps) {
  const navigate = useNavigate();
  const { theme, toggleTheme } = useTheme();
  const [search, setSearch] = useState('');

  useEffect(() => {
    if (!open) setSearch('');
  }, [open]);

  const runCommand = (command: () => void) => {
    onOpenChange(false);
    command();
  };

  const navigationCommands = [
    { icon: LayoutDashboard, label: 'Go to Dashboard', action: () => navigate('/dashboard') },
    { icon: Inbox, label: 'Go to Inbox', action: () => navigate('/inbox') },
    { icon: ShoppingBag, label: 'Go to Orders', action: () => navigate('/orders') },
    { icon: Plug, label: 'Go to Integrations', action: () => navigate('/integrations') },
    { icon: Bot, label: 'Go to Assistant', action: () => navigate('/assistant') },
    { icon: Users, label: 'Go to Customers', action: () => navigate('/customers') },
    { icon: BarChart3, label: 'Go to Analytics', action: () => navigate('/analytics') },
    { icon: Settings, label: 'Go to Settings', action: () => navigate('/settings') },
  ];

  const actionCommands = [
    { icon: MessageSquare, label: 'New Message', action: () => navigate('/inbox') },
    { icon: Search, label: 'Search Everything', action: () => navigate('/search') },
    { icon: Bell, label: 'View Notifications', action: () => navigate('/notifications') },
    { icon: theme === 'dark' ? Sun : Moon, label: `Switch to ${theme === 'dark' ? 'Light' : 'Dark'} Mode`, action: toggleTheme },
    { icon: HelpCircle, label: 'Start Tour', action: () => window.dispatchEvent(new CustomEvent('restart-tour')) },
  ];

  return (
    <CommandDialog open={open} onOpenChange={onOpenChange}>
      <CommandInput
        placeholder="Type a command or search..."
        value={search}
        onValueChange={setSearch}
      />
      <CommandList>
        <CommandEmpty>No results found.</CommandEmpty>
        <CommandGroup heading="Navigation">
          {navigationCommands.map((cmd) => (
            <CommandItem
              key={cmd.label}
              onSelect={() => runCommand(cmd.action)}
              className="cursor-pointer"
            >
              <cmd.icon className="mr-2 h-4 w-4" />
              <span>{cmd.label}</span>
            </CommandItem>
          ))}
        </CommandGroup>
        <CommandSeparator />
        <CommandGroup heading="Actions">
          {actionCommands.map((cmd) => (
            <CommandItem
              key={cmd.label}
              onSelect={() => runCommand(cmd.action)}
              className="cursor-pointer"
            >
              <cmd.icon className="mr-2 h-4 w-4" />
              <span>{cmd.label}</span>
            </CommandItem>
          ))}
        </CommandGroup>
      </CommandList>
    </CommandDialog>
  );
}
