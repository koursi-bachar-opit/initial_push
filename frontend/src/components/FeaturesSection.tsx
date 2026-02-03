import React from 'react';
import { motion } from 'framer-motion';
import { FeatureCard } from './FeatureCard';
import { FeatureMarquee } from './FeatureMarquee';

const features = [
  {
    icon: '⚡',
    title: 'Lightning Fast',
    description: 'Deploy GPU instances in under 60 seconds',
    color: 'blue'
  },
  {
    icon: '🔒',
    title: 'Enterprise Security',
    description: 'Military-grade encryption and isolated VPCs',
    color: 'emerald'
  },
  {
    icon: '📊',
    title: 'Real-time Analytics',
    description: 'Monitor performance, usage, and costs',
    color: 'teal'
  },
  {
    icon: '🔄',
    title: 'Auto Scaling',
    description: 'Automatically scale based on workload',
    color: 'cyan'
  },
  {
    icon: '💰',
    title: 'Cost Optimized',
    description: 'Spot instances and reserved pricing',
    color: 'violet'
  },
  {
    icon: '🌐',
    title: 'Global Network',
    description: 'Deploy in 15+ regions worldwide',
    color: 'orange'
  }
];

export const FeaturesSection: React.FC = () => {
  return (
    <section id="features" className="py-20 relative overflow-hidden bg-transparent">
      <div className="max-w-7xl mx-auto px-6 mb-12 text-center">
        <h2 className="text-3xl md:text-4xl font-semibold tracking-tighter text-zinc-900 dark:text-white mb-4">
          Uninterrupted Compute Flow
        </h2>
        <p className="text-zinc-600 dark:text-zinc-400">
          Seamlessly integrated into your development workflow
        </p>
      </div>

      {/* Feature Marquee */}
      <FeatureMarquee features={features} />

      {/* Static Feature Cards */}
      <div className="mt-20 max-w-6xl mx-auto px-6">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {features.slice(0, 3).map((feature, index) => (
            <motion.div
              key={feature.title}
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
            >
              <FeatureCard {...feature} />
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
};