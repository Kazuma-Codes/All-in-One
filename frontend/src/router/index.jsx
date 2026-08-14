import React, { useEffect, useState } from 'react';
import { createBrowserRouter } from 'react-router-dom';
import { Loader2, WifiOff, RefreshCcw } from 'lucide-react';

import Layout from '../components/layout/Layout';
import AdminLogin from '../pages/AdminLogin';
import Dashboard from '../pages/Dashboard';
import Converter from '../pages/Converter';
import Batch from '../pages/Batch';
import History from '../pages/History';
import Settings from '../pages/Settings';
import Admin from '../pages/Admin';
import NotFound from '../pages/NotFound';

import { ensureSession } from '../api/client';

const Protected = ({ children }) => {
  const [ready, setReady] = useState(() => Boolean(localStorage.getItem('token')));
  const [failed, setFailed] = useState(false);

  useEffect(() => {
    if (ready) return;

    let cancelled = false;

    ensureSession()
      .then(() => {
        if (!cancelled) setReady(true);
      })
      .catch(() => {
        if (!cancelled) setFailed(true);
      });

    return () => {
      cancelled = true;
    };
  }, [ready]);

  const retry = () => {
    setFailed(false);
    setReady(false);
  };

  if (failed) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 p-6">
        <div className="text-center max-w-sm">
          <div className="mx-auto w-14 h-14 rounded-2xl bg-orange-100 flex items-center justify-center mb-4">
            <WifiOff className="h-7 w-7 text-orange-600" />
          </div>
          <h2 className="text-lg font-semibold text-gray-900 mb-1">Couldn't start your session</h2>
          <p className="text-sm text-gray-500 mb-6">
            Our server is temporarily unreachable. Please try again in a moment.
          </p>
          <button
            onClick={retry}
            className="inline-flex items-center gap-2 bg-blue-600 text-white px-5 py-2.5 rounded-xl font-semibold hover:bg-blue-700 transition-colors"
          >
            <RefreshCcw className="h-4 w-4" />
            Retry
          </button>
        </div>
      </div>
    );
  }

  if (!ready) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="flex items-center gap-3 text-gray-500">
          <Loader2 className="animate-spin h-6 w-6 text-blue-600" />
          <span className="font-medium">Preparing your session...</span>
        </div>
      </div>
    );
  }

  return <>{children}</>;
};

export const router = createBrowserRouter([
  {
    path: '/admin-login',
    element: <AdminLogin />,
  },
  {
    path: '/',
    element: (
      <Protected>
        <Layout />
      </Protected>
    ),
    children: [
      {
        index: true,
        element: <Converter />,
      },
      {
        path: 'batch',
        element: <Batch />,
      },
      {
        path: 'dashboard',
        element: <Dashboard />,
      },
      {
        path: 'history',
        element: <History />,
      },
      {
        path: 'settings',
        element: <Settings />,
      },
      {
        path: 'admin',
        element: <Admin />,
      },
    ],
  },
  {
    path: '*',
    element: <NotFound />,
  },
]);
