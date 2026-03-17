const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000/api'
const AUTH_TOKEN_KEY = 'skill_gap_auth_token'

export function getAuthToken() {
  return localStorage.getItem(AUTH_TOKEN_KEY)
}

export function setAuthToken(token) {
  if (token) {
    localStorage.setItem(AUTH_TOKEN_KEY, token)
    return
  }
  localStorage.removeItem(AUTH_TOKEN_KEY)
}

async function request(path, options = {}) {
  const token = getAuthToken()
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...(options.headers || {}),
    },
    ...options,
  })

  if (!response.ok) {
    const payload = await response.json().catch(() => ({}))
    throw new Error(payload.error || 'Request failed')
  }

  return response.json()
}

export function registerUser(payload) {
  return request('/auth/register', {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}

export function loginUser(payload) {
  return request('/auth/login', {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}

export function fetchCurrentUser() {
  return request('/auth/me')
}

export function fetchRoleTrends() {
  return request('/trends/roles')
}

export function fetchSkillTrends() {
  return request('/trends/skills')
}

export function fetchRecommendation(payload) {
  return request('/recommend', {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}

export function fetchAssessmentQuestions(payload) {
  return request('/assessment/questions', {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}

export function submitAssessment(payload) {
  return request('/assessment/submit', {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}

export function getPowerBIExportUrl(datasetName) {
  const token = getAuthToken()
  const query = token ? `?token=${encodeURIComponent(token)}` : ''
  return `${API_BASE_URL}/export/${datasetName}${query}`
}
