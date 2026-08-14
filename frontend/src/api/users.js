import api from './client';

export const getMe = async () => {
  const response = await api.get('/users/me');
  return response.data;
};

export const getUsage = async () => {
  const response = await api.get('/users/me/usage');
  return response.data;
};
