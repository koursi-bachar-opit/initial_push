import React from 'react'
import ReactDOM from 'react-dom/client'
import { DashboardApp } from './DashboardApp.tsx'
import { ListingsApp } from './ListingsApp.tsx'
import { HomePage } from './components/HomePage.tsx'
import './index.css'

// Lucide icons for components
import { CheckIcon, Github, Linkedin, Mail, ChevronDown, ChevronUp, Moon, Sun } from 'lucide-react'

export { CheckIcon, Github, Linkedin, Mail, ChevronDown, ChevronUp, Moon, Sun }

function mountReactApp() {
  const currentPath = window.location.pathname;
  console.log('Mounting React app for path:', currentPath);

  // Check if we're on homepage (special template) or other pages (base.html)
  const isHomepage = currentPath === '/';
  
  let targetRootId = '';
  let appToMount = null;

  if (isHomepage) {
    // Homepage uses special template - mount to react-homepage-root
    targetRootId = 'react-homepage-root';
    appToMount = <HomePage />;
  } else if (currentPath.includes('/listings') || currentPath.includes('/browse')) {
    // Listings page uses base.html
    targetRootId = 'react-listings-root';
    appToMount = <ListingsApp />;
  } else if (currentPath.includes('/dashboard') || currentPath.includes('/account')) {
    // Dashboard page uses base.html
    targetRootId = 'react-dashboard-root';
    const userRole = localStorage.getItem('user_role') || 'buyer';
    appToMount = <DashboardApp userRole={userRole} />;
  } else if (currentPath.includes('/bookings')) {
    // Bookings page uses base.html
    targetRootId = 'react-bookings-root';
    const userRole = localStorage.getItem('user_role') || 'buyer';
    appToMount = <DashboardApp userRole={userRole} />;
  } else {
    // Default to homepage
    targetRootId = 'react-homepage-root';
    appToMount = <HomePage />;
  }

  // Find or create root element
  let targetRoot = document.getElementById(targetRootId);
  
  if (!targetRoot) {
    console.log(`Creating root element: ${targetRootId}`);
    targetRoot = document.createElement('div');
    targetRoot.id = targetRootId;
    
    // Insert into appropriate location
    if (isHomepage) {
      // Homepage: insert at beginning of body
      document.body.insertBefore(targetRoot, document.body.firstChild);
    } else {
      // Other pages: insert into main content area
      const mainContent = document.querySelector('main');
      if (mainContent) {
        mainContent.appendChild(targetRoot);
      } else {
        document.body.appendChild(targetRoot);
      }
    }
  }

  // Mount the app
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
      fallback.style.display = 'block';
    }
  }
}

// Mount when ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', mountReactApp);
} else {
  mountReactApp();
}