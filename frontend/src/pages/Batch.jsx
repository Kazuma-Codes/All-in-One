import React, { useEffect, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { UploadCloud, Layers, CheckCircle2 } from 'lucide-react';

import api from '../api/client';
import { requestUploadUrl, completeUpload } from '../api/files';
import { getSupportedConversions } from '../api/conversions';
import FormatSelector from '../components/conversion/FormatSelector';
import FileCard from '../components/file/FileCard';

const Batch = () => {
  const [files, setFiles] = useState([]);
  const [operations, setOperations] = useState([]);
  const [operation, setOperation] = useState('');
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');

  useEffect(() => {
    const load = async () => {
      try {
        const data = await getSupportedConversions();
        const all = [
          ...(data.image || []),
          ...(data.pdf || []),
          ...(data.document || []),
        ];

        setOperations(all);
        if (all.length > 0) {
          setOperation(all[0]);
        }
      } catch (err) {
        console.error(err);
      }
    };

    load();
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop: (acceptedFiles) => {
      setFiles((prev) => [...prev, ...acceptedFiles]);
    },
    multiple: true,
  });

  const uploadFile = async (file) => {
    const uploadData = await requestUploadUrl(file.name, file.type, file.size);

    await fetch(uploadData.upload_url, {
      method: 'PUT',
      body: file,
      headers: {
        'Content-Type': file.type,
      },
    });

    await completeUpload(uploadData.file_id);
    return uploadData.file_id;
  };

  const handleBatchConvert = async () => {
    if (files.length === 0) return;

    setLoading(true);
    setMessage('');

    try {
      const fileIds = [];
      for (const file of files) {
        const fileId = await uploadFile(file);
        fileIds.push(fileId);
      }

      const response = await api.post('/batch', {
        file_ids: fileIds,
        operation,
        options: {},
      });

      setMessage(`Created ${response.data.count || fileIds.length} batch jobs. Check History for download links.`);
      setFiles([]);
    } catch (err) {
      setMessage(err.response?.data?.detail || err.message || 'Batch conversion failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Batch Conversion</h1>
        <p className="text-gray-500 text-sm mt-1">Convert multiple files at once using identical operations.</p>
      </div>

      <div className="bg-white border border-gray-200 rounded-2xl p-6 shadow-sm space-y-6">
        <div>
          <label className="text-sm font-semibold text-gray-700 mb-2 block">
            Target Batch Format
          </label>
          <FormatSelector
            value={operation}
            onChange={setOperation}
            options={operations}
          />
        </div>

        <div
          {...getRootProps()}
          className={`border-2 border-dashed rounded-2xl p-10 text-center cursor-pointer transition-colors ${
            isDragActive
              ? 'border-blue-500 bg-blue-50'
              : 'border-gray-300 hover:border-gray-400 bg-gray-50'
          }`}
        >
          <input {...getInputProps()} />
          <UploadCloud className="mx-auto h-12 w-12 text-gray-400" />
          <p className="mt-3 text-sm font-medium text-gray-700">Drop multiple files here for batch processing</p>
        </div>

        {files.length > 0 && (
          <div className="space-y-2">
            <label className="text-xs font-semibold text-gray-500 uppercase tracking-wider">
              Batch Queue ({files.length} files)
            </label>
            {files.map((file, index) => (
              <FileCard
                key={`${file.name}-${index}`}
                file={file}
                onRemove={() =>
                  setFiles((prev) => prev.filter((_, i) => i !== index))
                }
              />
            ))}
          </div>
        )}

        <button
          onClick={handleBatchConvert}
          disabled={files.length === 0 || loading}
          className="w-full bg-blue-600 text-white py-3.5 rounded-xl font-semibold hover:bg-blue-700 disabled:bg-gray-300 transition-colors flex items-center justify-center gap-2"
        >
          <Layers className="h-5 w-5" />
          {loading ? 'Submitting Batch...' : `Convert ${files.length} Files`}
        </button>

        {message && (
          <div className="bg-blue-50 border border-blue-200 rounded-xl p-4 text-sm text-blue-900 flex items-center gap-2">
            <CheckCircle2 className="h-5 w-5 text-blue-600 shrink-0" />
            {message}
          </div>
        )}
      </div>
    </div>
  );
};

export default Batch;
