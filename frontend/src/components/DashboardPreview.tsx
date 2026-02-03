import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

interface DashboardCard {
  id: string;
  title: string;
  subtitle: string;
  icon: string;
  color: string;
  stats: {
    primary: string;
    secondary: string;
  };
}

const dashboardCards: DashboardCard[] = [
  {
    id: '1',
    title: 'Active Servers',
    subtitle: 'Manage your instances',
    icon: '⚡',
    color: 'blue',
    stats: { primary: '12 Active', secondary: '3 Offline' }
  },
  {
    id: '2',
    title: 'GPU Utilization',
    subtitle: 'Performance metrics',
    icon: '📊',
    color: 'emerald',
    stats: { primary: '85% Avg', secondary: 'Peak 98%' }
  },
  {
    id: '3',
    title: 'Cost Analytics',
    subtitle: 'Usage & billing',
    icon: '💰',
    color: 'purple',
    stats: { primary: '$2,450', secondary: 'This month' }
  },
  {
    id: '4',
    title: 'Network Traffic',
    subtitle: 'Bandwidth monitor',
    icon: '🌐',
    color: 'cyan',
    stats: { primary: '5.2 TB', secondary: 'Data transfer' }
  }
];

export const DashboardPreview: React.FC = () => {
  const [activeCard, setActiveCard] = useState(0);

  return (
    <section className="py-32 relative overflow-hidden">
      <div className="max-w-4xl mx-auto px-6 text-center mb-16">
        <h2 className="text-3xl md:text-5xl font-semibold tracking-tighter text-zinc-900 dark:text-white mb-6">
          Real-time Dashboard
        </h2>
        <p className="text-zinc-600 dark:text-zinc-400 text-lg">
          Monitor everything from one unified dashboard
        </p>
      </div>

      <div className="max-w-6xl mx-auto px-6 relative">
        {/* Dashboard Preview */}
        <div className="relative w-full rounded-2xl bg-zinc-900/5 dark:bg-white/5 p-2.5 ring-1.5 ring-zinc-900/10 dark:ring-white/10">
          <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-3/4 h-3/4 bg-blue-500/20 dark:bg-emerald-500/20 blur-[100px] -z-10 rounded-full"></div>
          
          <div className="w-full bg-white dark:bg-[#0A0A0A] rounded-xl shadow-2xl overflow-hidden border-1.5 border-zinc-200 dark:border-white/10 p-6">
            {/* Dashboard Header */}
            <div className="flex justify-between items-center mb-6 border-b border-zinc-100 dark:border-white/10 pb-4">
              <div className="flex gap-2">
                <div className="w-3 h-3 rounded-full bg-zinc-200 dark:bg-zinc-800"></div>
                <div className="w-3 h-3 rounded-full bg-zinc-200 dark:bg-zinc-800"></div>
              </div>
              <div className="text-xs text-blue-600 dark:text-emerald-400 uppercase tracking-widest font-bold">
                Compute Dashboard
              </div>
            </div>

            {/* Dashboard Content */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {dashboardCards.map((card, index) => (
                <motion.div
                  key={card.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.1 }}
                  whileHover={{ y: -5 }}
                  className={`p-4 rounded-xl bg-zinc-50 dark:bg-zinc-900/50 border border-zinc-200 dark:border-white/10 hover:border-${
                    card.color
                  }-300 dark:hover:border-${card.color}-500/30 transition-all cursor-pointer group`}
                >
                  <div className="flex items-center gap-4 mb-4">
                    <div className={`w-12 h-12 rounded-lg bg-${
                      card.color
                    }-100 dark:bg-${card.color}-500/10 flex items-center justify-center text-${
                      card.color
                    }-600 dark:text-${card.color}-400 group-hover:scale-110 transition-transform`}>
                      <span className="text-2xl">{card.icon}</span>
                    </div>
                    <div className="flex-1">
                      <h3 className="text-lg font-semibold text-zinc-900 dark:text-white">
                        {card.title}
                      </h3>
                      <p className="text-sm text-zinc-500 dark:text-zinc-400 mt-1">
                        {card.subtitle}
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center justify-between">
                    <div className="flex gap-3">
                      <span className="text-sm bg-zinc-100 dark:bg-zinc-800 text-zinc-600 dark:text-zinc-300 px-3 py-1 rounded-full font-medium">
                        {card.stats.primary}
                      </span>
                      <span className="text-sm bg-zinc-100 dark:bg-zinc-800 text-zinc-600 dark:text-zinc-300 px-3 py-1 rounded-full font-medium">
                        {card.stats.secondary}
                      </span>
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>

            {/* Live Metrics Graph */}
            <div className="mt-8 p-4 bg-zinc-50 dark:bg-zinc-900/50 rounded-xl border border-zinc-200 dark:border-white/10">
              <div className="flex justify-between items-center mb-4">
                <h4 className="font-semibold text-zinc-900 dark:text-white">
                  GPU Utilization (Last 24h)
                </h4>
                <span className="text-xs text-emerald-600 dark:text-emerald-400 font-medium">
                  Live
                </span>
              </div>
              <div className="h-32 relative">
                <svg className="w-full h-full" viewBox="0 0 300 100">
                  <path
                    d="M0,80 L30,60 L60,40 L90,70 L120,30 L150,50 L180,20 L210,40 L240,60 L270,30 L300,50"
                    fill="none"
                    stroke="url(#gradient)"
                    strokeWidth="2"
                    className="animate-pulse"
                  />
                  <defs>
                    <linearGradient id="gradient" x1="0%" y1="0%" x2="100%" y2="0%">
                      <stop offset="0%" stopColor="#3b82f6" />
                      <stop offset="100%" stopColor="#10b981" />
                    </linearGradient>
                  </defs>
                </svg>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};