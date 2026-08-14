import React, { useCallback, useEffect, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { UploadCloud, Loader2, CheckCircle2, XCircle, Download } from 'lucide-react';

import { useUpload } from '../hooks/useUpload';
import { getSupportedConversions } from '../api/conversions';
import FormatSelector from '../components/conversion/FormatSelector';
import FileCard from '../components/file/FileCard';

const Converter = () => {
  const {
    convertSingleFile,
    convertMultipleFiles,
    state,
    error,
    downloadUrl,
    reset,
  } = useUpload();

  const [operations, setOperations] = useState([]);
  const [operation, setOperation] = useState('');
  const [files, setFiles] = useState([]);

  const isMerge = operation === 'pdf.merge';

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
        console.error('Failed to load supported operations', err);
      }
    };

    load();
  }, []);

  const onDrop = useCallback(
    (acceptedFiles) => {
      if (isMerge) {
        setFiles((prev) => [...prev, ...acceptedFiles]);
      } else {
        setFiles([acceptedFiles[0]]);
      }
    },
    [isMerge]
  );

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    multiple: isMerge,
  });

  const handleConvert = async () => {
    if (files.length === 0) return;

    if (isMerge) {
      await convertMultipleFiles(files, operation);
    } else {
      await convertSingleFile(files[0], operation);
    }
  };

  const busy =
    state === 'uploading' ||
    state === 'requesting' ||
    state === 'confirming' ||
    state === 'queued' ||
    state === 'processing';

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">File Converter</h1>
        <p className="text-gray-500 text-sm mt-1">Convert images, documents, and PDFs in seconds.</p>
      </div>

      <div className="bg-white border border-gray-200 rounded-2xl p-6 shadow-sm space-y-6">
        <div>
          <label className="text-sm font-semibold text-gray-700 mb-2 block">
            Target Conversion
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
          <p className="mt-3 text-sm font-medium text-gray-700">
            {isMerge
              ? 'Drop multiple PDF files here for merging'
              : 'Drag & drop a file, or click to browse'}
          </p>
          <p className="text-xs text-gray-400 mt-1">Supports images, documents, and PDFs up to 25MB</p>
        </div>

        {files.length > 0 && (
          <div className="space-y-2">
            <label className="text-xs font-semibold text-gray-500 uppercase tracking-wider">
              Selected Files ({files.length})
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
          onClick={handleConvert}
          disabled={files.length === 0 || busy}
          className="w-full bg-blue-600 text-white py-3.5 rounded-xl font-semibold hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors flex items-center justify-center gap-2 shadow-sm"
        >
          {busy && <Loader2 className="animate-spin h-5 w-5" />}
          {busy ? 'Processing Conversion...' : 'Convert Now'}
        </button>
      </div>

      {state === 'completed' && downloadUrl && (
        <div className="bg-green-50 border border-green-200 rounded-2xl p-6 flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-3 text-green-800">
            <CheckCircle2 className="h-6 w-6 text-green-600 shrink-0" />
            <div>
              <p className="font-semibold">Conversion Completed Successfully!</p>
              <p className="text-xs text-green-700">Your processed file is ready for download.</p>
            </div>
          </div>

          <a
            href={downloadUrl}
            target="_blank"
            rel="noreferrer"
            className="w-full sm:w-auto bg-green-600 hover:bg-green-700 text-white px-6 py-3 rounded-xl font-semibold flex items-center justify-center gap-2 transition-colors shrink-0"
          >
            <Download className="h-4 w-4" />
            Download File
          </a>
        </div>
      )}

      {state === 'failed' && (
        <div className="bg-red-50 border border-red-200 rounded-2xl p-6">
          <div className="flex items-center gap-2 text-red-800 font-semibold">
            <XCircle className="h-5 w-5 text-red-600" />
            Conversion Failed
          </div>
          <p className="mt-2 text-sm text-red-700">{error}</p>
          <button
            onClick={reset}
            className="mt-4 bg-gray-900 text-white px-4 py-2 rounded-xl text-sm font-medium hover:bg-gray-800"
          >
            Try Again
          </button>
        </div>
      )}
    </div>
  );
};

export default Converter;
