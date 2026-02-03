import React from 'react';
import { motion } from 'framer-motion';
import { CheckIcon } from 'lucide-react';

interface PricingCardProps {
  name: string;
  seats: number;
  price: number;
  period: string;
  setupFee: number;
  features: string[];
  popular?: boolean;
  isAnnual: boolean;
}

export const PricingCard: React.FC<PricingCardProps> = ({
  name,
  seats,
  price,
  period,
  setupFee,
  features,
  popular = false,
  isAnnual
}) => {
  const totalPrice = price * seats;

  return (
    <motion.div
      whileHover={{ y: -5 }}
      className={`group relative p-6 bg-white dark:bg-gray-800 border rounded-xl transition-all duration-300 flex flex-col h-full ${
        popular
          ? 'border-blue-500 shadow-lg'
          : 'border-gray-200 dark:border-gray-700'
      }`}
    >
      {popular && (
        <div className="absolute -top-3 left-1/2 -translate-x-1/2">
          <span className="bg-gradient-to-r from-blue-600 to-emerald-600 text-white text-xs font-semibold px-4 py-1 rounded-full">
            Most Popular
          </span>
        </div>
      )}

      <div className="mb-8">
        <h3 className="text-2xl font-bold text-zinc-900 dark:text-white mb-2">
          {name}
        </h3>
        <div className="flex items-baseline gap-2">
          <span className="text-4xl font-bold tracking-tight text-zinc-900 dark:text-white">
            ${price}
          </span>
          <span className="text-zinc-500 dark:text-zinc-400">
            /seat/{period}
          </span>
        </div>
        <div className="text-sm text-zinc-500 dark:text-zinc-400 mt-2">
          {seats} seat{seats !== 1 ? 's' : ''}
        </div>
      </div>

      <div className="mb-8 space-y-4 flex-1">
        {features.map((feature) => (
          <div key={feature} className="flex items-center gap-3">
            <div className="w-5 h-5 rounded-full bg-emerald-100 dark:bg-emerald-500/10 flex items-center justify-center text-emerald-600 dark:text-emerald-400">
              <CheckIcon className="w-3 h-3" />
            </div>
            <span className="text-sm text-zinc-700 dark:text-zinc-300">
              {feature}
            </span>
          </div>
        ))}
      </div>

      <div className="mt-auto pt-6 border-t border-zinc-100 dark:border-white/5">
        <div className="space-y-3">
          <div className="flex justify-between items-center">
            <span className="text-sm text-zinc-500">Total</span>
            <div className="flex flex-col items-end">
              <span className="font-bold text-zinc-900 dark:text-white">
                ${totalPrice}
              </span>
              <span className="text-xs text-zinc-500">/{period}</span>
            </div>
          </div>
          <div className="flex justify-between items-center">
            <span className="text-sm text-zinc-500">Setup Fee</span>
            <span className="font-medium text-zinc-700 dark:text-zinc-300">
              ${setupFee}
            </span>
          </div>
        </div>

        <motion.button
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          className={`w-full mt-6 py-3 rounded-lg font-semibold transition-all ${
            popular
              ? 'bg-gradient-to-r from-blue-600 to-emerald-600 text-white hover:shadow-lg hover:shadow-blue-500/25'
              : 'bg-zinc-100 dark:bg-zinc-800 text-zinc-900 dark:text-white hover:bg-zinc-200 dark:hover:bg-zinc-700'
          }`}
        >
          Get Started
        </motion.button>
      </div>
    </motion.div>
  );
};