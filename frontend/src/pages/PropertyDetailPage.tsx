import { useParams, Link } from 'react-router-dom'
import { useQuery, useQueryClient } from '@tanstack/react-query'
import { propertiesApi } from '../api/properties'
import { reviewsApi } from '../api/reviews'
import { paymentsApi } from '../api/payments'
import { useAuthStore } from '../store/authStore'
import ReviewSummary from '../components/review/ReviewSummary'
import ReviewCard from '../components/review/ReviewCard'
import PaywallOverlay from '../components/review/PaywallOverlay'
import Spinner from '../components/ui/Spinner'
import StarRating from '../components/ui/StarRating'
import { useState } from 'react'

export default function PropertyDetailPage() {
  const { id } = useParams<{ id: string }>()
  const { user, isAuthenticated } = useAuthStore()
  const queryClient = useQueryClient()
  const [unlocking, setUnlocking] = useState(false)

  const { data: property, isLoading: loadingProp } = useQuery({
    queryKey: ['property', id],
    queryFn: () => propertiesApi.get(id!).then((r) => r.data),
    enabled: !!id,
  })

  const { data: summary } = useQuery({
    queryKey: ['reviewSummary', id],
    queryFn: () => reviewsApi.getPropertyReviewSummary(id!).then((r) => r.data),
    enabled: !!id,
  })

  const { data: pricing } = useQuery({
    queryKey: ['pricing'],
    queryFn: () => paymentsApi.getPricing().then((r) => r.data),
  })

  const { data: wallet } = useQuery({
    queryKey: ['wallet'],
    queryFn: () => paymentsApi.getWallet().then((r) => r.data),
    enabled: isAuthenticated,
  })

  // Reviews are always fetched - the backend gates content by unlock tier
  const { data: reviewsData } = useQuery({
    queryKey: ['reviews', id],
    queryFn: () => reviewsApi.getPropertyReviews(id!).then((r) => r.data),
    enabled: !!id,
  })

  const handleUnlockReview = async (reviewId: string, tier: 'summary' | 'detailed' | 'full') => {
    setUnlocking(true)
    try {
      await paymentsApi.purchaseUnlock({ review_id: reviewId, tier })
      queryClient.invalidateQueries({ queryKey: ['reviews', id] })
      queryClient.invalidateQueries({ queryKey: ['wallet'] })
    } catch (err: unknown) {
      const msg = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail || 'Failed to unlock. Check your credit balance.'
      alert(msg)
    } finally {
      setUnlocking(false)
    }
  }

  if (loadingProp) return <Spinner />
  if (!property) return <div className="p-8 text-center text-gray-500">Property not found</div>

  // Determine if a review item is a snippet (no review_text field) or full review
  const isSnippet = (item: Record<string, unknown>) => !('review_text' in item)

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Property Header */}
      <div className="bg-white rounded-lg border border-gray-200 p-6 mb-6">
        <div className="flex justify-between items-start">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">{property.community_name}</h1>
            {property.building_name && (
              <p className="text-gray-500">{property.building_name}</p>
            )}
            <div className="mt-2 flex items-center gap-3 text-sm text-gray-500">
              <span className="capitalize">{property.property_type}</span>
              {property.bedrooms !== undefined && (
                <>
                  <span>&middot;</span>
                  <span>{property.bedrooms} Bedrooms</span>
                </>
              )}
            </div>
          </div>
          <div className="text-right">
            {property.avg_overall_rating ? (
              <>
                <StarRating rating={property.avg_overall_rating} size="lg" />
                <p className="text-sm text-gray-500 mt-1">
                  {property.review_count} review{property.review_count !== 1 ? 's' : ''}
                </p>
              </>
            ) : (
              <span className="text-gray-400">No reviews yet</span>
            )}
          </div>
        </div>

        {/* Wallet balance + Action Buttons */}
        <div className="mt-4 flex items-center gap-3">
          {isAuthenticated && wallet && (
            <span className="text-sm text-gray-500 bg-gray-100 px-3 py-1 rounded-full">
              {wallet.balance_credits} credits
            </span>
          )}
          {isAuthenticated && user?.role === 'tenant' && (
            <Link
              to={`/properties/${id}/review`}
              className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 text-sm font-medium"
            >
              Write a Review
            </Link>
          )}
          {isAuthenticated && user?.role === 'landlord' && (
            <button
              onClick={() => propertiesApi.claim(id!)}
              className="border border-gray-300 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-50 text-sm font-medium"
            >
              Claim Property
            </button>
          )}
        </div>
      </div>

      <div className="grid lg:grid-cols-3 gap-6">
        {/* Summary (always visible) */}
        <div className="lg:col-span-1">
          {summary && <ReviewSummary summary={summary} />}
        </div>

        {/* Reviews */}
        <div className="lg:col-span-2">
          <h2 className="text-lg font-semibold mb-4">Reviews</h2>

          {!reviewsData?.items?.length ? (
            <div className="bg-white rounded-lg border border-gray-200 p-8 text-center text-gray-500">
              No reviews yet for this property.
            </div>
          ) : (
            <div className="space-y-4">
              {reviewsData.items.map((item: Record<string, unknown>) => {
                const reviewId = item.id as string
                const snippet = isSnippet(item)

                if (snippet) {
                  // Snippet view - show excerpt + unlock CTA
                  return (
                    <div key={reviewId} className="relative">
                      <div className="bg-white rounded-lg border border-gray-200 p-5">
                        <div className="flex items-center justify-between mb-2">
                          <StarRating rating={item.overall_rating as number} size="sm" />
                          <span className="text-xs text-gray-400">
                            {new Date(item.created_at as string).toLocaleDateString()}
                          </span>
                        </div>
                        {item.public_excerpt && (
                          <p className="text-gray-500 text-sm italic mb-3">{item.public_excerpt as string}</p>
                        )}
                        {isAuthenticated ? (
                          <button
                            onClick={() => handleUnlockReview(reviewId, 'summary')}
                            disabled={unlocking}
                            className="text-blue-600 hover:text-blue-800 text-sm font-medium"
                          >
                            Unlock summary for {pricing?.unlock_summary ?? 5} credits
                          </button>
                        ) : (
                          <Link to="/login" className="text-blue-600 hover:underline text-sm">
                            Sign in to read reviews
                          </Link>
                        )}
                      </div>
                    </div>
                  )
                }

                // Unlocked review - determine tier level from available data
                const hasPhotos = Array.isArray(item.photos) && (item.photos as unknown[]).length > 0
                const hasCategoryRatings = item.rating_plumbing != null || item.rating_electricity != null
                const reviewText = item.review_text as string
                const isTruncated = reviewText?.endsWith('...')

                return (
                  <div key={reviewId}>
                    <ReviewCard review={item as unknown as import('../types/review').PropertyReview} />

                    {/* Upgrade CTAs */}
                    {isTruncated && !hasCategoryRatings && (
                      <div className="mt-2 bg-blue-50 border border-blue-200 rounded-lg p-3 flex items-center justify-between">
                        <span className="text-sm text-blue-700">Upgrade to see full text and all ratings</span>
                        <button
                          onClick={() => handleUnlockReview(reviewId, 'detailed')}
                          disabled={unlocking}
                          className="bg-blue-600 text-white text-sm px-3 py-1 rounded-lg hover:bg-blue-700 disabled:opacity-50"
                        >
                          Upgrade for {pricing?.unlock_detailed ?? 15} credits
                        </button>
                      </div>
                    )}
                    {hasCategoryRatings && !hasPhotos && (
                      <div className="mt-2 bg-blue-50 border border-blue-200 rounded-lg p-3 flex items-center justify-between">
                        <span className="text-sm text-blue-700">Upgrade to see photos and full evidence</span>
                        <button
                          onClick={() => handleUnlockReview(reviewId, 'full')}
                          disabled={unlocking}
                          className="bg-blue-600 text-white text-sm px-3 py-1 rounded-lg hover:bg-blue-700 disabled:opacity-50"
                        >
                          Upgrade for {pricing?.unlock_full ?? 30} credits
                        </button>
                      </div>
                    )}
                  </div>
                )
              })}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
