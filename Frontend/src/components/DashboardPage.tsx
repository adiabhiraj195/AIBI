import { useState, useEffect } from 'react'; // Added useEffect
import {
  LayoutDashboard,
  Trash2,
  ArrowRight,
  Brain
} from 'lucide-react';
import { Button } from './ui/button';
import { Card } from './ui/card';
import { Badge } from './ui/badge';
import { Progress } from './ui/progress';
import { getDashboardItems, deleteDashboardItem, getAuthUser } from '../services/api';
import { DashboardItem } from '../types';
import { VisualizationPanel } from './VisualizationPanel';

interface DashboardPageProps {
  onCardQuery: (query: string) => void;
  onNavigateToChat: () => void;
  onBack?: () => void; // Added
}

export function DashboardPage({ onCardQuery, onNavigateToChat, onBack }: DashboardPageProps) {
  const [hoveredCard, setHoveredCard] = useState<string | null>(null);
  const [dashboardItems, setDashboardItems] = useState<DashboardItem[]>([]);

  // Fetch dashboard items
  useEffect(() => {
    loadDashboardItems();
  }, []);

  const loadDashboardItems = async () => {
    try {
      const user = getAuthUser();
      if (!user) return;

      const items = await getDashboardItems(String(user.id));
      setDashboardItems(items);
    } catch (error) {
      console.error("Failed to load dashboard items", error);
    }
  };

  const handleDeleteItem = async (id: number) => {
    try {
      await deleteDashboardItem(id);
      setDashboardItems(prev => prev.filter(item => item.id !== id));
    } catch (error) {
      console.error("Failed to delete item", error);
    }
  };

  const handleCardClick = (query: string) => {
    // Navigate to chat first, then submit the query
    onNavigateToChat();
    // Use setTimeout to ensure the navigation happens before query submission
    setTimeout(() => {
      onCardQuery(query);
    }, 100);
  };

  return (
    <div className="h-screen overflow-auto bg-gradient-to-br from-slate-950 via-slate-900 to-emerald-950 text-white">
      {/* Header */}
      <header className="border-b border-slate-800/50 backdrop-blur-sm sticky top-0 z-10 bg-slate-950/80">
        <div className="max-w-7xl mx-auto px-8 py-6 flex items-center justify-between">
          <div className="flex items-center gap-3">
            {/* {onBack && (
              <Button
                variant="ghost"
                size="icon"
                onClick={onBack}
                className="mr-2 text-slate-400 hover:text-white hover:bg-slate-800"
              >
                <ArrowLeft className="w-5 h-5" />
              </Button>
            )} */}
            <div className="w-12 h-12 bg-gradient-to-br from-emerald-500 to-emerald-600 rounded-xl flex items-center justify-center shadow-lg shadow-emerald-500/20">
              <Brain className="w-7 h-7 text-white" />
            </div>
            <div>
              <h1 className="text-white">CFO Financial Dashboard</h1>
              <p className="text-emerald-400 text-sm">💰 Chief Financial Officer Command Center</p>
            </div>
          </div>
          <Button
            onClick={onNavigateToChat}
            className="bg-emerald-600 hover:bg-emerald-700 text-white"
          >
            Open Chat Assistant
            <ArrowRight className="w-4 h-4 ml-2" />
          </Button>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-8 py-8">

        {/* Saved Visualizations Section - Grouped by Category */}
        <section className="mb-12">
          <div className="flex items-center gap-3 mb-6">
            <div className="w-10 h-10 bg-amber-500/20 border border-amber-500/30 rounded-lg flex items-center justify-center">
              <LayoutDashboard className="w-5 h-5 text-amber-400" />
            </div>
            <div>
              <h2 className="text-2xl text-white">Dashboard Visualizations</h2>
              <p className="text-slate-400 text-sm">Custom insights saved from chat analysis</p>
            </div>
          </div>

          {dashboardItems.length === 0 ? (
            <div className="text-center p-8 bg-slate-900/30 rounded-xl border border-slate-800 border-dashed">
              <p className="text-slate-500">No pinned visualizations yet. Go to Chat to add some!</p>
            </div>
          ) : (
            // Group items by category
            (() => {
              // Get unique categories
              const categories = Array.from(new Set(dashboardItems.map(item => item.category || 'General')));
              // Sort categories (maybe prioritize General or others if needed)
              categories.sort();

              return (
                <div className="space-y-10">
                  {categories.map(category => {
                    const categoryItems = dashboardItems.filter(item => (item.category || 'General') === category);
                    if (categoryItems.length === 0) return null;

                    return (
                      <div key={category}>
                        <h3 className="text-lg font-semibold text-emerald-400 mb-4 pl-2 border-l-4 border-emerald-500">{category}</h3>
                        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                          {categoryItems.map((item) => (
                            <DashboardItemCard
                              key={item.id}
                              item={item}
                              onDelete={handleDeleteItem}
                            />
                          ))}
                        </div>
                      </div>
                    );
                  })}
                </div>
              );
            })()
          )}
        </section>


      </main>
    </div>
  );
}



interface DashboardItemCardProps {
  item: DashboardItem;
  onDelete: (id: number) => void;
}

function DashboardItemCard({ item, onDelete }: DashboardItemCardProps) {
  const [isExpanded, setIsExpanded] = useState(false);
  const MAX_LENGTH = 150;

  // Simple improved text formatting: Remove ** for bold and replace with clean text
  const cleanDescription = item.description?.replace(/\*\*(.*?)\*\*/g, '$1') || "";

  const shouldTruncate = cleanDescription.length > MAX_LENGTH;
  const displayDescription = isExpanded || !shouldTruncate
    ? cleanDescription
    : `${cleanDescription.substring(0, MAX_LENGTH)}...`;

  return (
    <Card className="bg-slate-900/50 border-slate-700/50 flex flex-col h-full relative group overflow-hidden">
      {/* Header Section */}
      <div className="p-6 pb-2">
        <div className="flex justify-between items-start mb-2">
          <h3 className="text-lg font-semibold text-white leading-tight">{item.title}</h3>
          <Button
            variant="ghost"
            size="icon"
            className="text-slate-400 hover:text-red-400 hover:bg-red-500/10 -mt-1 -mr-2"
            onClick={() => onDelete(item.id)}
          >
            <Trash2 className="w-4 h-4" />
          </Button>
        </div>

        {item.description && (
          <div className="text-sm text-slate-400 mb-2">
            <p className="whitespace-pre-wrap leading-relaxed">
              {displayDescription}
            </p>
            {shouldTruncate && (
              <button
                onClick={() => setIsExpanded(!isExpanded)}
                className="text-emerald-400 hover:text-emerald-300 text-xs font-medium mt-1 focus:outline-none"
              >
                {isExpanded ? 'Show Less' : 'Read More'}
              </button>
            )}
          </div>
        )}

        <p className="text-xs text-slate-500 mt-2">{new Date(item.created_at).toLocaleDateString()} • {new Date(item.created_at).toLocaleTimeString()}</p>
      </div>

      {/* divider */}
      <div className="mx-6 border-b border-slate-700/30 my-2"></div>

      {/* Visualization Section - perfectly padded container */}
      <div className="p-4 flex-grow flex flex-col min-h-[400px]">
        <div className="flex-grow w-full rounded-lg overflow-hidden bg-slate-950/30 border border-slate-800/50 backdrop-blur-sm">
          {/* The VisualizatonPanel usually has its own padding, we ensure the container is neat */}
          <div className="w-full h-full p-2">
            <VisualizationPanel visualizations={[item.visualization_data]} />
          </div>
        </div>
      </div>
    </Card>
  );
}
