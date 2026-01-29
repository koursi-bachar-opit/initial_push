import React from 'react'
import ReactDOM from 'react-dom/client'
import { DashboardApp } from './DashboardApp.tsx'
import { ListingsApp } from './ListingsApp.tsx' // Import the ListingsApp
import App from './App.tsx'
import './index.css'

function mountReactApp() {
  // Check for different root elements based on page
  const listingsRoot = document.getElementById('react-listings-root');
  const dashboardRoot = document.getElementById('react-dashboard-root');
  const homepageRoot = document.getElementById('react-homepage-root');
  const defaultRoot = document.getElementById('react-root'); // Fallback
  
  const currentPath = window.location.pathname.toLowerCase();
  
  console.log('Current path:', currentPath);
  console.log('Available roots:', {
    listingsRoot: !!listingsRoot,
    dashboardRoot: !!dashboardRoot,
    homepageRoot: !!homepageRoot,
    defaultRoot: !!defaultRoot
  });

  try {
    const userRole = localStorage.getItem('user_role') || 'buyer';
    
    // Check for listings page
    if (listingsRoot || (currentPath.includes('/listings') && defaultRoot)) {
      console.log('Mounting ListingsApp on listings page');
      const root = ReactDOM.createRoot(listingsRoot || defaultRoot!);
      root.render(
        <React.StrictMode>
          <ListingsApp />
        </React.StrictMode>
      );
      return;
    }
    
    // Check for dashboard page
    if (dashboardRoot || (currentPath.includes('/dashboard') && defaultRoot)) {
      console.log('Mounting DashboardApp on dashboard page');
      const root = ReactDOM.createRoot(dashboardRoot || defaultRoot!);
      root.render(
        <React.StrictMode>
          <DashboardApp userRole={userRole} />
        </React.StrictMode>
      );
      return;
    }
    
    // Check for homepage
    if (homepageRoot || (currentPath === '/' && defaultRoot)) {
      console.log('Mounting App on homepage');
      const root = ReactDOM.createRoot(homepageRoot || defaultRoot!);
      root.render(
        <React.StrictMode>
          <App />
        </React.StrictMode>
      );
      return;
    }
    
    console.log('No React app mounted for current page');
    
  } catch (error) {
    console.error('Error mounting React app:', error);
  }
}

// Mount when ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', mountReactApp);
} else {
  mountReactApp();
}