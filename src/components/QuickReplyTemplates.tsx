import { useState, useEffect } from 'react';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';
import { Search, Plus, Pencil, Trash2, MessageSquare } from 'lucide-react';
import { cn } from '@/lib/utils';

export interface QuickReplyTemplate {
  id: string;
  name: string;
  content: string;
  category: string;
}

interface QuickReplyTemplatesProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSelect: (template: QuickReplyTemplate) => void;
}

const TEMPLATE_STORAGE_KEY = 'ghostworker-quick-replies';

export function QuickReplyTemplates({ open, onOpenChange, onSelect }: QuickReplyTemplatesProps) {
  const [templates, setTemplates] = useState<QuickReplyTemplate[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [isEditing, setIsEditing] = useState(false);
  const [editingTemplate, setEditingTemplate] = useState<QuickReplyTemplate | null>(null);
  const [formData, setFormData] = useState({ name: '', content: '', category: 'General' });

  useEffect(() => {
    const stored = localStorage.getItem(TEMPLATE_STORAGE_KEY);
    if (stored) {
      setTemplates(JSON.parse(stored));
    }
  }, []);

  const saveTemplates = (newTemplates: QuickReplyTemplate[]) => {
    setTemplates(newTemplates);
    localStorage.setItem(TEMPLATE_STORAGE_KEY, JSON.stringify(newTemplates));
  };

  const handleSave = () => {
    if (!formData.name.trim() || !formData.content.trim()) return;

    if (editingTemplate) {
      const updated = templates.map((t) =>
        t.id === editingTemplate.id ? { ...t, ...formData } : t
      );
      saveTemplates(updated);
    } else {
      const newTemplate: QuickReplyTemplate = {
        id: Date.now().toString(),
        ...formData,
      };
      saveTemplates([...templates, newTemplate]);
    }

    setFormData({ name: '', content: '', category: 'General' });
    setEditingTemplate(null);
    setIsEditing(false);
  };

  const handleEdit = (template: QuickReplyTemplate) => {
    setEditingTemplate(template);
    setFormData({ name: template.name, content: template.content, category: template.category });
    setIsEditing(true);
  };

  const handleDelete = (id: string) => {
    saveTemplates(templates.filter((t) => t.id !== id));
  };

  const filteredTemplates = templates.filter(
    (t) =>
      t.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      t.content.toLowerCase().includes(searchQuery.toLowerCase()) ||
      t.category.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const categories = Array.from(new Set(templates.map((t) => t.category)));

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-lg">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <MessageSquare className="h-5 w-5" />
            Quick Reply Templates
          </DialogTitle>
        </DialogHeader>

        {isEditing ? (
          <div className="space-y-4">
            <div>
              <Label htmlFor="template-name">Name</Label>
              <Input
                id="template-name"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                placeholder="e.g., Greeting"
              />
            </div>
            <div>
              <Label htmlFor="template-category">Category</Label>
              <Input
                id="template-category"
                value={formData.category}
                onChange={(e) => setFormData({ ...formData, category: e.target.value })}
                placeholder="e.g., Support"
              />
            </div>
            <div>
              <Label htmlFor="template-content">Message</Label>
              <Textarea
                id="template-content"
                value={formData.content}
                onChange={(e) => setFormData({ ...formData, content: e.target.value })}
                placeholder="Type your template message..."
                rows={4}
              />
            </div>
            <div className="flex gap-2 justify-end">
              <Button
                variant="outline"
                onClick={() => {
                  setIsEditing(false);
                  setEditingTemplate(null);
                  setFormData({ name: '', content: '', category: 'General' });
                }}
              >
                Cancel
              </Button>
              <Button onClick={handleSave}>
                {editingTemplate ? 'Update' : 'Save'}
              </Button>
            </div>
          </div>
        ) : (
          <>
            <div className="flex gap-2">
              <div className="relative flex-1">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                <Input
                  placeholder="Search templates..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-9"
                />
              </div>
              <Button onClick={() => setIsEditing(true)}>
                <Plus className="h-4 w-4 mr-1" />
                New
              </Button>
            </div>

            <div className="max-h-80 overflow-y-auto space-y-2">
              {filteredTemplates.length === 0 ? (
                <div className="py-8 text-center text-muted-foreground">
                  <MessageSquare className="h-8 w-8 mx-auto mb-2 opacity-50" />
                  <p className="text-sm">No templates yet</p>
                  <p className="text-xs mt-1">Create your first quick reply template</p>
                </div>
              ) : (
                categories.map((category) => (
                  <div key={category}>
                    <p className="text-xs font-medium text-muted-foreground uppercase tracking-wide mb-2 px-1">
                      {category}
                    </p>
                    {filteredTemplates
                      .filter((t) => t.category === category)
                      .map((template) => (
                        <div
                          key={template.id}
                          className={cn(
                            'group flex items-start gap-3 p-3 rounded-lg border border-border',
                            'hover:bg-muted/50 transition-colors cursor-pointer'
                          )}
                          onClick={() => {
                            onSelect(template);
                            onOpenChange(false);
                          }}
                        >
                          <div className="flex-1 min-w-0">
                            <p className="text-sm font-medium text-foreground">{template.name}</p>
                            <p className="text-xs text-muted-foreground line-clamp-2 mt-1">
                              {template.content}
                            </p>
                          </div>
                          <div className="flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                            <Button
                              variant="ghost"
                              size="icon"
                              className="h-7 w-7"
                              onClick={(e) => {
                                e.stopPropagation();
                                handleEdit(template);
                              }}
                            >
                              <Pencil className="h-3 w-3" />
                            </Button>
                            <Button
                              variant="ghost"
                              size="icon"
                              className="h-7 w-7 text-destructive"
                              onClick={(e) => {
                                e.stopPropagation();
                                handleDelete(template.id);
                              }}
                            >
                              <Trash2 className="h-3 w-3" />
                            </Button>
                          </div>
                        </div>
                      ))}
                  </div>
                ))
              )}
            </div>
          </>
        )}
      </DialogContent>
    </Dialog>
  );
}
