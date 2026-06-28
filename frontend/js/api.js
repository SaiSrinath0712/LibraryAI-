'use strict';

/**
 * LibraryAI Pro — Frontend API client
 * Connects the UI to the FastAPI backend.
 */

var token = sessionStorage.getItem('token') || null;

const BASE_URL = window.location.protocol === 'file:'
  ? 'http://127.0.0.1:8000'
  : '';

async function api(path, opts = {}) {
  const headers = { 'Content-Type': 'application/json' };
  if (token) {
    headers['Authorization'] = 'Bearer ' + token;
  }

  const response = await fetch(`${BASE_URL}${path}`, {
    cache: 'no-store',
    ...opts,
    headers: { ...headers, ...(opts.headers || {}) },
  });

  if (!response.ok) {
    let errMessage = 'Request failed';
    try {
      const errData = await response.json();
      if (Array.isArray(errData.detail)) {
        errMessage = errData.detail.map(e => `${e.loc.join('.')}: ${e.msg}`).join(' | ');
      } else {
        errMessage = errData.detail || errData.message || errMessage;
      }
    } catch (e) {}

    if (response.status === 401 && typeof logout === 'function') {
      logout();
    }
    throw new Error(errMessage);
  }

  if (response.status === 204) return null;
  return await response.json();
}

const get = (p) => api(p, { method: 'GET' });
const post = (p, d) => api(p, { method: 'POST', body: JSON.stringify(d || {}) });
const put = (p, d) => api(p, { method: 'PUT', body: JSON.stringify(d || {}) });
const del = (p) => api(p, { method: 'DELETE' });

function setToken(newToken) {
  token = newToken;
  if (newToken) {
    sessionStorage.setItem('token', newToken);
  } else {
    sessionStorage.removeItem('token');
  }
}

function clearToken() {
  token = null;
  sessionStorage.removeItem('token');
  sessionStorage.removeItem('user');
}

// ── AUTH ──

async function login(memberId, password) {
  const data = await post('/auth/login', { member_id: memberId, password });
  setToken(data.access_token);
  sessionStorage.setItem('user', JSON.stringify(data.student));
  return data;
}

async function adminLogin(username, password) {
  const data = await post('/auth/login', { username, password });
  setToken(data.access_token);
  sessionStorage.setItem('user', JSON.stringify(data.admin));
  return data;
}

async function register(payload) {
  return post('/auth/register', payload);
}

async function changePassword(payload) {
  return post('/auth/change-password', payload);
}

// ── BOOKS ──

async function getBooks(params = {}) {
  const qs = new URLSearchParams();
  if (params.q) qs.set('q', params.q);
  if (params.genre) qs.set('genre', params.genre);
  if (params.available) qs.set('available', params.available);
  const query = qs.toString();
  return get('/books' + (query ? '?' + query : ''));
}

async function getBook(id) {
  return get('/books/' + id);
}

async function createBook(data) {
  return post('/books', data);
}

async function updateBook(id, data) {
  return put('/books/' + id, data);
}

async function deleteBook(id) {
  return del('/books/' + id);
}

// ── REQUESTS ──

async function requestBook(payload) {
  return post('/requests', payload);
}

async function getRequests(status) {
  return get('/requests' + (status ? '?status=' + status : ''));
}

async function approveRequest(id, payload) {
  return put('/requests/' + id + '/approve', payload);
}

async function rejectRequest(id, payload) {
  return put('/requests/' + id + '/reject', payload);
}

// ── LOANS ──

async function getLoans(params = {}) {
  const qs = new URLSearchParams();
  if (params.status) qs.set('status', params.status);
  if (params.member_id) qs.set('member_id', params.member_id);
  const query = qs.toString();
  return get('/loans' + (query ? '?' + query : ''));
}

async function renewBook(loanId) {
  return post('/loans/' + loanId + '/renew', {});
}

async function returnBook(loanId) {
  return post('/loans/' + loanId + '/return', {});
}

async function issueLoan(payload) {
  return post('/loans/issue', payload);
}

// ── MEMBERS ──

async function getMembers(q) {
  return get('/members' + (q ? '?q=' + encodeURIComponent(q) : ''));
}

async function getMember(id) {
  return get('/members/' + id);
}

// ── NOTIFICATIONS ──

async function getNotifications() {
  return get('/notifications');
}

async function markNotificationRead(id) {
  return put('/notifications/' + id + '/read', {});
}

// ── ANALYTICS & DASHBOARD ──

async function getDashboard() {
  return get('/analytics/dashboard');
}

async function getAnalytics() {
  return get('/analytics');
}

async function getTopBooks() {
  return get('/analytics/top-books');
}

async function getGenreDistribution() {
  return get('/analytics/genre-distribution');
}

// ── REPORTS ──

async function getOverdueReport() {
  return get('/reports/overdue');
}

async function getFinesReport() {
  return get('/reports/fines');
}

async function getMembersReport() {
  return get('/reports/members');
}

// ── SETTINGS ──

async function getSettings() {
  return get('/settings');
}

async function saveSettings(payload) {
  return post('/settings', payload);
}

// ── CHATBOT ──

async function chatbotQuery(query) {
  return post('/chatbot/query', { query });
}
