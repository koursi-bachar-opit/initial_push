import React from 'react';
import { ReactShowcase } from './components/ReactShowcase';

export const DashboardApp: React.FC = () => {
  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 p-4">
      <div className="max-w-7xl mx-auto">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Dashboard</h1>
          <p className="text-gray-600 dark:text-gray-300">Monitor your servers and bookings</p>
        </div>
        <ReactShowcase />
      </div>
    </div>
  );
};

// import React from 'react';
// import { Flowbite } from 'flowbite-react';
// import { ReactShowcase } from './components/ReactShowcase';

// export const DashboardApp: React.FC = () => {
//   return (
//     <Flowbite>
//       <div className="min-h-screen bg-gray-50 dark:bg-gray-900 p-4">
//         <div className="max-w-7xl mx-auto">
//           <div className="mb-8">
//             <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Dashboard</h1>
//             <p className="text-gray-600 dark:text-gray-300">Monitor your servers and bookings</p>
//           </div>
//           <ReactShowcase />
//         </div>
//       </div>
//     </Flowbite>
//   );
// };