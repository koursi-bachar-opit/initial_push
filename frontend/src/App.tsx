import React from 'react';
import { motion } from 'framer-motion';
import { HomepageShowcase } from './components/HomepageShowcase';
import { TechStackMarquee } from './components/TechStackMarquee';

function App() {
  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* Hero Section */}
      <div className="bg-gradient-to-br from-blue-600 to-purple-700 text-white">
        <div className="max-w-7xl mx-auto px-4 py-20 text-center">
          <motion.h1 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="text-5xl md:text-6xl font-bold mb-6"
          >
            High-Performance Compute, Simplified
          </motion.h1>
          <p className="text-xl mb-10 max-w-3xl mx-auto opacity-90">
            Rent GPU servers on demand. Scale instantly. Pay only for what you use.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <button 
              onClick={() => window.location.href = '/listings'}
              className="px-8 py-3 bg-white text-blue-600 font-bold rounded-lg hover:bg-gray-100 transition transform hover:scale-105"
            >
              Explore Servers
            </button>
            <button 
              onClick={() => window.location.href = '/signup'}
              className="px-8 py-3 bg-transparent border-2 border-white font-bold rounded-lg hover:bg-white/10 transition"
            >
              Start Free Trial
            </button>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 py-12">
        <HomepageShowcase />
        <TechStackMarquee />
        
        {/* Testimonials */}
        <div className="mt-16">
          <h3 className="text-3xl font-bold text-center text-gray-900 dark:text-white mb-12">
            Trusted by Teams Worldwide
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <TestimonialCard
              quote="Reduced our ML training costs by 60% while improving performance."
              author="Alex Chen"
              role="AI Research Lead"
              company="TechCorp AI"
            />
            <TestimonialCard
              quote="The easiest way to access high-end GPUs without capital expenditure."
              author="Maria Rodriguez"
              role="CTO"
              company="StartupXYZ"
            />
            <TestimonialCard
              quote="24/7 support and reliable infrastructure for our rendering farm."
              author="James Wilson"
              role="Studio Director"
              company="Animation Studios"
            />
          </div>
        </div>
      </div>
    </div>
  );
}

const TestimonialCard: React.FC<{ quote: string; author: string; role: string; company: string }> = ({
  quote, author, role, company
}) => (
  <div className="p-8 bg-white dark:bg-gray-800 rounded-xl shadow-lg hover:shadow-xl transition-shadow border border-gray-200 dark:border-gray-700">
    <div className="text-4xl text-gray-300 dark:text-gray-600 mb-4">"</div>
    <p className="text-gray-700 dark:text-gray-300 mb-6 italic">{quote}</p>
    <div className="border-t pt-4">
      <div className="font-bold text-gray-900 dark:text-white">{author}</div>
      <div className="text-sm text-gray-600 dark:text-gray-400">{role}, {company}</div>
    </div>
  </div>
);

export default App;


// import { ThemeProvider } from './contexts/ThemeContext';
// import { ReactShowcase } from './components/ReactShowcase';

// function App() {
//   return (
//     <ThemeProvider>
//       <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
//         <ReactShowcase />
//       </div>
//     </ThemeProvider>
//   );
// }

// export default App;