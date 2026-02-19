export interface User {
  id: string
  email: string
  first_name: string
  last_name: string
  phone: string | null
  role: 'tenant' | 'landlord' | 'lead' | 'admin'
  auth_provider: string
  avatar_url: string | null
  is_email_verified: boolean
  is_identity_verified: boolean
  is_contactable: boolean
  is_active: boolean
  created_at: string
}

export interface UserPublic {
  id: string
  first_name: string
  last_name: string
  role: string
  avatar_url: string | null
  is_identity_verified: boolean
  created_at: string
}
