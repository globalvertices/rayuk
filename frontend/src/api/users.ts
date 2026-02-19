import client from './client'
import type { User, UserPublic } from '../types/user'

export const usersApi = {
  getMe: () => client.get<User>('/users/me'),
  updateMe: (data: Partial<User>) => client.patch<User>('/users/me', data),
  updateContactable: (is_contactable: boolean) =>
    client.patch<User>('/users/me/contactable', { is_contactable }),
  getUser: (id: string) => client.get<UserPublic>(`/users/${id}`),
}
