import client from './client'
import type { PropertyReview, LandlordReview, ReviewSummary } from '../types/review'
import type { PaginatedResponse } from '../types/api'

export const reviewsApi = {
  createPropertyReview: (data: Record<string, unknown>) =>
    client.post<PropertyReview>('/reviews/property', data),

  createLandlordReview: (data: Record<string, unknown>) =>
    client.post<LandlordReview>('/reviews/landlord', data),

  getPropertyReviewSummary: (propertyId: string) =>
    client.get<ReviewSummary>(`/reviews/property/${propertyId}/summary`),

  getPropertyReviews: (propertyId: string, params?: Record<string, string | number>) =>
    client.get<PaginatedResponse<PropertyReview>>(`/reviews/property/${propertyId}`, { params }),

  getLandlordReviews: (landlordId: string, params?: Record<string, string | number>) =>
    client.get<PaginatedResponse<LandlordReview>>(`/reviews/landlord/${landlordId}`, { params }),

  getMyReviews: () =>
    client.get<{ property_reviews: PropertyReview[]; landlord_reviews: LandlordReview[] }>('/reviews/my'),

  updatePropertyReview: (id: string, data: Record<string, unknown>) =>
    client.patch<PropertyReview>(`/reviews/property/${id}`, data),

  deletePropertyReview: (id: string) =>
    client.delete(`/reviews/property/${id}`),
}
