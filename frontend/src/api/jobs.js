import api from './client';

export const createJob = async (payload) => {
  const response = await api.post('/jobs', payload);
  return response.data;
};

export const listJobs = async () => {
  const response = await api.get('/jobs');
  return response.data;
};

export const getJob = async (jobId) => {
  const response = await api.get(`/jobs/${jobId}`);
  return response.data;
};

export const cancelJob = async (jobId) => {
  const response = await api.post(`/jobs/${jobId}/cancel`);
  return response.data;
};

export const getJobDownloadUrl = async (jobId) => {
  const response = await api.get(`/jobs/${jobId}/download`);
  return response.data.download_url;
};
