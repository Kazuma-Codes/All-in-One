import api from './client';

export const getSupportedConversions = async () => {
  const response = await api.get('/conversions');
  return response.data;
};
