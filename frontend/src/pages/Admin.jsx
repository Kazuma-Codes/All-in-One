import React, { useEffect, useState } from 'react';
import { ShieldOff, RefreshCw, Trash2, Users } from 'lucide-react';
import api from '../api/client';
import { getMe } from '../api/users';

const Admin = () => {
  const [stats, setStats] = useState(null);
  const [jobs, setJobs] = useState([]);
  const [users, setUsers] = useState([]);
  const [isAdmin, setIsAdmin] = useState(null);
  const [loading, setLoading] = useState(true);
  const [deletingId, setDeletingId] = useState(null);
  const [error, setError] = useState('');

  const load = async () => {
    setLoading(true);
    setError('');

    try {
      const me = await getMe();

      if (!me.is_admin) {
        setIsAdmin(false);
        return;
      }

      setIsAdmin(true);

      const [statsRes, jobsRes, usersRes] = await Promise.all([
        api.get('/admin/stats'),
        api.get('/admin/jobs'),
        api.get('/admin/users'),
      ]);

      setStats(statsRes.data);
      setJobs(jobsRes.data || []);
      setUsers(usersRes.data || []);
    } catch (err) {
      setError(err.response?.data?.detail || err.message || 'Failed to load admin data');
      setIsAdmin(false);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, []);

  const handleDeleteUser = async (userId, email) => {
    if (!window.confirm(`Delete user ${email} and all their files and jobs?`)) {
      return;
    }

    setDeletingId(userId);
    setError('');

    try {
      await api.delete(`/admin/users/${userId}`);
      setUsers((prev) => prev.filter((u) => u.id !== userId));
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to delete user');
    } finally {
      setDeletingId(null);
    }
  };

  if (loading && isAdmin === null) {
    return <div className="p-12 text-center text-gray-500">Loading admin panel...</div>;
  }

  if (isAdmin === false) {
    return (
      <div className="max-w-xl mx-auto bg-white border border-red-200 rounded-2xl p-12 text-center shadow-sm">
        <ShieldOff className="mx-auto h-10 w-10 text-red-500" />
        <h1 className="text-xl font-bold text-gray-900 mt-4">Access Denied</h1>
        <p className="text-sm text-gray-500 mt-2">
          Only administrators can view this page. Guests are created automatically — contact
          an administrator if you believe this is a mistake.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Admin Overview</h1>
          <p className="text-gray-500 text-sm mt-1">Platform analytics and user administration.</p>
        </div>

        <button
          onClick={load}
          className="flex items-center gap-2 bg-white border border-gray-200 px-4 py-2 rounded-xl text-sm font-medium hover:bg-gray-50 transition-colors"
        >
          <RefreshCw className="h-4 w-4" />
          Refresh
        </button>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-xl p-4 text-sm text-red-700">
          {error}
        </div>
      )}

      {stats && (
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
          <div className="bg-white p-5 rounded-2xl border shadow-sm">
            <p className="text-xs text-gray-500 uppercase font-semibold">Users</p>
            <p className="text-2xl font-bold mt-1">{stats.total_users}</p>
          </div>
          <div className="bg-white p-5 rounded-2xl border shadow-sm">
            <p className="text-xs text-gray-500 uppercase font-semibold">Jobs</p>
            <p className="text-2xl font-bold mt-1">{stats.total_jobs}</p>
          </div>
          <div className="bg-white p-5 rounded-2xl border shadow-sm">
            <p className="text-xs text-gray-500 uppercase font-semibold">Files</p>
            <p className="text-2xl font-bold mt-1">{stats.total_files}</p>
          </div>
          <div className="bg-white p-5 rounded-2xl border shadow-sm">
            <p className="text-xs text-green-600 uppercase font-semibold">Completed</p>
            <p className="text-2xl font-bold mt-1">{stats.completed_jobs}</p>
          </div>
          <div className="bg-white p-5 rounded-2xl border shadow-sm">
            <p className="text-xs text-red-600 uppercase font-semibold">Failed</p>
            <p className="text-2xl font-bold mt-1">{stats.failed_jobs}</p>
          </div>
        </div>
      )}

      <div className="space-y-4">
        <h2 className="text-lg font-bold text-gray-900">Users</h2>
        <div className="bg-white border border-gray-200 rounded-2xl overflow-hidden shadow-sm">
          <table className="w-full text-sm text-left">
            <thead className="bg-gray-50 text-gray-600 text-xs uppercase border-b">
              <tr>
                <th className="p-3.5">ID</th>
                <th className="p-3.5">Email</th>
                <th className="p-3.5">Role</th>
                <th className="p-3.5">Created</th>
                <th className="p-3.5"></th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {users.map((user) => (
                <tr key={user.id} className="hover:bg-gray-50">
                  <td className="p-3.5 font-medium">{user.id}</td>
                  <td className="p-3.5">{user.email}</td>
                  <td className="p-3.5">
                    <span
                      className={`px-2.5 py-0.5 rounded-full text-xs font-semibold ${
                        user.is_admin
                          ? 'bg-indigo-100 text-indigo-800'
                          : 'bg-gray-100 text-gray-600'
                      }`}
                    >
                      {user.is_admin ? 'Admin' : 'User'}
                    </span>
                  </td>
                  <td className="p-3.5 text-gray-500">
                    {new Date(user.created_at).toLocaleString()}
                  </td>
                  <td className="p-3.5 text-right">
                    {!user.is_admin && (
                      <button
                        onClick={() => handleDeleteUser(user.id, user.email)}
                        disabled={deletingId === user.id}
                        className="inline-flex items-center gap-1.5 text-red-600 hover:text-red-800 hover:bg-red-50 px-2.5 py-1.5 rounded-lg text-xs font-medium disabled:opacity-50 transition-colors"
                      >
                        <Trash2 className="h-3.5 w-3.5" />
                        {deletingId === user.id ? 'Deleting...' : 'Delete'}
                      </button>
                    )}
                  </td>
                </tr>
              ))}
              {users.length === 0 && (
                <tr>
                  <td colSpan={5} className="p-6 text-center text-gray-400">
                    <Users className="mx-auto h-6 w-6 mb-1" />
                    No users yet
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      <div className="space-y-4">
        <h2 className="text-lg font-bold text-gray-900">Recent Platform Jobs</h2>
        <div className="bg-white border border-gray-200 rounded-2xl overflow-hidden shadow-sm">
          <table className="w-full text-sm text-left">
            <thead className="bg-gray-50 text-gray-600 text-xs uppercase border-b">
              <tr>
                <th className="p-3.5">ID</th>
                <th className="p-3.5">User ID</th>
                <th className="p-3.5">Operation</th>
                <th className="p-3.5">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {jobs.map((job) => (
                <tr key={job.id} className="hover:bg-gray-50">
                  <td className="p-3.5 font-medium">{job.id}</td>
                  <td className="p-3.5 text-gray-500">{job.user_id}</td>
                  <td className="p-3.5">{job.operation}</td>
                  <td className="p-3.5 font-semibold">{job.status}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default Admin;