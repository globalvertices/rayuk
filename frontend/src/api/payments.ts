import client from './client'
import type { UnlockCheck, WalletInfo, CreditPricing, LedgerEntry } from '../types/api'

export interface TopupCheckoutResponse {
  checkout_url: string
  topup_id: string
}

export interface PurchaseUnlockResponse {
  unlock_id: string
  credits_charged: number
  new_balance: number
}

export interface ContactRequestPaymentResponse {
  contact_request_id: string
  credits_charged: number
  new_balance: number
}

export const paymentsApi = {
  getWallet: () =>
    client.get<WalletInfo>('/payments/wallet'),

  topup: (tier: 'small' | 'medium' | 'large') =>
    client.post<TopupCheckoutResponse>('/payments/topup', { tier }),

  purchaseUnlock: (data: { review_id: string; tier: 'summary' | 'detailed' | 'full' }) =>
    client.post<PurchaseUnlockResponse>('/payments/unlock', data),

  purchaseContactRequest: (data: {
    tenant_id: string
    property_id: string
    review_id?: string
    message?: string
  }) => client.post<ContactRequestPaymentResponse>('/payments/contact-request', data),

  checkUnlock: (reviewId: string) =>
    client.get<UnlockCheck>('/payments/unlocks/check', { params: { review_id: reviewId } }),

  getLedger: () =>
    client.get<LedgerEntry[]>('/payments/ledger'),

  getPricing: () =>
    client.get<CreditPricing>('/payments/pricing'),
}
