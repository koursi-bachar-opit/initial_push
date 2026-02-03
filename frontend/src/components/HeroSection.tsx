import React from 'react';
import { motion } from 'framer-motion';

export const HeroSection: React.FC = () => {
  return (
    <section className="max-w-3xl mx-auto text-center px-6 py-20">
      {/* Main Heading */}
      <motion.h1
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.1 }}
        className="text-5xl md:text-7xl font-semibold text-gray-900 dark:text-white tracking-tighter mb-6 leading-[1.1]"
      >
        High-Performance Compute,
        <br />
        <span className="bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
          On Demand.
        </span>
      </motion.h1>

      {/* Subtitle */}
      <motion.p
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.2 }}
        className="text-lg md:text-xl text-gray-600 dark:text-gray-300 font-normal leading-relaxed mb-10 max-w-xl mx-auto"
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
        <motion.a
          href="/listings"
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          className="group relative rounded-lg p-[1px] bg-gradient-to-r from-blue-600 to-emerald-500 overflow-hidden"
        >
          <div className="relative rounded-lg bg-gradient-to-r from-blue-600 to-emerald-600 px-8 py-3 flex items-center gap-2">
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
        </motion.a>

        <a 
          href="/docs"
          className="group px-8 py-3 rounded-lg border border-gray-200 dark:border-gray-600 text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white hover:bg-gray-50 dark:hover:bg-gray-800 transition-all text-sm font-medium"
        >
          Documentation
        </a>
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
            <div className="text-2xl font-bold text-gray-900 dark:text-white">
              {stat.value}
            </div>
            <div className="text-sm text-gray-500 dark:text-gray-400 mt-1">
              {stat.label}
            </div>
          </div>
        ))}
      </motion.div>
    </section>
  );
};