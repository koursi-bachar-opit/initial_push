import React from 'react'
import ReactDOM from 'react-dom/client'
import { DashboardApp } from './DashboardApp.tsx'
import { ListingsApp } from './ListingsApp.tsx'
import App from './App.tsx'
import './index.css'

function mountReactApp() {
  // Get the current path and convert to lowercase
  const currentPath = window.location.pathname.toLowerCase();
  
  console.log('Current path:', currentPath);
  console.log('Current URL:', window.location.href);

  // Try to find any of the possible root elements
  const roots = [
    'react-listings-root',
    'react-dashboard-root', 
    'react-homepage-root',
    'react-root'
  ];

  let targetRoot = null;
  let appToMount = null;

  // Check which root element exists on the page
  for (const rootId of roots) {
    const element = document.getElementById(rootId);
    if (element) {
      console.log(`Found root element: ${rootId}`);
      targetRoot = element;
      break;
    }
  }

  // If no specific root found, use body or create one
  if (!targetRoot) {
    console.log('No specific root found, checking for listings in path...');
    
    // Create a new root element if needed
    const newRoot = document.createElement('div');
    newRoot.id = 'react-app-root';
    document.body.appendChild(newRoot);
    targetRoot = newRoot;
  }

  // Determine which app to mount based on URL path
  if (currentPath.includes('/listings') || currentPath.includes('/browse')) {
    console.log('Mounting ListingsApp');
    appToMount = <ListingsApp />;
  } else if (currentPath.includes('/dashboard') || currentPath.includes('/account')) {
    console.log('Mounting DashboardApp');
    const userRole = localStorage.getItem('user_role') || 'buyer';
    appToMount = <DashboardApp userRole={userRole} />;
  } else if (currentPath === '/' || currentPath.includes('/home')) {
    console.log('Mounting Homepage App');
    appToMount = <App />;
  } else {
    console.log('Defaulting to App component');
    appToMount = <App />;
  }

  // Mount the React app
  try {
    const root = ReactDOM.createRoot(targetRoot);
    root.render(
      <React.StrictMode>
        {appToMount}
      </React.StrictMode>
    );
    console.log('React app successfully mounted');
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