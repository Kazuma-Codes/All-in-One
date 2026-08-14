import React, { useEffect, useState } from 'react';
import { Download, RefreshCw, Clock, CheckCircle2, XCircle } from 'lucide-react';
import { listJobs, getJobDownloadUrl } from '../api/jobs';
import { getMe } from '../api/users';

const History = () => {
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [isGuest, setIsGuest] = useState(false);

  const loadJobs = async () => {
    setLoading(true);
    try {
      const data = await listJobs();
      setJobs(data || []);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    getMe()
      .then((user) => setIsGuest(Boolean(user.email?.endsWith('@guest.local'))))
      .catch(() => {});
  }, []);

  useEffect(() => {
    loadJobs();
  }, []);

  const visibleJobs =
    isGuest && jobs.length > 0
      ? jobs.filter(
          (job) => new Date(job.created_at).getTime() >= Date.now() - 24 * 60 * 60 * 1000
        )
      : jobs;

  const handleDownload = async (jobId) => {
    const url = await getJobDownloadUrl(jobId);
    window.open(url, '_blank');
  };

  const getStatusBadge = (status) => {
    switch (status) {
      case 'COMPLETED':
        return <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-semibold bg-green-100 text-green-800"><CheckCircle2 className="h-3.5 w-3.5" /> Completed</span>;
      case 'FAILED':
        return <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-semibold bg-red-100 text-red-800"><XCircle className="h-3.5 w-3.5" /> Failed</span>;
      case 'PROCESSING':
        return <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-semibold bg-blue-100 text-blue-800"><RefreshCw className="h-3.5 w-3.5 animate-spin" /> Processing</span>;
      default:
        return <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-semibold bg-amber-100 text-amber-800"><Clock className="h-3.5 w-3.5" /> Queued</span>;
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Conversion History</h1>
          <p className="text-gray-500 text-sm mt-1">Review and download all your processed files.</p>
        </div>

        <button
          onClick={loadJobs}
          className="flex items-center gap-2 bg-white border border-gray-200 px-4 py-2 rounded-xl text-sm font-medium hover:bg-gray-50 transition-colors"
        >
          <RefreshCw className="h-4 w-4" />
          Refresh
        </button>
      </div>

      {loading ? (
        <div className="p-12 text-center text-gray-500">Loading history...</div>
      ) : visibleJobs.length === 0 ? (
        <div className="bg-white border border-dashed border-gray-300 rounded-2xl p-12 text-center text-gray-500">
          {jobs.length === 0
            ? 'No conversions found yet. Start by converting a file!'
            : 'No recent conversions. Guest files are kept for 24 hours.'}
        </div>
      ) : (
        <div className="space-y-3">
          {visibleJobs.map((job) => (
            <div
              key={job.id}
              className="bg-white border border-gray-200 rounded-2xl p-5 flex flex-col sm:flex-row sm:items-center justify-between gap-4 shadow-sm"
            >
              <div>
                <p className="font-semibold text-gray-900">{job.operation}</p>
                <div className="mt-1 flex items-center gap-3 text-xs text-gray-500">
                  <span>Job #{job.id}</span>
                  <span>•</span>
                  {getStatusBadge(job.status)}
                </div>
              </div>

              {job.status === 'COMPLETED' && (
                <button
                  onClick={() => handleDownload(job.id)}
                  className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-xl text-sm font-medium flex items-center justify-center gap-2 transition-colors self-start sm:self-auto"
                >
                  <Download className="h-4 w-4" />
                  Download
                </button>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default History;
