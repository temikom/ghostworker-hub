import { useEffect, useCallback } from 'react';

interface ShortcutHandlers {
  onNextItem?: () => void;
  onPrevItem?: () => void;
  onReply?: () => void;
  onSearch?: () => void;
  onCommandPalette?: () => void;
  onEscape?: () => void;
}

export function useKeyboardShortcuts(handlers: ShortcutHandlers) {
  const handleKeyDown = useCallback(
    (event: KeyboardEvent) => {
      const target = event.target as HTMLElement;
      const isInput = target.tagName === 'INPUT' || target.tagName === 'TEXTAREA' || target.isContentEditable;

      // Cmd/Ctrl + K for command palette (works even in inputs)
      if ((event.metaKey || event.ctrlKey) && event.key === 'k') {
        event.preventDefault();
        handlers.onCommandPalette?.();
        return;
      }

      // Cmd/Ctrl + / for search
      if ((event.metaKey || event.ctrlKey) && event.key === '/') {
        event.preventDefault();
        handlers.onSearch?.();
        return;
      }

      // Skip other shortcuts when in input
      if (isInput) return;

      switch (event.key.toLowerCase()) {
        case 'j':
          event.preventDefault();
          handlers.onNextItem?.();
          break;
        case 'k':
          event.preventDefault();
          handlers.onPrevItem?.();
          break;
        case 'r':
          event.preventDefault();
          handlers.onReply?.();
          break;
        case 'escape':
          handlers.onEscape?.();
          break;
      }
    },
    [handlers]
  );

  useEffect(() => {
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [handleKeyDown]);
}
