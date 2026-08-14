import React from 'react';
import { Loader2, CheckCircle2, XCircle, Clock } from 'lucide-react';

const JobProgress = ({ status, filename }) => {
  const getStatusUI = () => {
    switch (status) {
      case 'QUEUED':
        return { icon: <Clock className="text-amber-500" />, text: 'Queued in line...', color: 'bg-amber-100 text-amber-800' };
      case 'PROCESSING':
        return { icon: <Loader2 className="animate-spin text-blue-500" />, text: 'Converting...', color: 'bg-blue-100 text-blue-800' };
      case 'COMPLETED':
        return { icon: <CheckCircle2 className="text-green-500" />, text: 'Completed', color: 'bg-green-100 text-green-800' };
      case 'FAILED':
        return { icon: <XCircle className="text-red-500" />, text: 'Failed', color: 'bg-red-100 text-red-800' };
      default:
        return { icon: null, text: 'Unknown', color: 'bg-gray-100 text-gray-800' };
    }
  };

  const ui = getStatusUI();

  return (
    <div className="flex items-center justify-between p-4 bg-white border border-gray-200 rounded-xl shadow-sm">
      <div className="flex items-center gap-3">
        {ui.icon}
        <div>
          <p className="font-medium text-gray-900 truncate max-w-xs">{filename}</p>
          <p className="text-sm text-gray-500">{ui.text}</p>
        </div>
      </div>
      <span className={`px-2.5 py-1 text-xs font-semibold rounded-full ${ui.color}`}>
        {status}
      </span>
    </div>
  );
};

export default JobProgress;
