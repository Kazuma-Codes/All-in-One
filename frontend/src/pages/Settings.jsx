import React, { useEffect, useState } from 'react';
import { User, Shield, HardDrive, Clock } from 'lucide-react';
import { getMe } from '../api/users';

const Settings = () => {
  const [user, setUser] = useState(null);

  useEffect(() => {
    const load = async () => {
      try {
        const data = await getMe();
        setUser(data);
      } catch (err) {
        console.error(err);
      }
    };

    load();
  }, []);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Settings</h1>
        <p className="text-gray-500 text-sm mt-1">Manage your account profile and check service quotas.</p>
      </div>

      <div className="bg-white border border-gray-200 rounded-2xl p-6 max-w-xl shadow-sm space-y-6">
        <div className="flex items-center gap-4 pb-6 border-b border-gray-100">
          <div className="p-3 bg-blue-50 text-blue-600 rounded-2xl">
            <User className="h-6 w-6" />
          </div>
          <div>
            <p className="text-xs font-semibold text-gray-400 uppercase tracking-wider">Account</p>
            <p className="text-lg font-bold text-gray-900">{user?.email || 'Loading...'}</p>
          </div>
        </div>

        <div className="space-y-4">
          <h2 className="text-sm font-bold text-gray-900 uppercase tracking-wider">Quota & Limits</h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-sm">
            <div className="p-4 bg-gray-50 rounded-xl">
              <div className="flex items-center gap-2 text-gray-600 mb-1">
                <HardDrive className="h-4 w-4" />
                <span>Max Upload Size</span>
              </div>
              <p className="text-base font-bold text-gray-900">250 MB</p>
            </div>

            <div className="p-4 bg-gray-50 rounded-xl">
              <div className="flex items-center gap-2 text-gray-600 mb-1">
                <Shield className="h-4 w-4" />
                <span>Total Storage Quota</span>
              </div>
              <p className="text-base font-bold text-gray-900">500 MB</p>
            </div>

            <div className="p-4 bg-gray-50 rounded-xl sm:col-span-2">
              <div className="flex items-center gap-2 text-gray-600 mb-1">
                <Clock className="h-4 w-4" />
                <span>Download Link Expiration</span>
              </div>
              <p className="text-base font-bold text-gray-900">24 Hours</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Settings;
