import api from './client';

export const requestUploadUrl = async (filename, contentType, size) => {
  const response = await api.post('/files/upload-url', {
    filename,
    content_type: contentType,
    size,
  });

  return response.data;
};

export const completeUpload = async (fileId) => {
  const response = await api.post(`/files/${fileId}/complete`);
  return response.data;
};

export const listFiles = async () => {
  const response = await api.get('/files');
  return response.data;
};

export const deleteFile = async (fileId) => {
  const response = await api.delete(`/files/${fileId}`);
  return response.data;
};

export const getFileDownloadUrl = async (fileId) => {
  const response = await api.get(`/files/${fileId}/download`);
  return response.data.download_url;
};
