import React, { useState } from 'react';
import { Brain, TrendingUp, MessageSquare, Database, BarChart3, Sparkles, ArrowRight } from 'lucide-react';
import { Button } from './ui/button';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogFooter } from './ui/dialog';
import { ConnectionCard } from './popups/DatasourcePopup/ConnectionCard';
import { DATA_CONNECTION_OPTIONS, DataSourceModal, getIconComponent } from './popups/DatasourcePopup/DataSourceModal';

interface WelcomePageProps {
  onGetStarted: () => void;
}

export function WelcomePage({ onGetStarted }: WelcomePageProps) {
  const [showSourceModal, setShowSourceModal] = useState(false);
  console.log(showSourceModal, "showSourceModal")
  return (
    <div className="relative min-h-screen bg-linear-to-br from-slate-950 via-slate-900 to-emerald-950 text-white">
      {/* Header */}
      <header className="border-b border-slate-800/50 backdrop-blur-sm">
        <div className="max-w-7xl mx-auto px-8 py-6 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 bg-linear-to-br from-emerald-500 to-emerald-600 rounded-xl flex items-center justify-center shadow-lg shadow-emerald-500/20">
              <Brain className="w-7 h-7 text-white" />
            </div>
            <div>
              <h1 className="text-white">Green.co CFO AI Assistant</h1>
              <p className="text-emerald-400 text-sm">Wind Energy Solutions</p>
            </div>
          </div>
          <Button
            onClick={onGetStarted}
            className="bg-emerald-600 hover:bg-emerald-700 text-white"
          >
            Get Started
            <ArrowRight className="w-4 h-4 ml-2" />
          </Button>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-8 py-20">
        {/* Hero Section */}
        <div className="text-center mb-20">
          <div className="inline-flex items-center gap-2 px-4 py-2 bg-emerald-500/10 border border-emerald-500/20 rounded-full mb-8">
            <Sparkles className="w-4 h-4 text-emerald-400" />
            <span className="text-emerald-400 text-sm">Multi-Agent Conversational AI</span>
          </div>

          <h2 className="text-6xl mb-6 bg-linear-to-r from-white via-emerald-100 to-emerald-300 bg-clip-text text-transparent">
            Your CFO-Based AI Assistant
          </h2>

          <p className="text-xl text-slate-300 max-w-3xl mx-auto mb-12">
            Welcome to your intelligent financial command center. Ask questions naturally, get instant insights,
            and make data-driven decisions with confidence.
          </p>

          <div className="flex gap-4 justify-center">
            <Button
              onClick={onGetStarted}
              size="lg"
              className="bg-emerald-600 hover:bg-emerald-700 text-white"
            >
              Start Analyzing
              <ArrowRight className="w-5 h-5 ml-2" />
            </Button>
            <Button
              size="lg"
              className="bg-emerald-600 hover:bg-emerald-700 text-white"
              onClick={() => setShowSourceModal(!showSourceModal)}
            >
              Connect Data Source
              <ArrowRight className="w-5 h-5 ml-2" />
            </Button>
          </div>
        </div>

        {/* Features Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-20">
          <FeatureCard
            icon={<MessageSquare className="w-6 h-6" />}
            title="Natural Language Queries"
            description="Ask questions in plain English - no SQL or technical knowledge required"
            gradient="from-blue-500/10 to-blue-600/10"
            borderColor="border-blue-500/20"
            iconColor="text-blue-400"
          />

          <FeatureCard
            icon={<TrendingUp className="w-6 h-6" />}
            title="Analysis & Forecasting"
            description="Get real-time financial analysis, predictive forecasting, and trend insights"
            gradient="from-emerald-500/10 to-emerald-600/10"
            borderColor="border-emerald-500/20"
            iconColor="text-emerald-400"
          />

          <FeatureCard
            icon={<BarChart3 className="w-6 h-6" />}
            title="What-If Scenarios"
            description="Explore different scenarios and understand their financial impact instantly"
            gradient="from-purple-500/10 to-purple-600/10"
            borderColor="border-purple-500/20"
            iconColor="text-purple-400"
          />

          <FeatureCard
            icon={<Database className="w-6 h-6" />}
            title="RAG-Based Intelligence"
            description="Powered by Retrieval-Augmented Generation for accurate, context-aware responses"
            gradient="from-amber-500/10 to-amber-600/10"
            borderColor="border-amber-500/20"
            iconColor="text-amber-400"
          />

          <FeatureCard
            icon={<Brain className="w-6 h-6" />}
            title="6-Agent Pipeline"
            description="Router → RAG → Visualization → Summarizer → Follow-up → Reflection"
            gradient="from-pink-500/10 to-pink-600/10"
            borderColor="border-pink-500/20"
            iconColor="text-pink-400"
          />

          <FeatureCard
            icon={<Sparkles className="w-6 h-6" />}
            title="Dashboard & Portal"
            description="Interactive dashboards with real-time metrics and KPI tracking"
            gradient="from-cyan-500/10 to-cyan-600/10"
            borderColor="border-cyan-500/20"
            iconColor="text-cyan-400"
          />
        </div>

        {/* Capabilities Section */}
        <div className="bg-linear-to-br from-slate-800/50 to-slate-900/50 border border-slate-700/50 rounded-2xl p-12 backdrop-blur-sm">
          <h3 className="text-3xl text-center mb-12 text-white">
            What Can I Help You With?
          </h3>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            <div className="space-y-4">
              <CapabilityItem text="Analyze E3 vs E4 turbine performance metrics" />
              <CapabilityItem text="Forecast quarterly revenue and cash flow" />
              <CapabilityItem text="Identify revenue at risk and delays" />
              <CapabilityItem text="Track project margin health and cost efficiency" />
            </div>
            <div className="space-y-4">
              <CapabilityItem text="Explore customer concentration and exposure" />
              <CapabilityItem text="Simulate what-if scenarios for financial planning" />
              <CapabilityItem text="Monitor working capital and cash position" />
              <CapabilityItem text="Generate actionable insights and analysis" />
            </div>
          </div>

          <div className="mt-12 text-center">
            <Button
              onClick={onGetStarted}
              size="lg"
              className="bg-emerald-600 hover:bg-emerald-700 text-white"
            >
              Start Your First Query
              <ArrowRight className="w-5 h-5 ml-2" />
            </Button>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-800/50 mt-20">
        <div className="max-w-7xl mx-auto px-8 py-8 text-center text-slate-400 text-sm">
          <p>Powered by LangGraph, LangChain & LlamaIndex • PostgreSQL Database • Multi-LLM Fallback System</p>
        </div>
      </footer>

      {/* Data Source Dialog */}
      <Dialog open={showSourceModal} onOpenChange={setShowSourceModal}>
        <DialogContent className="min-w-[65vw] max-w-[960px] max-h-[90vh] border-emerald-500/20 bg-linear-to-br from-slate-900 via-slate-950 to-slate-900 shadow-2xl shadow-emerald-900/40 z-50">
          <DataSourceModal open={showSourceModal} onClose={() => setShowSourceModal(false)} />
        </DialogContent>
      </Dialog>
      {/* <DataSourceModal open={showSourceModal} onClose={() => setShowSourceModal(false)} /> */}
    </div>
  );
}

interface FeatureCardProps {
  icon: React.ReactNode;
  title: string;
  description: string;
  gradient: string;
  borderColor: string;
  iconColor: string;
}

function FeatureCard({ icon, title, description, gradient, borderColor, iconColor }: FeatureCardProps) {
  return (
    <div className={`bg-linear-to-br ${gradient} border ${borderColor} rounded-xl p-6 backdrop-blur-sm hover:scale-105 transition-transform duration-200`}>
      <div className={`w-12 h-12 ${iconColor} bg-slate-900/50 rounded-lg flex items-center justify-center mb-4`}>
        {icon}
      </div>
      <h4 className="text-white mb-2">{title}</h4>
      <p className="text-slate-400 text-sm">{description}</p>
    </div>
  );
}

interface CapabilityItemProps {
  text: string;
}

function CapabilityItem({ text }: CapabilityItemProps) {
  return (
    <div className="flex items-start gap-3">
      <div className="w-6 h-6 rounded-full bg-emerald-500/20 flex items-center justify-center shrink-0 mt-0.5">
        <div className="w-2 h-2 rounded-full bg-emerald-400"></div>
      </div>
      <p className="text-slate-300">{text}</p>
    </div>
  );
}