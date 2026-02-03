import React from 'react'
import ReactDOM from 'react-dom/client'
import { DashboardApp } from './DashboardApp.tsx'
import { ListingsApp } from './ListingsApp.tsx'
import { HomePage } from './components/HomePage.tsx'
import './index.css'

// Import Lucide icons
import { CheckIcon, Github, Linkedin, Mail, ChevronDown, ChevronUp } from 'lucide-react'

// Export Lucide icons for components
export { CheckIcon, Github, Linkedin, Mail, ChevronDown, ChevronUp }

function mountReactApp() {
  // Get the current path
  const currentPath = window.location.pathname;
  
  console.log('Mounting React app for path:', currentPath);

  // Define root IDs for different pages
  const rootConfigs = [
    { id: 'react-listings-root', path: '/listings' },
    { id: 'react-dashboard-root', path: '/dashboard' },
    { id: 'react-homepage-root', path: '/' },
    { id: 'react-account-root', path: '/account' },
    { id: 'react-bookings-root', path: '/bookings' }
  ];

  // Find target root element
  let targetRoot = null;
  let targetRootId = 'react-app-root'; // Default

  // Check for existing root elements
  for (const config of rootConfigs) {
    const element = document.getElementById(config.id);
    if (element) {
      targetRoot = element;
      targetRootId = config.id;
      console.log(`Found root element: ${config.id}`);
      break;
    }
  }

  // If no specific root found, check path and create appropriate root
  if (!targetRoot) {
    console.log('No specific root found, checking path...');
    
    if (currentPath.includes('/listings') || currentPath.includes('/browse')) {
      targetRootId = 'react-listings-root';
    } else if (currentPath.includes('/dashboard') || currentPath.includes('/account')) {
      targetRootId = 'react-dashboard-root';
    } else if (currentPath === '/' || currentPath.includes('/home')) {
      targetRootId = 'react-homepage-root';
    } else if (currentPath.includes('/bookings')) {
      targetRootId = 'react-bookings-root';
    }

    // Create the root element
    targetRoot = document.createElement('div');
    targetRoot.id = targetRootId;
    
    // Insert it into the main content area
    const mainContent = document.querySelector('main');
    if (mainContent) {
      mainContent.appendChild(targetRoot);
    } else {
      document.body.appendChild(targetRoot);
    }
    
    console.log(`Created root element: ${targetRootId}`);
  }

  // Determine which app to mount
  let appToMount = null;

  if (currentPath.includes('/listings') || currentPath.includes('/browse')) {
    console.log('Mounting ListingsApp');
    appToMount = <ListingsApp />;
  } else if (currentPath.includes('/dashboard') || currentPath.includes('/account')) {
    console.log('Mounting DashboardApp');
    const userRole = localStorage.getItem('user_role') || 'buyer';
    appToMount = <DashboardApp userRole={userRole} />;
  } else if (currentPath === '/' || currentPath.includes('/home')) {
    console.log('Mounting HomePage');
    appToMount = <HomePage />;
  } else if (currentPath.includes('/bookings')) {
    console.log('Mounting BookingsApp (defaulting to Dashboard)');
    const userRole = localStorage.getItem('user_role') || 'buyer';
    appToMount = <DashboardApp userRole={userRole} />;
  } else {
    console.log('Defaulting to HomePage');
    appToMount = <HomePage />;
  }

  // Mount the React app
  try {
    const root = ReactDOM.createRoot(targetRoot);
    root.render(
      <React.StrictMode>
        {appToMount}
      </React.StrictMode>
    );
    console.log(`React app successfully mounted to ${targetRootId}`);
  } catch (error) {
    console.error('Error mounting React app:', error);
    // Show fallback content
    const fallback = document.getElementById('fallback-content');
    if (fallback) {
      fallback.classList.remove('hidden');
    }
  }
}

// Mount when ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', mountReactApp);
} else {
  mountReactApp();
}