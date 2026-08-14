import api from './client';

export const register = async (email, password) => {
  const response = await api.post('/auth/register', {
    email,
    password,
  });

  localStorage.setItem('token', response.data.access_token);
  return response.data;
};

export const login = async (email, password) => {
  const response = await api.post('/auth/login', {
    email,
    password,
  });

  localStorage.setItem('token', response.data.access_token);
  return response.data;
};

export const logout = () => {
  localStorage.removeItem('token');
};
