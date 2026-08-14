import { useState } from 'react';
import { requestUploadUrl, completeUpload } from '../api/files';
import { createJob, getJob, getJobDownloadUrl } from '../api/jobs';

export const useUpload = () => {
  const [state, setState] = useState('idle');
  const [jobId, setJobId] = useState(null);
  const [error, setError] = useState(null);
  const [downloadUrl, setDownloadUrl] = useState(null);

  const reset = () => {
    setState('idle');
    setJobId(null);
    setError(null);
    setDownloadUrl(null);
  };

  const uploadFileOnly = async (file) => {
    const uploadData = await requestUploadUrl(
      file.name,
      file.type,
      file.size
    );

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

  const pollJob = async (id) => {
    setState('processing');

    const interval = setInterval(async () => {
      try {
        const currentJob = await getJob(id);

        if (currentJob.status === 'COMPLETED') {
          clearInterval(interval);
          const url = await getJobDownloadUrl(id);
          setDownloadUrl(url);
          setState('completed');
        }

        if (currentJob.status === 'FAILED') {
          clearInterval(interval);
          setState('failed');
          setError(currentJob.error_message || 'Conversion failed');
        }

        if (currentJob.status === 'CANCELLED') {
          clearInterval(interval);
          setState('failed');
          setError('Job cancelled');
        }
      } catch (err) {
        clearInterval(interval);
        setState('failed');
        setError(err.message || 'Failed to poll job status');
      }
    }, 2000);
  };

  const convertSingleFile = async (file, operation) => {
    try {
      reset();
      setState('uploading');

      const fileId = await uploadFileOnly(file);
      setState('queued');

      const job = await createJob({
        operation,
        input_file_id: fileId,
        options: {},
      });

      setJobId(job.id);
      await pollJob(job.id);
    } catch (err) {
      setState('failed');
      setError(err.response?.data?.detail || err.message || 'Conversion failed');
    }
  };

  const convertMultipleFiles = async (files, operation) => {
    try {
      reset();
      setState('uploading');

      const fileIds = [];
      for (const file of files) {
        const fileId = await uploadFileOnly(file);
        fileIds.push(fileId);
      }

      setState('queued');

      const job = await createJob({
        operation,
        input_file_ids: fileIds,
        options: {},
      });

      setJobId(job.id);
      await pollJob(job.id);
    } catch (err) {
      setState('failed');
      setError(err.response?.data?.detail || err.message || 'Conversion failed');
    }
  };

  return {
    convertSingleFile,
    convertMultipleFiles,
    state,
    jobId,
    error,
    downloadUrl,
    reset,
  };
};
