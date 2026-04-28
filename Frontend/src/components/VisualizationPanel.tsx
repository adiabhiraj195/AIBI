import { useState, useEffect, useRef } from 'react';
import Plot from 'react-plotly.js';
import { BarChart3, TrendingUp, PieChart, ScatterChart } from 'lucide-react';
import { PlotlyChart } from '../types';

interface VisualizationPanelProps {
  visualizations?: PlotlyChart[];
}

const CHART_ICONS: Record<string, any> = {
  bar: BarChart3,
  line: TrendingUp,
  pie: PieChart,
  scatter: ScatterChart,
  box: BarChart3,
  heatmap: BarChart3,
};

export function VisualizationPanel({ visualizations }: VisualizationPanelProps) {
  const [selectedIndex, setSelectedIndex] = useState(0);
  const [thumbnails, setThumbnails] = useState<{ [key: number]: string }>({});
  const plotRefs = useRef<{ [key: number]: any }>({});

  // Debug logging
  console.log('[VisualizationPanel] Received visualizations:', visualizations);
  console.log('[VisualizationPanel] Visualization count:', visualizations?.length);

  if (!visualizations || visualizations.length === 0) {
    console.log('[VisualizationPanel] No visualizations to display');
    return (
      <div className="bg-gray-900/30 rounded-lg p-6 border border-gray-800/50">
        <div className="h-96 flex items-center justify-center text-gray-500">
          <div className="text-center">
            <BarChart3 className="w-12 h-12 mx-auto mb-3 opacity-50" />
            <p>Visualization will appear here</p>
          </div>
        </div>
      </div>
    );
  }

  const selectedChart = visualizations[selectedIndex];
  console.log('[VisualizationPanel] Selected chart:', selectedChart);
  console.log('[VisualizationPanel] Chart data:', selectedChart?.data);
  console.log('[VisualizationPanel] Chart traces:', selectedChart?.data?.traces);

  return (
    <div className="bg-gray-900/30 rounded-lg border border-gray-800/50 overflow-hidden">
      {/* Chart Thumbnails/Tabs */}
      {visualizations.length > 1 && (
        <div className="flex gap-2 p-4 border-b border-gray-800/50 bg-gray-900/50 overflow-x-auto">
          {visualizations.map((chart, index) => {
            const Icon = CHART_ICONS[chart.type] || BarChart3;
            const chartTitle = chart.layout?.title?.text || chart.layout?.title || `Chart ${index + 1}`;
            const isSelected = index === selectedIndex;

            return (
              <button
                key={index}
                onClick={() => setSelectedIndex(index)}
                className={`
                  flex items-center gap-3 px-4 py-3 rounded-lg transition-all flex-shrink-0
                  ${isSelected 
                    ? 'bg-emerald-500/20 border-2 border-emerald-500 text-emerald-400' 
                    : 'bg-gray-800/50 border-2 border-gray-700/50 text-gray-400 hover:bg-gray-800 hover:border-gray-600'
                  }
                `}
              >
                <Icon className="w-5 h-5" />
                <div className="text-left">
                  <div className="text-sm font-medium capitalize">{chart.type}</div>
                  <div className="text-xs opacity-75 truncate max-w-[150px]">
                    {typeof chartTitle === 'string' ? chartTitle : 'Chart'}
                  </div>
                </div>
              </button>
            );
          })}
        </div>
      )}

      {/* Main Chart Display - Fixed height container */}
      <div className="p-4">
        <div style={{ width: '100%', height: '500px', minHeight: '500px' }}>
          {visualizations.map((chart, index) => (
            <div
              key={index}
              style={{
                display: index === selectedIndex ? 'block' : 'none',
                width: '100%',
                height: '100%'
              }}
            >
              <Plot
                data={chart.data?.traces || chart.data || []}
                layout={{
                  ...chart.layout,
                  autosize: true,
                  width: undefined,
                  height: 500,
                  margin: { l: 60, r: 40, t: 60, b: 80 },
                  paper_bgcolor: 'rgba(15, 23, 42, 0.5)',
                  plot_bgcolor: 'rgba(15, 23, 42, 0.3)',
                  font: {
                    family: 'Inter, system-ui, sans-serif',
                    size: 12,
                    color: '#e2e8f0'
                  },
                  title: {
                    ...chart.layout?.title,
                    font: {
                      size: 16,
                      color: '#f1f5f9'
                    }
                  },
                  xaxis: {
                    ...chart.layout?.xaxis,
                    gridcolor: '#334155',
                    linecolor: '#475569',
                    tickfont: { color: '#cbd5e1' },
                    title: {
                      ...chart.layout?.xaxis?.title,
                      font: { color: '#e2e8f0' }
                    }
                  },
                  yaxis: {
                    ...chart.layout?.yaxis,
                    gridcolor: '#334155',
                    linecolor: '#475569',
                    tickfont: { color: '#cbd5e1' },
                    title: {
                      ...chart.layout?.yaxis?.title,
                      font: { color: '#e2e8f0' }
                    }
                  },
                  legend: {
                    font: { color: '#e2e8f0' },
                    bgcolor: 'rgba(15, 23, 42, 0.8)',
                    bordercolor: '#475569',
                    borderwidth: 1
                  },
                  hoverlabel: {
                    bgcolor: '#1e293b',
                    bordercolor: '#475569',
                    font: { color: '#f1f5f9' }
                  }
                }}
                config={{
                  responsive: true,
                  displayModeBar: true,
                  displaylogo: false,
                  modeBarButtonsToRemove: ['lasso2d', 'select2d'],
                  toImageButtonOptions: {
                    format: 'png',
                    filename: `chart_${index + 1}`,
                    height: 800,
                    width: 1200,
                    scale: 2
                  },
                  ...chart.config
                }}
                style={{ width: '100%', height: '100%' }}
                useResizeHandler={true}
              />
            </div>
          ))}
        </div>

        {/* Chart Info */}
        {visualizations.length > 1 && (
          <div className="text-xs text-gray-500 text-center pt-3 mt-2 border-t border-gray-800/50">
            Showing {selectedIndex + 1} of {visualizations.length} visualizations
          </div>
        )}
      </div>
    </div>
  );
}
