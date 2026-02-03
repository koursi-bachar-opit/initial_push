import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ChevronDown, ChevronUp } from 'lucide-react';

interface FAQItem {
  id: string;
  question: string;
  answer: string;
}

const faqItems: FAQItem[] = [
  {
    id: '1',
    question: 'How quickly can I deploy a GPU instance?',
    answer: 'Most GPU instances deploy in under 60 seconds. Our automated provisioning system ensures you can start working immediately.'
  },
  {
    id: '2',
    question: 'What GPU models are available?',
    answer: 'We offer a wide range of NVIDIA (A100, H100, V100, RTX series) and AMD (MI250X, MI300X) GPUs. New models are added regularly.'
  },
  {
    id: '3',
    question: 'Can I scale my instances up or down?',
    answer: 'Yes! You can scale vertically (upgrade GPU/CPU/RAM) or horizontally (add more instances) at any time, with no downtime.'
  },
  {
    id: '4',
    question: 'How is billing handled?',
    answer: 'We bill per second of usage, with no minimum commitment. You only pay for what you use, and you can set up auto-scaling rules to optimize costs.'
  },
  {
    id: '5',
    question: 'What security measures are in place?',
    answer: 'All instances run in isolated VPCs with encrypted storage, zero-trust networking, and regular security audits. We\'re SOC 2 Type II compliant.'
  },
  {
    id: '6',
    question: 'Do you offer enterprise support?',
    answer: 'Yes, we offer 24/7 enterprise support with dedicated account managers and custom SLAs for mission-critical workloads.'
  }
];

export const FAQSection: React.FC = () => {
  const [openId, setOpenId] = useState<string | null>(faqItems[0].id);

  const toggleFAQ = (id: string) => {
    setOpenId(openId === id ? null : id);
  };

  return (
    <section id="faq" className="pt-32 pb-[105px] relative z-10 bg-transparent dark:bg-black/40 backdrop-blur-2xl transition-colors duration-500">
      <div className="max-w-3xl mx-auto px-6">
        <h2 className="text-3xl font-semibold tracking-tighter text-center text-zinc-900 dark:text-white mb-12">
          Frequently Asked Questions
        </h2>
        
        <div className="space-y-2">
          {faqItems.map((item, index) => (
            <motion.div
              key={item.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
              className="border-b border-zinc-200 dark:border-white/5"
            >
              <button
                onClick={() => toggleFAQ(item.id)}
                className="w-full flex items-center justify-between py-6 text-left focus:outline-none"
              >
                <span className="text-base font-medium text-zinc-900 dark:text-white group-hover:text-blue-600 dark:group-hover:text-blue-400 transition-colors">
                  {item.question}
                </span>
                <motion.span
                  animate={{ rotate: openId === item.id ? 180 : 0 }}
                  transition={{ duration: 0.3 }}
                  className="flex items-center justify-center w-6 h-6"
                >
                  {openId === item.id ? (
                    <ChevronUp className="w-4 h-4 text-blue-600 dark:text-blue-400" />
                  ) : (
                    <ChevronDown className="w-4 h-4 text-zinc-400" />
                  )}
                </motion.span>
              </button>
              
              <AnimatePresence>
                {openId === item.id && (
                  <motion.div
                    initial={{ height: 0, opacity: 0 }}
                    animate={{ height: 'auto', opacity: 1 }}
                    exit={{ height: 0, opacity: 0 }}
                    transition={{ duration: 0.3 }}
                    className="overflow-hidden"
                  >
                    <p className="pb-6 text-sm text-zinc-600 dark:text-zinc-400 leading-relaxed">
                      {item.answer}
                    </p>
                  </motion.div>
                )}
              </AnimatePresence>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
};