import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 30000,
})

export const getErrorMessage = (error, fallback = 'Something went wrong. Please try again.') => {
  return error.response?.data?.detail || error.message || fallback
}

export default api
