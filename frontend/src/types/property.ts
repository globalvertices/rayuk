export interface Property {
  id: string
  community_id: string
  building_id: string | null
  property_type: 'villa' | 'apartment' | 'townhouse' | 'studio' | 'penthouse'
  unit_number: string | null
  utility_reference: string | null
  bedrooms: number | null
  bathrooms: number | null
  size_sqft: number | null
  year_built: number | null
  address_line: string
  community_name: string | null
  building_name: string | null
  avg_property_rating: number
  avg_landlord_rating: number
  avg_overall_rating: number | null
  review_count: number
  is_active: boolean
  created_at: string
}

export interface PropertyListItem {
  id: string
  property_type: string
  unit_number: string | null
  bedrooms: number | null
  bathrooms: number | null
  size_sqft: number | null
  address_line: string
  avg_property_rating: number
  avg_landlord_rating: number
  review_count: number
  community_name: string | null
  city_name: string | null
}

export interface Community {
  id: string
  name: string
  slug: string
}
