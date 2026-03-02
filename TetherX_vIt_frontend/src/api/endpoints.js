// src/api/endpoints.js
import api from './axiosConfig';

// ─── AUTH ───
export const authAPI = {
    register: (data) => api.post('/api/auth/register/', data),
    verify: (data) => api.post('/api/auth/verify/', data),
    resendOTP: (data) => api.post('/api/auth/resend-otp/', data),
    login: (data) => api.post('/api/auth/login/', data),
    refresh: (data) => api.post('/api/auth/refresh/', data),
    me: () => api.get('/api/auth/me/'),
    changePassword: (data) => api.post('/api/auth/change-password/', data),
    deleteAccount: (data) => api.post('/api/auth/delete-account/', data),
    checkUsername: (username) => api.get(`/api/auth/check-username/?username=${username}`),
    checkEmail: (email) => api.get(`/api/auth/check-email/?email=${email}`),
};

// ─── CRUD ───
export const accessLogsAPI = {
    list: () => api.get('/api/access-logs/'),
    create: (data) => api.post('/api/access-logs/', data),
    delete: (id) => api.delete(`/api/access-logs/${id}/`),
};

export const auditLogsAPI = {
    list: () => api.get('/api/audit-logs/'),
    create: (data) => api.post('/api/audit-logs/', data),
};

export const abacPoliciesAPI = {
    list: () => api.get('/api/abac-policies/'),
    create: (data) => api.post('/api/abac-policies/', data),
    patch: (id, data) => api.patch(`/api/abac-policies/${id}/`, data),
    delete: (id) => api.delete(`/api/abac-policies/${id}/`),
};

export const roleAdaptationsAPI = {
    list: () => api.get('/api/role-adaptations/'),
};

// ─── AI ───
export const aiAPI = {
    adaptRole: (data) => api.post('/api/adapt-role/', data),
    detectAnomaly: (data) => api.post('/api/anomaly-detect/', data),
    blockchainVerify: () => api.get('/api/blockchain-verify/'),
    blockchainPost: () => api.post('/api/blockchain-verify/'),
};
