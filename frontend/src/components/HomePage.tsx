import React from 'react';
import { motion } from 'framer-motion';
import { HeroSection } from './HeroSection';
import { FeaturesSection } from './FeaturesSection';
import { DashboardPreview } from './DashboardPreview';
import { PricingSection } from './PricingSection';
import { TestimonialsSection } from './TestimonialsSection';
import { FAQSection } from './FAQSection';
import { useScrollAnimation } from '../hooks/useScrollAnimation';

export const HomePage: React.FC = () => {
  const { ref: featuresRef, controls: featuresControls } = useScrollAnimation();
  const { ref: pricingRef, controls: pricingControls } = useScrollAnimation();
  const { ref: testimonialsRef, controls: testimonialsControls } = useScrollAnimation();
  const { ref: faqRef, controls: faqControls } = useScrollAnimation();

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 text-gray-900 dark:text-gray-100 transition-colors duration-300">
      {/* No grid lines or particles background */}
      
      <main className="relative z-10 overflow-hidden">
        {/* Remove particles background div */}
        
        <div className="relative z-10">
          <HeroSection />
          
          {/* Trusted Companies Logos - keep this if you want it */}
          <section className="mt-24 border-y border-gray-200 dark:border-gray-700 py-10 overflow-hidden transition-colors duration-500">
            <div className="flex justify-center flex-wrap gap-12 md:gap-20 opacity-50 px-6 grayscale hover:grayscale-0 transition-all duration-700">
              {['NVIDIA', 'AMD', 'Intel', 'AWS', 'Google Cloud', 'Microsoft Azure'].map((company, index) => (
                <motion.div
                  key={company}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 0.5, y: 0 }}
                  transition={{ delay: index * 0.1 }}
                  className="text-lg font-semibold text-gray-900 dark:text-white"
                >
                  {company}
                </motion.div>
              ))}
            </div>
          </section>

          <motion.section
            ref={featuresRef}
            animate={featuresControls}
            initial="hidden"
            variants={{
              visible: { opacity: 1, y: 0 },
              hidden: { opacity: 0, y: 50 }
            }}
            id="features"
            className="py-20"
          >
            <FeaturesSection />
          </motion.section>

          <motion.section
            animate={pricingControls}
            initial="hidden"
            variants={{
              visible: { opacity: 1, y: 0 },
              hidden: { opacity: 0, y: 50 }
            }}
            className="py-20"
          >
            <DashboardPreview />
          </motion.section>

          <motion.section
            ref={pricingRef}
            animate={pricingControls}
            initial="hidden"
            variants={{
              visible: { opacity: 1, y: 0 },
              hidden: { opacity: 0, y: 50 }
            }}
            id="pricing"
            className="py-20"
          >
            <PricingSection />
          </motion.section>

          <motion.section
            ref={testimonialsRef}
            animate={testimonialsControls}
            initial="hidden"
            variants={{
              visible: { opacity: 1, y: 0 },
              hidden: { opacity: 0, y: 50 }
            }}
            id="testimonials"
            className="py-20"
          >
            <TestimonialsSection />
          </motion.section>

          <motion.section
            ref={faqRef}
            animate={faqControls}
            initial="hidden"
            variants={{
              visible: { opacity: 1, y: 0 },
              hidden: { opacity: 0, y: 50 }
            }}
            id="faq"
            className="py-20"
          >
            <FAQSection />
          </motion.section>
        </div>
      </main>
      
      {/* No Footer component - using base.html footer instead */}
    </div>
  );
};