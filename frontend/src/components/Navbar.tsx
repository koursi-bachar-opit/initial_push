import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';

interface NavItem {
  label: string;
  href: string;
}

const navItems: NavItem[] = [
  { label: 'Features', href: '#features' },
  { label: 'Pricing', href: '#pricing' },
  { label: 'Testimonials', href: '#testimonials' },
  { label: 'FAQ', href: '#faq' },
  { label: 'Dashboard', href: '/dashboard' }
];

export const Navbar: React.FC = () => {
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 20);
    };
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  // Hide this navbar on non-homepage routes since base.html already has one
  const isHomepage = window.location.pathname === '/';
  
  if (!isHomepage) {
    return null; // Don't render React navbar on other pages
  }

  return (
    <nav className={`fixed top-0 w-full z-50 transition-all duration-300 ${
      scrolled 
        ? 'nav-bg border-b border-zinc-200/50 dark:border-white/10 backdrop-blur-md' 
        : 'bg-transparent'
    }`}>
      <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
        {/* Logo */}
        <div className="flex items-center gap-2">
          <motion.div
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.5 }}
            className="h-8 w-8 rounded-lg bg-gradient-to-r from-blue-600 to-purple-600 flex items-center justify-center"
          >
            <span className="text-white font-bold text-sm">GPU</span>
          </motion.div>
          <span className="text-xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
            SuperVision
          </span>
        </div>

        {/* Desktop Navigation */}
        <div className="hidden md:flex items-center gap-8">
          {navItems.map((item) => (
            <a
              key={item.label}
              href={item.href}
              className="relative text-sm font-medium text-zinc-500 hover:text-blue-600 dark:text-zinc-400 dark:hover:text-emerald-400 transition-all duration-300 hover:scale-110 group"
            >
              <span className="relative z-10">{item.label}</span>
              <motion.span
                className="absolute inset-x-0 -bottom-1 h-0.5 bg-blue-600 dark:bg-emerald-400 scale-x-0 group-hover:scale-x-100 transition-transform duration-300 origin-left"
                initial={false}
                whileHover={{ scaleX: 1 }}
              />
            </a>
          ))}
        </div>

        {/* Right Side Actions */}
        <div className="flex items-center gap-4">
          <a 
            href="/listings"
            className="text-sm font-medium text-zinc-500 hover:text-zinc-900 dark:text-white/70 dark:hover:text-white transition-all duration-300 hover:scale-105"
          >
            Browse
          </a>
          <motion.a
            href="/signup"
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            className="bg-gradient-to-r from-blue-600 to-emerald-600 dark:from-blue-500 dark:to-emerald-500 text-white text-sm font-semibold px-4 py-2 rounded-full hover:shadow-blue-500/20 transition-all duration-300"
          >
            Get Started
          </motion.a>
        </div>
      </div>
    </nav>
  );
};