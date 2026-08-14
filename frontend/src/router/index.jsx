import React, { useEffect, useState } from 'react';
import { createBrowserRouter, Navigate } from 'react-router-dom';
import { Loader2 } from 'lucide-react';

import Layout from '../components/layout/Layout';
import Auth from '../pages/Auth';
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

  if (failed) {
    return <Navigate to="/auth" replace />;
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
    path: '/auth',
    element: <Auth />,
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
