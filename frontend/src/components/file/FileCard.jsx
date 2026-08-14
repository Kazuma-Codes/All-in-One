import React from 'react';
import { X, FileText } from 'lucide-react';

const FileCard = ({ file, onRemove }) => {
  const sizeMb = (file.size / (1024 * 1024)).toFixed(2);

  return (
    <div className="flex items-center justify-between bg-white border border-gray-200 rounded-xl p-3.5 shadow-sm">
      <div className="flex items-center gap-3 min-w-0">
        <div className="p-2 bg-blue-50 text-blue-600 rounded-lg shrink-0">
          <FileText className="h-5 w-5" />
        </div>
        <div className="min-w-0">
          <p className="font-medium text-sm text-gray-900 truncate">{file.name}</p>
          <p className="text-xs text-gray-500">{sizeMb} MB</p>
        </div>
      </div>

      <button
        onClick={onRemove}
        className="p-1.5 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors"
        title="Remove file"
      >
        <X className="h-4 w-4" />
      </button>
    </div>
  );
};

export default FileCard;
