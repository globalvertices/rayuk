export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  page_size: number
  total_pages: number
}

export interface TokenResponse {
  access_token: string
  refresh_token: string
  token_type: string
}

export interface UnlockCheck {
  has_summary: boolean
  has_detailed: boolean
  has_full: boolean
  highest_tier: string | null
}

export interface WalletInfo {
  user_id: string
  balance_credits: number
}

export interface CreditPricing {
  unlock_summary: number
  unlock_detailed: number
  unlock_full: number
  contact_request: number
  topup_small_cents: number
  topup_small_credits: number
  topup_medium_cents: number
  topup_medium_credits: number
  topup_large_cents: number
  topup_large_credits: number
}

export interface LedgerEntry {
  id: string
  user_id: string
  amount: number
  entry_type: string
  ref_type: string | null
  ref_id: string | null
  description: string | null
  created_at: string
}
