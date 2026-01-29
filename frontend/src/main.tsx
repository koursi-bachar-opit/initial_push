import React from 'react'
import ReactDOM from 'react-dom/client'
import { DashboardApp } from './DashboardApp.tsx'
import App from './App.tsx'
import './index.css'

function mountReactApp() {
  const rootElement = document.getElementById('react-root');
  
  if (!rootElement) {
    console.log('No react-root element found');
    return;
  }

  try {
    const currentPath = window.location.pathname.toLowerCase();
    const userRole = localStorage.getItem('user_role') || 'buyer';
    const root = ReactDOM.createRoot(rootElement);
    
    console.log('Current path:', currentPath);
    console.log('User role:', userRole);
    
    // More specific path checking
    const isHomePage = currentPath === '/' || 
                      currentPath === '/index.html' || 
                      currentPath.includes('/home') ||
                      currentPath === '';
    
    const isDashboardPage = currentPath.includes('/dashboard');
    
    if (isHomePage) {
      // Homepage - mount Homepage App
      console.log('Mounting Homepage App');
      root.render(
        <React.StrictMode>
          <App />
        </React.StrictMode>
      );
    } else if (isDashboardPage) {
      // Dashboard - mount Dashboard App
      console.log('Mounting Dashboard App');
      root.render(
        <React.StrictMode>
          <DashboardApp userRole={userRole} />
        </React.StrictMode>
      );
    } else {
      // Other pages - could mount different app or nothing
      console.log('Not homepage or dashboard, not mounting React');
    }
    
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


// import React from 'react'
// import ReactDOM from 'react-dom/client'
// import App from './App.tsx'
// import './index.css'

// // Function to mount React app
// function mountReactApp() {
//   const rootElement = document.getElementById('react-root')
  
//   if (!rootElement) {
//     console.log('React root element not found - skipping React mount')
//     return
//   }

//   try {
//     ReactDOM.createRoot(rootElement).render(
//       <React.StrictMode>
//         <App />
//       </React.StrictMode>
//     )
//     console.log('React app mounted successfully')
//   } catch (error) {
//     console.error('Failed to mount React app:', error)
//   }
// }

// // Mount when DOM is ready
// if (document.readyState === 'loading') {
//   document.addEventListener('DOMContentLoaded', mountReactApp)
// } else {
//   mountReactApp()
// }