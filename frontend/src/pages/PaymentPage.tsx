import { useQuery, useQueryClient } from '@tanstack/react-query'
import { paymentsApi } from '../api/payments'
import Spinner from '../components/ui/Spinner'
import { useState } from 'react'

export default function PaymentPage() {
  const queryClient = useQueryClient()
  const [topupLoading, setTopupLoading] = useState(false)

  const { data: wallet, isLoading: walletLoading } = useQuery({
    queryKey: ['wallet'],
    queryFn: () => paymentsApi.getWallet().then((r) => r.data),
  })

  const { data: ledger, isLoading: ledgerLoading } = useQuery({
    queryKey: ['ledger'],
    queryFn: () => paymentsApi.getLedger().then((r) => r.data),
  })

  const { data: pricing } = useQuery({
    queryKey: ['pricing'],
    queryFn: () => paymentsApi.getPricing().then((r) => r.data),
  })

  const handleTopup = async (tier: 'small' | 'medium' | 'large') => {
    setTopupLoading(true)
    try {
      const { data } = await paymentsApi.topup(tier)
      window.location.href = data.checkout_url
    } catch {
      alert('Failed to start checkout. Please try again.')
      setTopupLoading(false)
    }
  }

  if (walletLoading || ledgerLoading) return <Spinner />

  const topupOptions = pricing
    ? [
        { tier: 'small' as const, cents: pricing.topup_small_cents, credits: pricing.topup_small_credits },
        { tier: 'medium' as const, cents: pricing.topup_medium_cents, credits: pricing.topup_medium_credits },
        { tier: 'large' as const, cents: pricing.topup_large_cents, credits: pricing.topup_large_credits },
      ]
    : []

  return (
    <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <h1 className="text-2xl font-bold mb-6">Credits Wallet</h1>

      {/* Balance Card */}
      <div className="bg-gradient-to-r from-blue-600 to-blue-700 rounded-xl p-6 text-white mb-8">
        <p className="text-blue-100 text-sm">Current Balance</p>
        <p className="text-4xl font-bold mt-1">{wallet?.balance_credits ?? 0} <span className="text-lg font-normal text-blue-200">credits</span></p>
      </div>

      {/* Top Up Section */}
      <div className="mb-8">
        <h2 className="text-lg font-semibold mb-3">Top Up Credits</h2>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
          {topupOptions.map((opt) => (
            <button
              key={opt.tier}
              onClick={() => handleTopup(opt.tier)}
              disabled={topupLoading}
              className="bg-white border-2 border-gray-200 rounded-lg p-4 hover:border-blue-500 transition-colors disabled:opacity-50 text-left"
            >
              <p className="text-2xl font-bold text-gray-900">{opt.credits}</p>
              <p className="text-sm text-gray-500">credits</p>
              <p className="mt-2 text-blue-600 font-semibold">${(opt.cents / 100).toFixed(2)}</p>
            </button>
          ))}
        </div>
      </div>

      {/* Pricing Info */}
      {pricing && (
        <div className="mb-8 bg-gray-50 rounded-lg p-4">
          <h3 className="font-medium text-gray-900 mb-2">Credit Costs</h3>
          <div className="grid grid-cols-2 gap-2 text-sm">
            <span className="text-gray-500">Summary unlock</span>
            <span className="font-medium">{pricing.unlock_summary} credits</span>
            <span className="text-gray-500">Detailed unlock</span>
            <span className="font-medium">{pricing.unlock_detailed} credits</span>
            <span className="text-gray-500">Full unlock</span>
            <span className="font-medium">{pricing.unlock_full} credits</span>
            <span className="text-gray-500">Contact request</span>
            <span className="font-medium">{pricing.contact_request} credits</span>
          </div>
        </div>
      )}

      {/* Transaction History */}
      <div>
        <h2 className="text-lg font-semibold mb-3">Transaction History</h2>
        {ledger?.length ? (
          <div className="space-y-2">
            {ledger.map((entry) => (
              <div key={entry.id} className="bg-white rounded-lg border border-gray-200 p-4 flex items-center justify-between">
                <div>
                  <p className="font-medium text-gray-900 capitalize">
                    {entry.entry_type} {entry.ref_type ? `- ${entry.ref_type.replace('_', ' ')}` : ''}
                  </p>
                  {entry.description && <p className="text-xs text-gray-500">{entry.description}</p>}
                  <p className="text-xs text-gray-400 mt-0.5">
                    {new Date(entry.created_at).toLocaleString()}
                  </p>
                </div>
                <span className={`font-semibold text-lg ${
                  entry.amount > 0 ? 'text-green-600' : 'text-red-600'
                }`}>
                  {entry.amount > 0 ? '+' : ''}{entry.amount}
                </span>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-8 text-gray-500">
            <p className="text-lg font-medium">No transactions yet</p>
            <p className="text-sm mt-1">Top up credits to get started.</p>
          </div>
        )}
      </div>
    </div>
  )
}
