import client from './client'
import type { Property } from '../types/property'
import type { PaginatedResponse } from '../types/api'

export const propertiesApi = {
  search: (params: Record<string, string | number | undefined>) =>
    client.get<PaginatedResponse<Property>>('/properties', { params }),

  get: (id: string) => client.get<Property>(`/properties/${id}`),

  create: (data: Record<string, unknown>) =>
    client.post<Property>('/properties', data),

  update: (id: string, data: Record<string, unknown>) =>
    client.patch<Property>(`/properties/${id}`, data),

  claim: (id: string) =>
    client.post(`/properties/${id}/claim`),

  searchCommunities: (q: string) =>
    client.get('/properties/locations/communities/search', { params: { q } }),
}
