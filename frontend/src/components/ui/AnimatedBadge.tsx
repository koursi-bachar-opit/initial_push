import React from 'react';
import { motion } from 'framer-motion';

interface AnimatedBadgeProps {
  text: string;
}

export const AnimatedBadge: React.FC<AnimatedBadgeProps> = ({ text }) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: -20 }}
      animate={{ opacity: 1, y: 0 }}
      className="inline-flex items-center gap-2 px-3 py-1 rounded-full border border-blue-100 dark:border-blue-900/30 bg-blue-50/50 dark:bg-blue-900/10 backdrop-blur-sm mb-8"
    >
      <span className="relative flex h-2 w-2">
        <motion.span
          className="absolute inline-flex h-full w-full rounded-full bg-blue-400 opacity-75"
          animate={{ scale: [1, 1.5, 1] }}
          transition={{ repeat: Infinity, duration: 1.5 }}
        />
        <span className="relative inline-flex rounded-full h-2 w-2 bg-blue-500" />
      </span>
      <span className="text-xs font-medium text-blue-700 dark:text-blue-300 tracking-wide">
        {text}
      </span>
    </motion.div>
  );
};