import axios from 'axios';

const API_Base = 'http://localhost:8000';

const api = axios.create({
  baseURL: API_Base,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const checkHealth = async () => {
  try {
    const res = await api.get('/');
    return res.data;
  } catch (error) {
    console.error("API Health Check Failed", error);
    return null;
  }
};

export const analyzeDocument = async (file, text, sensitivity = 0.5) => {
  const formData = new FormData();
  if (file) formData.append('file', file);
  if (text) formData.append('text', text);
  formData.append('sensitivity', sensitivity);

  const res = await api.post('/analyze', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  return res.data;
};

export const personalizeRisk = async (clauses, userProfile) => {
  const res = await api.post('/personalize', {
    clauses,
    user_profile: userProfile
  });
  return res.data;
};

export default api;
