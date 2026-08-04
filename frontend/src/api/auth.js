import http from './http'

export const loginRequest = (credentials, config = {}) => http.post('/auth/login', credentials, config)
export const createAdminRequest = (payload) => http.post('/auth/crear-admin', payload)
