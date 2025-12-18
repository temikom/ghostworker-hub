import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Switch } from '@/components/ui/switch';
import { Badge } from '@/components/ui/badge';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Plus, GripVertical, Trash2, Edit, Route, ArrowRight } from 'lucide-react';
import { toast } from 'sonner';
import { routingApi } from '@/lib/api';
import type { SmartRoutingRule, RoutingCondition, RoutingAction } from '@/types';

const conditionFields = [
  { value: 'sentiment', label: 'Sentiment' },
  { value: 'platform', label: 'Platform' },
  { value: 'language', label: 'Language' },
  { value: 'keyword', label: 'Keyword' },
  { value: 'customer_tag', label: 'Customer Tag' },
];

const conditionOperators = [
  { value: 'equals', label: 'Equals' },
  { value: 'contains', label: 'Contains' },
  { value: 'greater_than', label: 'Greater Than' },
  { value: 'less_than', label: 'Less Than' },
];

const actionTypes = [
  { value: 'assign_to_user', label: 'Assign to User' },
  { value: 'assign_to_team', label: 'Assign to Team' },
  { value: 'add_tag', label: 'Add Tag' },
  { value: 'send_auto_reply', label: 'Send Auto Reply' },
  { value: 'escalate', label: 'Escalate' },
];

export function SmartRouting() {
  const [rules, setRules] = useState<SmartRoutingRule[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [editingRule, setEditingRule] = useState<SmartRoutingRule | null>(null);
  const [formData, setFormData] = useState({
    name: '',
    conditions: [{ field: 'sentiment', operator: 'equals', value: '' }] as RoutingCondition[],
    action: { type: 'assign_to_user', target_id: '' } as RoutingAction,
    priority: 1,
    is_active: true,
  });

  useEffect(() => {
    loadRules();
  }, []);

  const loadRules = async () => {
    setIsLoading(true);
    try {
      const data = await routingApi.list();
      setRules(data);
    } catch {
      // Show sample data if API not available
      setRules([
        {
          id: '1',
          name: 'High Priority - Negative Sentiment',
          conditions: [{ field: 'sentiment', operator: 'equals', value: 'negative' }],
          action: { type: 'escalate' },
          priority: 1,
          is_active: true,
        },
        {
          id: '2',
          name: 'Spanish Speakers',
          conditions: [{ field: 'language', operator: 'equals', value: 'es' }],
          action: { type: 'assign_to_team', target_id: 'spanish-team' },
          priority: 2,
          is_active: true,
        },
        {
          id: '3',
          name: 'VIP Customers',
          conditions: [{ field: 'customer_tag', operator: 'equals', value: 'vip' }],
          action: { type: 'assign_to_user', target_id: 'senior-agent' },
          priority: 3,
          is_active: false,
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSave = async () => {
    if (!formData.name.trim()) {
      toast.error('Please enter a rule name');
      return;
    }

    try {
      if (editingRule) {
        await routingApi.update(editingRule.id, formData);
        toast.success('Rule updated');
      } else {
        await routingApi.create(formData);
        toast.success('Rule created');
      }
      setIsDialogOpen(false);
      resetForm();
      loadRules();
    } catch {
      toast.error('Failed to save rule');
    }
  };

  const handleDelete = async (id: string) => {
    try {
      await routingApi.delete(id);
      toast.success('Rule deleted');
      loadRules();
    } catch {
      toast.error('Failed to delete rule');
    }
  };

  const handleToggle = async (rule: SmartRoutingRule) => {
    try {
      await routingApi.update(rule.id, { ...rule, is_active: !rule.is_active });
      loadRules();
    } catch {
      toast.error('Failed to update rule');
    }
  };

  const openEditDialog = (rule: SmartRoutingRule) => {
    setEditingRule(rule);
    setFormData({
      name: rule.name,
      conditions: rule.conditions,
      action: rule.action,
      priority: rule.priority,
      is_active: rule.is_active,
    });
    setIsDialogOpen(true);
  };

  const resetForm = () => {
    setEditingRule(null);
    setFormData({
      name: '',
      conditions: [{ field: 'sentiment', operator: 'equals', value: '' }],
      action: { type: 'assign_to_user', target_id: '' },
      priority: rules.length + 1,
      is_active: true,
    });
  };

  const addCondition = () => {
    setFormData({
      ...formData,
      conditions: [...formData.conditions, { field: 'sentiment', operator: 'equals', value: '' }],
    });
  };

  const removeCondition = (index: number) => {
    setFormData({
      ...formData,
      conditions: formData.conditions.filter((_, i) => i !== index),
    });
  };

  const updateCondition = (index: number, field: keyof RoutingCondition, value: string) => {
    const newConditions = [...formData.conditions];
    newConditions[index] = { ...newConditions[index], [field]: value };
    setFormData({ ...formData, conditions: newConditions });
  };

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <div>
            <CardTitle>Routing Rules</CardTitle>
            <CardDescription>Automatically route conversations based on conditions</CardDescription>
          </div>
          <Dialog open={isDialogOpen} onOpenChange={(open) => { setIsDialogOpen(open); if (!open) resetForm(); }}>
            <DialogTrigger asChild>
              <Button>
                <Plus className="h-4 w-4 mr-2" />
                Add Rule
              </Button>
            </DialogTrigger>
            <DialogContent className="max-w-2xl">
              <DialogHeader>
                <DialogTitle>{editingRule ? 'Edit Rule' : 'Create Routing Rule'}</DialogTitle>
              </DialogHeader>
              <div className="space-y-6">
                <div className="space-y-2">
                  <Label>Rule Name</Label>
                  <Input
                    value={formData.name}
                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                    placeholder="e.g., High Priority Escalation"
                  />
                </div>

                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <Label>Conditions</Label>
                    <Button variant="outline" size="sm" onClick={addCondition}>
                      <Plus className="h-3 w-3 mr-1" />
                      Add Condition
                    </Button>
                  </div>
                  
                  {formData.conditions.map((condition, index) => (
                    <div key={index} className="flex gap-2 items-end">
                      <div className="flex-1">
                        <Select
                          value={condition.field}
                          onValueChange={(v) => updateCondition(index, 'field', v)}
                        >
                          <SelectTrigger>
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            {conditionFields.map((f) => (
                              <SelectItem key={f.value} value={f.value}>{f.label}</SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                      </div>
                      <div className="flex-1">
                        <Select
                          value={condition.operator}
                          onValueChange={(v) => updateCondition(index, 'operator', v)}
                        >
                          <SelectTrigger>
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            {conditionOperators.map((o) => (
                              <SelectItem key={o.value} value={o.value}>{o.label}</SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                      </div>
                      <div className="flex-1">
                        <Input
                          value={condition.value}
                          onChange={(e) => updateCondition(index, 'value', e.target.value)}
                          placeholder="Value"
                        />
                      </div>
                      {formData.conditions.length > 1 && (
                        <Button variant="ghost" size="icon" onClick={() => removeCondition(index)}>
                          <Trash2 className="h-4 w-4 text-destructive" />
                        </Button>
                      )}
                    </div>
                  ))}
                </div>

                <div className="space-y-4">
                  <Label>Action</Label>
                  <div className="flex gap-2">
                    <div className="flex-1">
                      <Select
                        value={formData.action.type}
                        onValueChange={(v) => setFormData({
                          ...formData,
                          action: { ...formData.action, type: v as RoutingAction['type'] },
                        })}
                      >
                        <SelectTrigger>
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          {actionTypes.map((a) => (
                            <SelectItem key={a.value} value={a.value}>{a.label}</SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>
                    {formData.action.type !== 'escalate' && (
                      <div className="flex-1">
                        <Input
                          value={formData.action.target_id || ''}
                          onChange={(e) => setFormData({
                            ...formData,
                            action: { ...formData.action, target_id: e.target.value },
                          })}
                          placeholder="Target ID"
                        />
                      </div>
                    )}
                  </div>
                </div>

                <div className="flex justify-end gap-2">
                  <Button variant="outline" onClick={() => setIsDialogOpen(false)}>Cancel</Button>
                  <Button onClick={handleSave}>{editingRule ? 'Update' : 'Create'} Rule</Button>
                </div>
              </div>
            </DialogContent>
          </Dialog>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="flex justify-center py-8">
              <div className="animate-spin h-8 w-8 border-2 border-primary border-t-transparent rounded-full" />
            </div>
          ) : rules.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-12 text-muted-foreground">
              <Route className="h-12 w-12 mb-4 opacity-50" />
              <p className="text-lg">No routing rules yet</p>
              <p className="text-sm">Create rules to automatically route conversations</p>
            </div>
          ) : (
            <div className="space-y-3">
              {rules.map((rule, index) => (
                <div
                  key={rule.id}
                  className="flex items-center gap-4 p-4 border border-border rounded-lg hover:bg-muted/50 transition-colors"
                >
                  <GripVertical className="h-5 w-5 text-muted-foreground cursor-move" />
                  <div className="flex-1">
                    <div className="flex items-center gap-2">
                      <h4 className="font-medium text-foreground">{rule.name}</h4>
                      <Badge variant={rule.is_active ? 'default' : 'secondary'}>
                        {rule.is_active ? 'Active' : 'Inactive'}
                      </Badge>
                    </div>
                    <div className="flex items-center gap-2 mt-1 text-sm text-muted-foreground">
                      <span className="flex items-center gap-1">
                        {rule.conditions.map((c, i) => (
                          <span key={i}>
                            {i > 0 && ' AND '}
                            {c.field} {c.operator} "{c.value}"
                          </span>
                        ))}
                      </span>
                      <ArrowRight className="h-4 w-4" />
                      <span>{rule.action.type.replace(/_/g, ' ')}</span>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <Switch
                      checked={rule.is_active}
                      onCheckedChange={() => handleToggle(rule)}
                    />
                    <Button variant="ghost" size="icon" onClick={() => openEditDialog(rule)}>
                      <Edit className="h-4 w-4" />
                    </Button>
                    <Button variant="ghost" size="icon" onClick={() => handleDelete(rule.id)}>
                      <Trash2 className="h-4 w-4 text-destructive" />
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Routing Statistics</CardTitle>
          <CardDescription>Overview of routing performance</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <div className="p-4 bg-muted rounded-lg">
              <p className="text-sm text-muted-foreground">Total Routed</p>
              <p className="text-2xl font-bold text-foreground">1,247</p>
              <p className="text-xs text-success">+12% this week</p>
            </div>
            <div className="p-4 bg-muted rounded-lg">
              <p className="text-sm text-muted-foreground">Avg. Response Time</p>
              <p className="text-2xl font-bold text-foreground">2.3m</p>
              <p className="text-xs text-success">-18% improvement</p>
            </div>
            <div className="p-4 bg-muted rounded-lg">
              <p className="text-sm text-muted-foreground">Auto-Escalated</p>
              <p className="text-2xl font-bold text-foreground">89</p>
              <p className="text-xs text-muted-foreground">7.1% of total</p>
            </div>
            <div className="p-4 bg-muted rounded-lg">
              <p className="text-sm text-muted-foreground">Rules Triggered</p>
              <p className="text-2xl font-bold text-foreground">{rules.filter(r => r.is_active).length}</p>
              <p className="text-xs text-muted-foreground">of {rules.length} total</p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
