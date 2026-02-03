import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { PricingCard } from './PricingCard';

interface PricingTier {
  id: string;
  name: string;
  seats: number;
  price: number;
  period: string;
  setupFee: number;
  features: string[];
  popular?: boolean;
}

const pricingTiers: PricingTier[] = [
  {
    id: '1',
    name: 'Starter',
    seats: 1,
    price: 50,
    period: 'month',
    setupFee: 100,
    features: ['1 GPU Instance', '100GB Storage', 'Basic Support', 'Community Access']
  },
  {
    id: '2',
    name: 'Team',
    seats: 10,
    price: 40,
    period: 'month',
    setupFee: 130,
    features: ['10 GPU Instances', '1TB Storage', 'Priority Support', 'Team Management'],
    popular: true
  },
  {
    id: '3',
    name: 'Enterprise',
    seats: 100,
    price: 24,
    period: 'month',
    setupFee: 800,
    features: ['Unlimited Instances', '10TB Storage', '24/7 Support', 'Custom SLAs', 'Dedicated Manager']
  }
];

export const PricingSection: React.FC = () => {
  const [isAnnual, setIsAnnual] = useState(false);

  const calculatePrice = (price: number) => {
    return isAnnual ? price * 10 : price; // 2 months free for annual
  };

  return (
    <section id="pricing" className="pt-20 pb-0 relative z-10 bg-transparent dark:bg-black/40 backdrop-blur-xl transition-colors duration-500">
      <div className="max-w-7xl mx-auto px-6 relative z-10">
        <div className="text-center mb-10">
          <h2 className="text-3xl md:text-5xl font-semibold tracking-tight text-zinc-900 dark:text-white mb-6">
            Simple, Transparent Pricing
          </h2>
          <p className="text-zinc-600 dark:text-zinc-400 text-lg mb-8">
            Pay only for what you use. No hidden fees.
          </p>
          
          {/* Toggle */}
          <div className="flex justify-center mb-6">
            <button
              onClick={() => setIsAnnual(!isAnnual)}
              className="relative bg-zinc-100 dark:bg-zinc-900 border border-zinc-200 dark:border-white/10 p-1 rounded-full flex items-center cursor-pointer hover:border-blue-500/30 transition-colors"
            >
              <motion.div
                className="absolute left-1 top-1 h-[calc(100%-8px)] w-[calc(50%-4px)] bg-gradient-to-r from-blue-700 to-emerald-700 dark:from-blue-800 dark:to-emerald-800 rounded-full shadow-sm pointer-events-none"
                animate={{ x: isAnnual ? 'calc(100% + 8px)' : '0' }}
                transition={{ type: 'spring', stiffness: 300, damping: 30 }}
              />
              <span className={`relative z-10 px-6 py-2 text-sm font-medium rounded-full transition-colors duration-300 ${
                !isAnnual ? 'text-white' : 'text-zinc-500 dark:text-zinc-400'
              }`}>
                Monthly
              </span>
              <span className={`relative z-10 px-6 py-2 text-sm font-medium rounded-full transition-colors duration-300 ${
                isAnnual ? 'text-white' : 'text-zinc-500 dark:text-zinc-400'
              }`}>
                Annually
              </span>
            </button>
          </div>
        </div>

        {/* Pricing Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-20">
          {pricingTiers.map((tier, index) => (
            <motion.div
              key={tier.id}
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
            >
              <PricingCard 
                {...tier} 
                price={calculatePrice(tier.price)}
                isAnnual={isAnnual}
              />
            </motion.div>
          ))}
        </div>

        {/* Add-ons Section */}
        <div className="border-t border-zinc-200 dark:border-white/5 pt-16 pb-8">
          <div className="text-center mb-10">
            <h3 className="text-2xl font-semibold tracking-tight text-zinc-900 dark:text-white mb-2">
              Add-On Services
            </h3>
            <p className="text-zinc-500 dark:text-zinc-400 text-sm">
              Enhance your compute power with powerful extras
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {[
              {
                icon: '🛡️',
                title: 'Enhanced Security',
                price: 2,
                description: 'Advanced threat protection and compliance monitoring'
              },
              {
                icon: '🚀',
                title: 'Priority GPU Access',
                price: 5,
                description: 'Guanteed access to high-demand GPU models'
              },
              {
                icon: '🤖',
                title: 'AI Optimization',
                price: 3,
                description: 'Auto-tuning for ML workloads and frameworks'
              },
              {
                icon: '📞',
                title: 'Dedicated Support',
                price: 5,
                description: '24/7 dedicated manager and SLA guarantees'
              }
            ].map((addon, index) => (
              <motion.div
                key={addon.title}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
                className="p-6 rounded-2xl bg-white dark:bg-zinc-900/50 border border-zinc-200 dark:border-white/5 transition-all hover:border-blue-500/30"
              >
                <div className="text-3xl mb-4">{addon.icon}</div>
                <h4 className="font-bold text-zinc-900 dark:text-white mb-1">
                  {addon.title}
                </h4>
                <div className="mb-4">
                  <div className="flex items-baseline gap-1">
                    <span className="text-2xl font-bold tracking-tight text-zinc-900 dark:text-white">
                      ${addon.price}
                    </span>
                    <span className="text-sm font-normal text-zinc-500">
                      /instance/hour
                    </span>
                  </div>
                </div>
                <p className="text-xs text-zinc-500 leading-relaxed">
                  {addon.description}
                </p>
              </motion.div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
};