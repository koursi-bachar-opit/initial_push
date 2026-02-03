import React from 'react';
import { motion } from 'framer-motion';
import { HomeNavbar } from './HomeNavbar'; // Create this
import { HeroSection } from './HeroSection';
import { FeaturesSection } from './FeaturesSection';
import { DashboardPreview } from './DashboardPreview';
import { PricingSection } from './PricingSection';
import { TestimonialsSection } from './TestimonialsSection';
import { FAQSection } from './FAQSection';
import { HomeFooter } from './HomeFooter'; // Create this
import { useScrollAnimation } from '../hooks/useScrollAnimation';

export const HomePage: React.FC = () => {
  const { ref: featuresRef, controls: featuresControls } = useScrollAnimation();
  const { ref: pricingRef, controls: pricingControls } = useScrollAnimation();
  const { ref: testimonialsRef, controls: testimonialsControls } = useScrollAnimation();
  const { ref: faqRef, controls: faqControls } = useScrollAnimation();

  return (
    <div className="min-h-screen bg-white dark:bg-[#010205] antialiased selection:bg-blue-500/20 selection:text-blue-600 dark:selection:bg-emerald-500/20 dark:selection:text-emerald-400 transition-colors duration-500">
      {/* Grid Lines Background */}
      <div className="fixed inset-0 pointer-events-none z-0 flex justify-center w-full h-full max-w-[90rem] mx-auto px-6">
        <div className="w-full h-full flex justify-between transition-colors duration-500">
          {[...Array(7)].map((_, i) => (
            <div key={i} className={`v-line ${i < 2 ? 'hidden xl:block' : i < 3 ? 'hidden lg:block' : i < 4 ? 'hidden md:block' : ''}`}></div>
          ))}
        </div>
      </div>

      {/* Homepage-specific navbar */}
      <HomeNavbar />

      <main className="relative z-10 pt-32 pb-20 overflow-hidden">
        {/* Particles Background */}
        <div id="particles-js" className="absolute inset-0 z-0">
          <canvas className="particles-js-canvas-el" style={{ width: '100%', height: '100%' }}></canvas>
        </div>
        
        <div className="absolute inset-0 z-[1] bg-transparent dark:bg-black/40 backdrop-blur-[0.5px] pointer-events-none"></div>
        
        <div className="relative z-10">
          <HeroSection />
          
          {/* Trusted Companies Logos */}
          <section className="mt-24 border-y border-zinc-200 dark:border-white/5 py-10 overflow-hidden transition-colors duration-500">
            <div className="flex justify-center flex-wrap gap-12 md:gap-20 opacity-50 px-6 grayscale hover:grayscale-0 transition-all duration-700">
              {['NVIDIA', 'AMD', 'Intel', 'AWS', 'Google Cloud', 'Microsoft Azure'].map((company, index) => (
                <motion.div
                  key={company}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 0.5, y: 0 }}
                  transition={{ delay: index * 0.1 }}
                  className="text-lg font-semibold text-zinc-900 dark:text-white"
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
          >
            <FAQSection />
          </motion.section>
        </div>
      </main>

      {/* Homepage-specific footer */}
      <HomeFooter />
    </div>
  );
};