import React from 'react';
import { motion } from 'framer-motion';
import { AnimatedBadge } from './ui/AnimatedBadge';

export const HeroSection: React.FC = () => {
  return (
    <section className="max-w-3xl mx-auto text-center px-6 relative z-10">
      {/* Animated Badge */}
      <AnimatedBadge text="GPU Compute 2.0 is now live" />

      {/* Main Heading */}
      <motion.h1
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.1 }}
        className="text-5xl md:text-7xl font-semibold text-zinc-900 dark:text-white tracking-tighter mb-6 leading-[1.1]"
      >
        High-Performance Compute,
        <br />
        <span className="text-gradient-gpu">On Demand.</span>
      </motion.h1>

      {/* Subtitle */}
      <motion.p
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.2 }}
        className="text-lg md:text-xl text-zinc-600 dark:text-zinc-400 font-normal leading-relaxed mb-10 max-w-xl mx-auto"
      >
        Rent GPU servers instantly. Scale as needed. Pay only for what you use.
        The most flexible compute marketplace for AI, ML, and HPC.
      </motion.p>

      {/* CTA Buttons */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.3 }}
        className="flex flex-col sm:flex-row items-center justify-center gap-4"
      >
        <motion.button
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          className="group relative rounded-full p-[1px] bg-gradient-to-r from-blue-600/80 to-emerald-500/80 overflow-hidden shadow-lg shadow-blue-500/20 transition-transform duration-200"
        >
          <div className="relative rounded-full bg-gradient-to-r from-blue-600 to-emerald-600 dark:from-blue-500 dark:to-emerald-500 px-8 py-3 flex items-center gap-2">
            <span className="text-sm font-bold text-white tracking-tight">
              Browse Listings
            </span>
            <motion.svg
              xmlns="http://www.w3.org/2000/svg"
              width="24"
              height="24"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              className="w-4 h-4 text-white/90 group-hover:translate-x-1 transition-transform stroke-2"
            >
              <path d="M5 12h14" />
              <path d="m12 5 7 7-7 7" />
            </motion.svg>
          </div>
        </motion.button>

        <button className="group px-8 py-3 rounded-full border border-zinc-200 dark:border-white/10 text-zinc-600 dark:text-zinc-300 hover:text-black dark:hover:text-white hover:bg-zinc-50 dark:hover:bg-white/5 transition-all text-sm font-medium">
          Documentation
        </button>
      </motion.div>

      {/* Stats */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.6, delay: 0.4 }}
        className="mt-16 grid grid-cols-3 gap-8 max-w-md mx-auto"
      >
        {[
          { value: '100+', label: 'GPU Models' },
          { value: '99.9%', label: 'Uptime' },
          { value: '24/7', label: 'Support' },
        ].map((stat, index) => (
          <div key={stat.label} className="text-center">
            <div className="text-2xl font-bold text-zinc-900 dark:text-white">
              {stat.value}
            </div>
            <div className="text-sm text-zinc-500 dark:text-zinc-400 mt-1">
              {stat.label}
            </div>
          </div>
        ))}
      </motion.div>
    </section>
  );
};