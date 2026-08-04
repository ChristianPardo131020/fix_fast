import http from './http'

// El login/logout ahora se hacen directo contra Supabase Auth (ver
// stores/auth.js). Este endpoint del backend solo devuelve el perfil de
// negocio del usuario ya autenticado.
export const meRequest = () => http.get('/auth/me')
