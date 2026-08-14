import React, { useEffect, useState } from 'react';
import { NavLink, Link, useNavigate } from 'react-router-dom';
import { RefreshCw, LogOut, Shield, LogIn } from 'lucide-react';
import { logout } from '../../api/auth';
import { getMe } from '../../api/users';

const Navbar = () => {
  const navigate = useNavigate();
  const [isAdmin, setIsAdmin] = useState(false);
  const [checked, setChecked] = useState(false);

  useEffect(() => {
    let cancelled = false;

    getMe()
      .then((user) => {
        if (!cancelled) setIsAdmin(Boolean(user.is_admin));
      })
      .catch(() => {
        if (!cancelled) setIsAdmin(false);
      })
      .finally(() => {
        if (!cancelled) setChecked(true);
      });

    return () => {
      cancelled = true;
    };
  }, []);

  const handleLogout = () => {
    logout();
    navigate('/auth');
  };

  const navLinkClass = ({ isActive }) =>
    `px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
      isActive
        ? 'bg-blue-50 text-blue-600 font-semibold'
        : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
    }`;

  return (
    <nav className="bg-white border-b border-gray-200 sticky top-0 z-40">
      <div className="max-w-6xl mx-auto px-4 h-16 flex items-center justify-between">
        <Link to="/" className="flex items-center gap-2 font-bold text-lg text-gray-900">
          <div className="bg-blue-600 text-white p-1.5 rounded-lg">
            <RefreshCw className="h-4 w-4" />
          </div>
          Universal Converter
        </Link>

        <div className="flex items-center gap-2 md:gap-4">
          <NavLink to="/" end className={navLinkClass}>Convert</NavLink>
          <NavLink to="/batch" className={navLinkClass}>Batch</NavLink>
          <NavLink to="/dashboard" className={navLinkClass}>Dashboard</NavLink>
          <NavLink to="/history" className={navLinkClass}>History</NavLink>
          <NavLink to="/settings" className={navLinkClass}>Settings</NavLink>

          {isAdmin && (
            <NavLink to="/admin" className={navLinkClass}>
              <span className="inline-flex items-center gap-1.5">
                <Shield className="h-4 w-4" />
                Admin
              </span>
            </NavLink>
          )}

          {checked && !isAdmin ? (
            <Link
              to="/auth"
              className="flex items-center gap-1.5 ml-2 bg-gray-100 hover:bg-gray-200 text-gray-700 px-3 py-2 rounded-lg text-sm font-medium transition-colors"
            >
              <LogIn className="h-4 w-4" />
              <span className="hidden sm:inline">Sign in</span>
            </Link>
          ) : (
            <button
              onClick={handleLogout}
              className="flex items-center gap-1.5 ml-2 bg-gray-100 hover:bg-gray-200 text-gray-700 px-3 py-2 rounded-lg text-sm font-medium transition-colors"
            >
              <LogOut className="h-4 w-4" />
              <span className="hidden sm:inline">Logout</span>
            </button>
          )}
        </div>
      </div>
    </nav>
  );
};

export default Navbar;