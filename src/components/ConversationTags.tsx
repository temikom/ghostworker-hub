import { useState, useEffect } from 'react';
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from '@/components/ui/popover';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Tag, Plus, X, Check } from 'lucide-react';
import { cn } from '@/lib/utils';

export interface ConversationTag {
  id: string;
  name: string;
  color: string;
}

interface ConversationTagsProps {
  conversationId: string;
  selectedTags: ConversationTag[];
  onTagsChange: (tags: ConversationTag[]) => void;
  compact?: boolean;
}

const TAG_STORAGE_KEY = 'ghostworker-conversation-tags';

const DEFAULT_COLORS = [
  'hsl(0 84% 60%)',
  'hsl(25 95% 53%)',
  'hsl(48 96% 53%)',
  'hsl(142 76% 36%)',
  'hsl(205 100% 50%)',
  'hsl(262 83% 58%)',
  'hsl(340 75% 55%)',
];

export function ConversationTags({
  conversationId,
  selectedTags,
  onTagsChange,
  compact = false,
}: ConversationTagsProps) {
  const [allTags, setAllTags] = useState<ConversationTag[]>([]);
  const [isOpen, setIsOpen] = useState(false);
  const [newTagName, setNewTagName] = useState('');
  const [selectedColor, setSelectedColor] = useState(DEFAULT_COLORS[0]);

  useEffect(() => {
    const stored = localStorage.getItem(TAG_STORAGE_KEY);
    if (stored) {
      setAllTags(JSON.parse(stored));
    }
  }, []);

  const saveTags = (tags: ConversationTag[]) => {
    setAllTags(tags);
    localStorage.setItem(TAG_STORAGE_KEY, JSON.stringify(tags));
  };

  const createTag = () => {
    if (!newTagName.trim()) return;
    const newTag: ConversationTag = {
      id: Date.now().toString(),
      name: newTagName.trim(),
      color: selectedColor,
    };
    saveTags([...allTags, newTag]);
    onTagsChange([...selectedTags, newTag]);
    setNewTagName('');
    setSelectedColor(DEFAULT_COLORS[Math.floor(Math.random() * DEFAULT_COLORS.length)]);
  };

  const toggleTag = (tag: ConversationTag) => {
    const isSelected = selectedTags.some((t) => t.id === tag.id);
    if (isSelected) {
      onTagsChange(selectedTags.filter((t) => t.id !== tag.id));
    } else {
      onTagsChange([...selectedTags, tag]);
    }
  };

  const removeTag = (tagId: string) => {
    onTagsChange(selectedTags.filter((t) => t.id !== tagId));
  };

  return (
    <div className="flex items-center gap-1 flex-wrap">
      {selectedTags.map((tag) => (
        <Badge
          key={tag.id}
          variant="outline"
          className={cn('text-xs gap-1', compact && 'px-1.5 py-0')}
          style={{ borderColor: tag.color, color: tag.color }}
        >
          {tag.name}
          {!compact && (
            <button
              onClick={(e) => {
                e.stopPropagation();
                removeTag(tag.id);
              }}
              className="hover:opacity-70"
            >
              <X className="h-3 w-3" />
            </button>
          )}
        </Badge>
      ))}

      <Popover open={isOpen} onOpenChange={setIsOpen}>
        <PopoverTrigger asChild>
          <Button
            variant="ghost"
            size="icon"
            className={cn('h-6 w-6', compact && 'h-5 w-5')}
          >
            <Tag className={cn('h-3.5 w-3.5', compact && 'h-3 w-3')} />
          </Button>
        </PopoverTrigger>
        <PopoverContent className="w-64 p-3" align="start">
          <div className="space-y-3">
            <p className="text-sm font-medium text-foreground">Tags</p>

            {/* Existing tags */}
            <div className="space-y-1 max-h-32 overflow-y-auto">
              {allTags.length === 0 ? (
                <p className="text-xs text-muted-foreground text-center py-2">No tags created yet</p>
              ) : (
                allTags.map((tag) => {
                  const isSelected = selectedTags.some((t) => t.id === tag.id);
                  return (
                    <button
                      key={tag.id}
                      onClick={() => toggleTag(tag)}
                      className={cn(
                        'w-full flex items-center gap-2 px-2 py-1.5 rounded text-sm',
                        'hover:bg-muted transition-colors text-left',
                        isSelected && 'bg-muted'
                      )}
                    >
                      <span
                        className="w-3 h-3 rounded-full flex-shrink-0"
                        style={{ backgroundColor: tag.color }}
                      />
                      <span className="flex-1 truncate text-foreground">{tag.name}</span>
                      {isSelected && <Check className="h-3.5 w-3.5 text-secondary" />}
                    </button>
                  );
                })
              )}
            </div>

            {/* Create new tag */}
            <div className="border-t border-border pt-3">
              <p className="text-xs text-muted-foreground mb-2">Create new tag</p>
              <div className="flex gap-2">
                <Input
                  value={newTagName}
                  onChange={(e) => setNewTagName(e.target.value)}
                  placeholder="Tag name"
                  className="h-8 text-sm"
                  onKeyDown={(e) => e.key === 'Enter' && createTag()}
                />
                <Button size="sm" className="h-8 px-2" onClick={createTag}>
                  <Plus className="h-4 w-4" />
                </Button>
              </div>
              <div className="flex gap-1 mt-2">
                {DEFAULT_COLORS.map((color) => (
                  <button
                    key={color}
                    onClick={() => setSelectedColor(color)}
                    className={cn(
                      'w-5 h-5 rounded-full transition-transform',
                      selectedColor === color && 'ring-2 ring-offset-2 ring-offset-background ring-secondary scale-110'
                    )}
                    style={{ backgroundColor: color }}
                  />
                ))}
              </div>
            </div>
          </div>
        </PopoverContent>
      </Popover>
    </div>
  );
}
