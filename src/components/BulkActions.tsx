import { Button } from '@/components/ui/button';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { Check, ChevronDown, Tag, Archive, Trash2, MailOpen, MailX } from 'lucide-react';
import { cn } from '@/lib/utils';

interface BulkActionsProps<T> {
  items: T[];
  selectedIds: string[];
  onSelectAll: () => void;
  onDeselectAll: () => void;
  onMarkAsRead?: () => void;
  onMarkAsUnread?: () => void;
  onArchive?: () => void;
  onDelete?: () => void;
  onAddTag?: () => void;
  getItemId: (item: T) => string;
}

export function BulkActions<T>({
  items,
  selectedIds,
  onSelectAll,
  onDeselectAll,
  onMarkAsRead,
  onMarkAsUnread,
  onArchive,
  onDelete,
  onAddTag,
  getItemId,
}: BulkActionsProps<T>) {
  const allSelected = items.length > 0 && selectedIds.length === items.length;
  const someSelected = selectedIds.length > 0 && selectedIds.length < items.length;

  if (selectedIds.length === 0) {
    return null;
  }

  return (
    <div className="flex items-center gap-2 px-4 py-2 bg-accent/50 border-b border-border">
      <button
        onClick={allSelected ? onDeselectAll : onSelectAll}
        className="flex items-center justify-center w-5 h-5 rounded border border-border bg-background"
      >
        {allSelected && <Check className="h-3 w-3 text-secondary" />}
        {someSelected && <div className="w-2 h-0.5 bg-secondary" />}
      </button>

      <span className="text-sm text-foreground font-medium">
        {selectedIds.length} selected
      </span>

      <div className="flex items-center gap-1 ml-auto">
        {onMarkAsRead && (
          <Button variant="ghost" size="sm" onClick={onMarkAsRead} className="h-8">
            <MailOpen className="h-4 w-4 mr-1" />
            Mark Read
          </Button>
        )}

        {onMarkAsUnread && (
          <Button variant="ghost" size="sm" onClick={onMarkAsUnread} className="h-8">
            <MailX className="h-4 w-4 mr-1" />
            Mark Unread
          </Button>
        )}

        {onAddTag && (
          <Button variant="ghost" size="sm" onClick={onAddTag} className="h-8">
            <Tag className="h-4 w-4 mr-1" />
            Add Tag
          </Button>
        )}

        {onArchive && (
          <Button variant="ghost" size="sm" onClick={onArchive} className="h-8">
            <Archive className="h-4 w-4 mr-1" />
            Archive
          </Button>
        )}

        {onDelete && (
          <Button variant="ghost" size="sm" onClick={onDelete} className="h-8 text-destructive">
            <Trash2 className="h-4 w-4 mr-1" />
            Delete
          </Button>
        )}

        <Button variant="ghost" size="sm" onClick={onDeselectAll} className="h-8">
          Cancel
        </Button>
      </div>
    </div>
  );
}

interface SelectCheckboxProps {
  checked: boolean;
  onChange: (checked: boolean) => void;
}

export function SelectCheckbox({ checked, onChange }: SelectCheckboxProps) {
  return (
    <button
      onClick={(e) => {
        e.stopPropagation();
        onChange(!checked);
      }}
      className={cn(
        'flex items-center justify-center w-4 h-4 rounded border transition-colors',
        checked
          ? 'bg-secondary border-secondary'
          : 'border-border bg-background hover:border-secondary'
      )}
    >
      {checked && <Check className="h-3 w-3 text-secondary-foreground" />}
    </button>
  );
}
