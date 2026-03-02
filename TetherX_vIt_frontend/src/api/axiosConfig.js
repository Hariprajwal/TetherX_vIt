// src/api/axiosConfig.js
import axios from 'axios';

const API = axios.create({
  baseURL: 'https://tetherx-vit.onrender.com/',
  headers: { 'Content-Type': 'application/json' },
});

// Attach JWT token to every request
API.interceptors.request.use((config) => {
  const stored = localStorage.getItem('tokens');
  if (stored) {
    const { access } = JSON.parse(stored);
    if (access) {
      config.headers.Authorization = `Bearer ${access}`;
    }
  }
  return config;
});

// Auto-refresh expired tokens
API.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      const stored = localStorage.getItem('tokens');
      if (stored) {
        const { refresh } = JSON.parse(stored);
        if (refresh) {
          try {
            const res = await axios.post('http://localhost:8000/api/auth/refresh/', { refresh });
            const newTokens = { access: res.data.access, refresh };
            localStorage.setItem('tokens', JSON.stringify(newTokens));
            originalRequest.headers.Authorization = `Bearer ${res.data.access}`;
            return API(originalRequest);
          } catch {
            localStorage.removeItem('tokens');
            window.location.href = '/login';
          }
        }
      }
    }
    return Promise.reject(error);
  }
);

export default API;
