import React from 'react';
import { motion } from 'framer-motion';
import { HeroSection } from './HeroSection';
import { BenefitsSection } from './BenefitsSection'; // Renamed from FeaturesSection
import { DashboardPreview } from './DashboardPreview';
import { TestimonialsSection } from './TestimonialsSection';
import { useScrollAnimation } from '../hooks/useScrollAnimation';

export const HomePage: React.FC = () => {
  const { ref: benefitsRef, controls: benefitsControls } = useScrollAnimation(0.1); // Lower threshold
  const { ref: dashboardRef, controls: dashboardControls } = useScrollAnimation(0.1); // Lower threshold
  const { ref: testimonialsRef, controls: testimonialsControls } = useScrollAnimation(0.1); // Lower threshold

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 text-gray-900 dark:text-gray-100 transition-colors duration-300">
      <main className="relative z-10 overflow-hidden">
        <div className="relative z-10">
          <HeroSection />
          
          {/* Trusted Companies Logos */}
          <section className="mt-24 border-y border-gray-200 dark:border-gray-700 py-10 overflow-hidden transition-colors duration-500">
            <div className="flex justify-center flex-wrap gap-12 md:gap-20 px-6">
              {['NVIDIA', 'AMD', 'Intel', 'AWS', 'Google Cloud', 'Microsoft Azure'].map((company, index) => (
                <motion.div
                  key={company}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.1 }}
                  whileHover={{ 
                    scale: 1.1, 
                    y: -5,
                    transition: { type: "spring", stiffness: 300, damping: 15 }
                  }}
                  className="text-lg font-semibold text-gray-500 dark:text-white 
                            relative group cursor-pointer transition-all duration-300
                            hover:text-gray-900 dark:hover:text-white"
                >
                  {/* Glow effect background */}
                  <span className="absolute inset-0 rounded-lg bg-gradient-to-r from-blue-500/0 to-purple-500/0 
                                  group-hover:from-blue-500/10 group-hover:to-purple-500/10 
                                  blur-xl group-hover:blur-lg transition-all duration-500 -z-10"></span>
                  
                  {/* Text with gradient effect on hover */}
                  <span className="bg-clip-text bg-gradient-to-r from-gray-500 to-gray-500 
                                  group-hover:from-blue-600 group-hover:to-purple-600
                                  dark:from-white dark:to-white
                                  dark:group-hover:from-blue-400 dark:group-hover:to-purple-400
                                  transition-all duration-300">
                    {company}
                  </span>
                  
                  {/* Underline animation */}
                  <span className="absolute -bottom-1 left-0 w-0 h-0.5 bg-gradient-to-r from-blue-500 to-purple-500 
                                  group-hover:w-full transition-all duration-300"></span>
                </motion.div>
              ))}
            </div>
          </section>

          {/* Benefits Section (formerly Features) */}
          <motion.section
            ref={benefitsRef}
            animate={benefitsControls}
            initial="hidden"
            variants={{
              visible: { opacity: 1, y: 0 },
              hidden: { opacity: 0, y: 20 } // Reduced y offset for smoother animation
            }}
            id="benefits" // Changed from features
            className="py-16"
          >
            <BenefitsSection />
          </motion.section>

          {/* Dashboard Preview - no animation delay */}
          <section 
            ref={dashboardRef}
            className="py-16"
          >
            <motion.div
              animate={dashboardControls}
              initial="hidden"
              variants={{
                visible: { opacity: 1, y: 0 },
                hidden: { opacity: 0, y: 20 }
              }}
            >
              <DashboardPreview />
            </motion.div>
          </section>

          {/* Testimonials Section */}
          <motion.section
            ref={testimonialsRef}
            animate={testimonialsControls}
            initial="hidden"
            variants={{
              visible: { opacity: 1, y: 0 },
              hidden: { opacity: 0, y: 20 }
            }}
            id="testimonials"
            className="py-16"
          >
            <TestimonialsSection />
          </motion.section>
        </div>
      </main>
    </div>
  );
};