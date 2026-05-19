const API_BASE = (import.meta.env.VITE_API_BASE_URL || '').replace(/\/$/, '');
const BASE = API_BASE ? `${API_BASE}/api` : '/api';

function getToken() {
  return localStorage.getItem('mindbloom_token');
}

async function request(path, options = {}) {
  const token = getToken();
  const headers = { ...(options.headers || {}) };
  if (token) headers['Authorization'] = `Bearer ${token}`;
  if (!(options.body instanceof FormData)) {
    headers['Content-Type'] = 'application/json';
  }
  const res = await fetch(`${BASE}${path}`, { ...options, headers });
  const data = await res.json();
  if (!res.ok) throw { status: res.status, data };
  return data;
}

// Auth
export const authAPI = {
  register: (body) => request('/auth/register', { method: 'POST', body: JSON.stringify(body) }),
  login: (body) => request('/auth/login', { method: 'POST', body: JSON.stringify(body) }),
  getMe: () => request('/auth/me'),
};

// Home
export const homeAPI = {
  getTasks: (day) => request(`/home/tasks${day ? `?day=${encodeURIComponent(day)}` : ''}`),
  addTask: (title, task_type = 'custom', day, note = '') => request(`/home/tasks${day ? `?day=${encodeURIComponent(day)}` : ''}`, { method: 'POST', body: JSON.stringify({ title, task_type, note }) }),
  toggleTask: (id, payload = {}) => request(`/home/tasks/${id}`, { method: 'PUT', body: JSON.stringify(payload) }),
  analyzeDay: (payload) => request('/home/analyze-day', { method: 'POST', body: JSON.stringify(payload) }),
  getQuest: () => request('/home/quest'),
  getSuggestions: () => request('/home/suggestions'),
};

// Journal
export const journalAPI = {
  getOptions: () => request('/journal/options'),
  getPrompts: (type) => request(`/journal/prompts/${type}`),
  getEntries: () => request('/journal/entries'),
  createEntry: (formData) => {
    if (formData instanceof FormData) {
      return request('/journal/entries', { method: 'POST', body: formData });
    }
    return request('/journal/entries', { method: 'POST', body: JSON.stringify(formData) });
  },
};

// Tests
export const testsAPI = {
  list: (search = '') => request(`/tests?search=${encodeURIComponent(search)}`),
  get: (id) => request(`/tests/${id}`),
  submit: (id, answers) => request(`/tests/${id}/submit`, { method: 'POST', body: JSON.stringify({ answers }) }),
  getResults: () => request('/tests/results'),
};

// Growth
export const growthAPI = {
  getAssessment: () => request('/growth/assessment'),
  submitAssessment: (answers) => request('/growth/assessment', { method: 'POST', body: JSON.stringify({ answers }) }),
  getResults: () => request('/growth/results'),
};

// Profile
export const profileAPI = {
  get: () => request('/profile'),
  update: (data) => {
    if (data instanceof FormData) {
      return request('/profile', { method: 'PUT', body: data });
    }
    return request('/profile', { method: 'PUT', body: JSON.stringify(data) });
  },
  changePassword: (current_password, new_password) =>
    request('/profile/change-password', { method: 'POST', body: JSON.stringify({ current_password, new_password }) }),
};

// Admin
export const adminAPI = {
  getAlerts: (params = {}) => {
    const query = new URLSearchParams(params).toString();
    return request(`/admin/alerts${query ? `?${query}` : ''}`);
  },
  getAlert: (id) => request(`/admin/alerts/${id}`),
  getStats: () => request('/admin/alerts/stats'),
  acknowledge: (id, note = '') => request(`/admin/alerts/${id}/acknowledge`, { method: 'POST', body: JSON.stringify({ note }) }),
  resolve: (id, note = '', status = 'resolved') => request(`/admin/alerts/${id}/resolve`, { method: 'POST', body: JSON.stringify({ note, status }) }),
  score: (payload = {}) => request('/admin/alerts/score', { method: 'POST', body: JSON.stringify(payload) }),
  retrain: (payload = {}) => request('/admin/models/retrain', { method: 'POST', body: JSON.stringify(payload) }),
  getModelJob: (jobId, params = {}) => {
    const query = new URLSearchParams(params).toString();
    return request(`/admin/models/jobs/${jobId}${query ? `?${query}` : ''}`);
  },
  listModelJobs: (params = {}) => {
    const query = new URLSearchParams(params).toString();
    return request(`/admin/models/jobs${query ? `?${query}` : ''}`);
  },
};
