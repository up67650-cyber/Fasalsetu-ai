const API_BASE_URL = (
  import.meta.env.VITE_API_BASE_URL || 'https://fasalsetu-ai.onrender.com'
).replace(/\/+$/, '')

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE_URL}${path}`, options)
  const payload = await response.json().catch(() => ({}))
  if (!response.ok) {
    throw new Error(payload.detail || `Request failed (${response.status})`)
  }
  return payload
}

export const api = {
  weather: (lat, lon, language = 'en') => request(`/api/weather?latitude=${lat}&longitude=${lon}&language=${language}`),
  weatherLocation: () => request('/api/weather/location'),
  saveWeatherLocation: (location) => request('/api/weather/location', {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(location)
  }),
  locations: (name) => request(`/api/locations?name=${encodeURIComponent(name)}`),
  farm: () => request('/api/farm'),
  saveFarm: (farm) => request('/api/farm', {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(farm)
  }),
  history: () => request('/api/history'),
  dashboardSummary: () => request('/api/dashboard/summary'),
  farmCrops: () => request('/api/farm/crops'),
  addFarmCrop: (crop) => request('/api/farm/crops', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(crop)
  }),
  updateFarmCrop: (id, crop) => request(`/api/farm/crops/${id}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(crop)
  }),
  deleteFarmCrop: (id) => request(`/api/farm/crops/${id}`, { method: 'DELETE' }),
  addFarmActivity: (activity) => request('/api/farm/activities', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(activity)
  }),
  advisory: (input) => request('/api/advisory', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(input)
  }),
  ask: (question, language) => request('/api/assistant', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ question, language })
  }),
  assistantStatus: () => request('/api/assistant/status'),
  cropDiagnosisStatus: () => request('/api/crop-diagnosis/status'),
  analyzeCrop: (file, language = 'en') => {
    const body = new FormData()
    body.append('image', file)
    return request(`/api/crop-diagnosis?language=${language}`, { method: 'POST', body })
  }
}
