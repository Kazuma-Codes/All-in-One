import axios from 'axios';

const baseURL = import.meta.env.VITE_API_URL || '/api/v1';

const api = axios.create({
  baseURL,
});

const createGuest = async () => {
  const response = await axios.post(`${baseURL}/auth/guest`);
  localStorage.setItem('token', response.data.access_token);
  return response.data.access_token;
};

export const ensureSession = async () => {
  const existing = localStorage.getItem('token');

  if (existing) {
    return existing;
  }

  return createGuest();
};

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');

  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }

  return config;
});

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const original = error.config;

    if (original && error.response?.status === 401 && !original._guestRetried) {
      original._guestRetried = true;

      try {
        const token = await createGuest();
        original.headers.Authorization = `Bearer ${token}`;
        return api(original);
      } catch {
        localStorage.removeItem('token');
      }
    }

    return Promise.reject(error);
  }
);

export default api;