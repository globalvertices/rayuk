import client from './client'
import type { TokenResponse } from '../types/api'
import type { User } from '../types/user'

export const authApi = {
  register: (data: {
    email: string; password: string; first_name: string;
    last_name: string; role: string; phone?: string
  }) => client.post<User>('/auth/register', data),

  login: (email: string, password: string) =>
    client.post<TokenResponse>('/auth/login', { email, password }),

  refresh: (refresh_token: string) =>
    client.post<TokenResponse>('/auth/refresh', { refresh_token }),

  logout: (refresh_token: string) =>
    client.post('/auth/logout', { refresh_token }),

  verifyEmail: (token: string) =>
    client.get(`/auth/verify-email?token=${token}`),

  forgotPassword: (email: string) =>
    client.post('/auth/forgot-password', { email }),

  resetPassword: (token: string, new_password: string) =>
    client.post('/auth/reset-password', { token, new_password }),
}
