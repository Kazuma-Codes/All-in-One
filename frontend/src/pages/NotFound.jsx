import React from 'react';
import { Link } from 'react-router-dom';
import { Home } from 'lucide-react';

const NotFound = () => {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center p-4 text-center bg-gray-50">
      <h1 className="text-7xl font-extrabold text-gray-900">404</h1>
      <p className="text-xl text-gray-600 mt-4">Page not found</p>
      <p className="text-sm text-gray-400 mt-2 max-w-sm">
        The page you are looking for might have been removed or moved to a different path.
      </p>
      <Link
        to="/"
        className="mt-6 inline-flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-xl font-semibold transition-colors"
      >
        <Home className="h-4 w-4" />
        Return Home
      </Link>
    </div>
  );
};

export default NotFound;
