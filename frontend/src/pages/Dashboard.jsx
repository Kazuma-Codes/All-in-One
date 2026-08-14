import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { HardDrive, Activity, CheckCircle, ArrowRight } from 'lucide-react';
import { getUsage } from '../api/users';

const Dashboard = () => {
  const [usage, setUsage] = useState(null);

  useEffect(() => {
    const load = async () => {
      try {
        const data = await getUsage();
        setUsage(data);
      } catch (err) {
        console.error(err);
      }
    };

    load();
  }, []);

  const percentUsed = usage && usage.storage_limit_bytes > 0
    ? Math.round((usage.storage_used_bytes / usage.storage_limit_bytes) * 100)
    : 0;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
          <p className="text-gray-500 text-sm mt-1">Overview of your conversions and storage limits.</p>
        </div>

        <Link
          to="/"
          className="bg-blue-600 hover:bg-blue-700 text-white px-5 py-2.5 rounded-xl font-semibold flex items-center gap-2 transition-colors text-sm shadow-sm"
        >
          New Conversion
          <ArrowRight className="h-4 w-4" />
        </Link>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white p-6 rounded-2xl border border-gray-200 shadow-sm">
          <div className="flex items-center justify-between text-gray-500">
            <p className="text-sm font-medium">Storage Used</p>
            <HardDrive className="h-5 w-5 text-blue-500" />
          </div>
          <p className="text-3xl font-bold mt-3 text-gray-900">{usage ? `${percentUsed}%` : '...'}</p>
          <div className="w-full bg-gray-100 rounded-full h-2 mt-4 overflow-hidden">
            <div className="bg-blue-600 h-2 rounded-full" style={{ width: `${percentUsed}%` }}></div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-2xl border border-gray-200 shadow-sm">
          <div className="flex items-center justify-between text-gray-500">
            <p className="text-sm font-medium">Total Jobs</p>
            <Activity className="h-5 w-5 text-indigo-500" />
          </div>
          <p className="text-3xl font-bold mt-3 text-gray-900">{usage ? usage.total_jobs : '...'}</p>
          <p className="text-xs text-gray-400 mt-4">Lifetime transformations</p>
        </div>

        <div className="bg-white p-6 rounded-2xl border border-gray-200 shadow-sm">
          <div className="flex items-center justify-between text-gray-500">
            <p className="text-sm font-medium">Completed Jobs</p>
            <CheckCircle className="h-5 w-5 text-green-500" />
          </div>
          <p className="text-3xl font-bold mt-3 text-gray-900">{usage ? usage.completed_jobs : '...'}</p>
          <p className="text-xs text-green-600 mt-4">100% processed successfully</p>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
