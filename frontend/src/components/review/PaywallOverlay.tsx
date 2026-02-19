interface PaywallOverlayProps {
  level: 'summary' | 'detailed' | 'full' | 'contact'
  onUnlock: () => void
  price?: number
  loading?: boolean
}

const messages = {
  summary: {
    title: 'Unlock Review Summary',
    description: 'Read truncated review text and overall ratings.',
  },
  detailed: {
    title: 'Unlock Detailed Reviews',
    description: 'See full review text and all category ratings.',
  },
  full: {
    title: 'Unlock Full Reviews',
    description: 'See everything including photos and evidence.',
  },
  contact: {
    title: 'Contact Ex-Tenant',
    description: 'Send a message to verified ex-tenants of this property.',
  },
}

export default function PaywallOverlay({ level, onUnlock, price, loading }: PaywallOverlayProps) {
  const { title, description } = messages[level]

  return (
    <div className="relative">
      <div className="absolute inset-0 bg-white/80 backdrop-blur-sm z-10 flex items-center justify-center rounded-lg">
        <div className="text-center p-6 max-w-sm">
          <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-3">
            <svg className="w-6 h-6 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
            </svg>
          </div>
          <h3 className="font-semibold text-gray-900 mb-1">{title}</h3>
          <p className="text-sm text-gray-500 mb-4">{description}</p>
          <button
            onClick={onUnlock}
            disabled={loading}
            className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition-colors text-sm font-medium disabled:opacity-50"
          >
            {loading ? 'Processing...' : price != null ? `Unlock for ${price} credits` : 'Unlock'}
          </button>
        </div>
      </div>
    </div>
  )
}
