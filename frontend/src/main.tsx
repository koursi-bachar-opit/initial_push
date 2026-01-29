import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.tsx'
import { DashboardApp } from './DashboardApp.tsx'
import './index.css'

function mountReactApp() {
  const rootElement = document.getElementById('react-root');
  
  if (!rootElement) {
    console.log('No react-root element found');
    return;
  }

  // Determine which app to load based on URL
  const isDashboard = window.location.pathname.includes('/dashboard');
  
  try {
    const root = ReactDOM.createRoot(rootElement);
    
    if (isDashboard) {
      root.render(
        <React.StrictMode>
          <DashboardApp />
        </React.StrictMode>
      );
      console.log('Dashboard React app mounted');
    } else {
      root.render(
        <React.StrictMode>
          <App />
        </React.StrictMode>
      );
      console.log('Homepage React app mounted');
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