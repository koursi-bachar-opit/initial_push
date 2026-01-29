import { Card } from 'flowbite-react';
import LiveMetricsDashboard from './LiveMetricsDashboard';
import MachineComparison from './MachineComparison';
import BookingTracker from './BookingTracker';

export const ReactShowcase = () => {
  return (
    <section className="py-12 px-4 max-w-7xl mx-auto">
      <div className="text-center mb-10">
        <h2 className="text-3xl font-bold text-gray-900 dark:text-white mb-4">
          React + TypeScript Interactive Demo
        </h2>
        <p className="text-gray-600 dark:text-gray-300 max-w-2xl mx-auto">
          Modern frontend features built with React hooks, TypeScript type safety, and real-time updates.
          These components fetch live data from your FastAPI backend.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-10">
        <Card className="dark:bg-gray-800">
          <LiveMetricsDashboard />
        </Card>
        
        <Card className="dark:bg-gray-800">
          <MachineComparison />
        </Card>
      </div>

      <div className="mb-10">
        <Card className="dark:bg-gray-800">
          <BookingTracker />
        </Card>
      </div>

      <div className="text-center text-sm text-gray-500 dark:text-gray-400 mt-12">
        <p>
          This React application is embedded in your existing Jinja2 templates using partial hydration.
          All data is fetched from your FastAPI backend at <code className="bg-gray-100 dark:bg-gray-700 px-2 py-1 rounded">/api/v1/</code>
        </p>
      </div>
    </section>
  );
};