export interface PropertyReview {
  id: string
  property_id: string
  tenant_id: string
  rating_plumbing: number | null
  rating_electricity: number | null
  rating_water: number | null
  rating_it_cabling: number | null
  rating_hvac: number | null
  rating_amenity_stove: number | null
  rating_amenity_washer: number | null
  rating_amenity_fridge: number | null
  rating_infra_water_tank: number | null
  rating_infra_irrigation: number | null
  rating_health_dust: number | null
  rating_health_breathing: number | null
  rating_health_sewage: number | null
  overall_rating: number
  review_text: string
  public_excerpt: string | null
  status: string
  verification_status: string
  is_flagged: boolean
  published_at: string | null
  created_at: string
  photos: PhotoItem[]
}

/** Snippet returned for unauthenticated / no-unlock users */
export interface PropertyReviewSnippet {
  id: string
  property_id: string
  overall_rating: number
  public_excerpt: string | null
  status: string
  verification_status: string
  created_at: string
}

export interface LandlordReview {
  id: string
  landlord_id: string
  tenant_id: string
  property_id: string
  rating_responsiveness: number | null
  rating_demeanor: number | null
  rating_repair_payments: number | null
  rating_availability: number | null
  rating_payment_flexibility: number | null
  overall_rating: number
  review_text: string
  status: string
  verification_status: string
  is_flagged: boolean
  published_at: string | null
  created_at: string
}

export interface PhotoItem {
  id: string
  file_url: string
  file_name: string
  sort_order: number
}

export interface ReviewSummary {
  property_id: string
  review_count: number
  avg_overall: number
  avg_plumbing: number | null
  avg_electricity: number | null
  avg_water: number | null
  avg_it_cabling: number | null
  avg_hvac: number | null
  avg_amenity_stove: number | null
  avg_amenity_washer: number | null
  avg_amenity_fridge: number | null
  avg_infra_water_tank: number | null
  avg_infra_irrigation: number | null
  avg_health_dust: number | null
  avg_health_breathing: number | null
  avg_health_sewage: number | null
}
