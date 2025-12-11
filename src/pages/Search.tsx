import { useState, useEffect } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { DashboardLayout } from '@/components/layout/DashboardLayout';
import { Card, CardContent } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Search as SearchIcon, MessageSquare, ShoppingBag, Users, Loader2 } from 'lucide-react';
import { PlatformIcon } from '@/components/icons/PlatformIcon';
import { cn } from '@/lib/utils';

interface SearchResult {
  id: string;
  type: 'conversation' | 'order' | 'customer';
  title: string;
  subtitle: string;
  platform?: 'whatsapp' | 'instagram' | 'tiktok' | 'email';
  timestamp?: string;
}

export default function Search() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const initialQuery = searchParams.get('q') || '';
  const [query, setQuery] = useState(initialQuery);
  const [results, setResults] = useState<SearchResult[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('all');

  useEffect(() => {
    if (query.trim()) {
      performSearch();
    } else {
      setResults([]);
    }
  }, [query]);

  const performSearch = async () => {
    setIsLoading(true);
    try {
      const response = await fetch(`/api/search?q=${encodeURIComponent(query)}`);
      if (response.ok) {
        const data = await response.json();
        setResults(data);
      }
    } catch {
      // API not connected
      setResults([]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSelect = (result: SearchResult) => {
    switch (result.type) {
      case 'conversation':
        navigate(`/inbox?id=${result.id}`);
        break;
      case 'order':
        navigate(`/orders?id=${result.id}`);
        break;
      case 'customer':
        navigate(`/customers?id=${result.id}`);
        break;
    }
  };

  const filteredResults = results.filter((r) => {
    if (activeTab === 'all') return true;
    if (activeTab === 'conversations') return r.type === 'conversation';
    if (activeTab === 'orders') return r.type === 'order';
    if (activeTab === 'customers') return r.type === 'customer';
    return true;
  });

  const getIcon = (result: SearchResult) => {
    if (result.platform) {
      return <PlatformIcon platform={result.platform} className="h-5 w-5" />;
    }
    switch (result.type) {
      case 'conversation':
        return <MessageSquare className="h-5 w-5 text-secondary" />;
      case 'order':
        return <ShoppingBag className="h-5 w-5 text-success" />;
      case 'customer':
        return <Users className="h-5 w-5 text-primary" />;
    }
  };

  const counts = {
    all: results.length,
    conversations: results.filter((r) => r.type === 'conversation').length,
    orders: results.filter((r) => r.type === 'order').length,
    customers: results.filter((r) => r.type === 'customer').length,
  };

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Search Input */}
        <div className="relative">
          <SearchIcon className="absolute left-4 top-1/2 -translate-y-1/2 h-5 w-5 text-muted-foreground" />
          <Input
            placeholder="Search conversations, orders, customers..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            className="pl-12 h-12 text-lg"
            autoFocus
          />
          {isLoading && (
            <Loader2 className="absolute right-4 top-1/2 -translate-y-1/2 h-5 w-5 animate-spin text-muted-foreground" />
          )}
        </div>

        {/* Results */}
        {query.trim() ? (
          <Tabs value={activeTab} onValueChange={setActiveTab}>
            <TabsList>
              <TabsTrigger value="all">All ({counts.all})</TabsTrigger>
              <TabsTrigger value="conversations">
                Conversations ({counts.conversations})
              </TabsTrigger>
              <TabsTrigger value="orders">Orders ({counts.orders})</TabsTrigger>
              <TabsTrigger value="customers">Customers ({counts.customers})</TabsTrigger>
            </TabsList>

            <TabsContent value={activeTab} className="mt-4">
              {filteredResults.length === 0 && !isLoading ? (
                <Card>
                  <CardContent className="py-12 text-center">
                    <SearchIcon className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
                    <h3 className="text-lg font-medium text-foreground">No results found</h3>
                    <p className="text-muted-foreground mt-1">
                      Try searching with different keywords
                    </p>
                  </CardContent>
                </Card>
              ) : (
                <div className="space-y-2">
                  {filteredResults.map((result) => (
                    <Card
                      key={`${result.type}-${result.id}`}
                      className="cursor-pointer hover:border-secondary transition-colors"
                      onClick={() => handleSelect(result)}
                    >
                      <CardContent className="p-4 flex items-center gap-4">
                        <div className="flex-shrink-0">{getIcon(result)}</div>
                        <div className="flex-1 min-w-0">
                          <h3 className="font-medium text-foreground truncate">{result.title}</h3>
                          <p className="text-sm text-muted-foreground truncate">
                            {result.subtitle}
                          </p>
                        </div>
                        <span className="text-xs text-muted-foreground capitalize flex-shrink-0">
                          {result.type}
                        </span>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              )}
            </TabsContent>
          </Tabs>
        ) : (
          <Card>
            <CardContent className="py-12 text-center">
              <SearchIcon className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
              <h3 className="text-lg font-medium text-foreground">Search GhostWorker</h3>
              <p className="text-muted-foreground mt-1">
                Search across all your conversations, orders, and customers
              </p>
              <div className="mt-4 text-sm text-muted-foreground">
                <p>
                  Tip: Press <kbd className="bg-muted px-1.5 py-0.5 rounded">⌘K</kbd> or{' '}
                  <kbd className="bg-muted px-1.5 py-0.5 rounded">Ctrl+K</kbd> for quick actions
                </p>
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </DashboardLayout>
  );
}
