import { useQuery } from '@tanstack/react-query'
import { reviewsApi } from '../api/reviews'
import ReviewCard from '../components/review/ReviewCard'
import Spinner from '../components/ui/Spinner'

export default function MyReviewsPage() {
  const { data, isLoading } = useQuery({
    queryKey: ['myReviews'],
    queryFn: () => reviewsApi.getMyReviews().then((r) => r.data),
  })

  if (isLoading) return <Spinner />

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <h1 className="text-2xl font-bold mb-6">My Reviews</h1>

      {data?.property_reviews.length ? (
        <div>
          <h2 className="text-lg font-semibold mb-3">Property Reviews</h2>
          <div className="space-y-3 mb-8">
            {data.property_reviews.map((review) => (
              <ReviewCard key={review.id} review={review} />
            ))}
          </div>
        </div>
      ) : null}

      {data?.landlord_reviews.length ? (
        <div>
          <h2 className="text-lg font-semibold mb-3">Landlord Reviews</h2>
          <div className="space-y-3">
            {data.landlord_reviews.map((review) => (
              <div key={review.id} className="bg-white rounded-lg border border-gray-200 p-5">
                <p className="text-sm text-gray-700">{review.review_text}</p>
                <div className="mt-2 text-xs text-gray-400">
                  {new Date(review.created_at).toLocaleDateString()}
                </div>
              </div>
            ))}
          </div>
        </div>
      ) : null}

      {!data?.property_reviews.length && !data?.landlord_reviews.length && (
        <div className="text-center py-12 text-gray-500">
          <p className="text-lg font-medium">No reviews yet</p>
          <p className="text-sm mt-1">Search for a property to write your first review.</p>
        </div>
      )}
    </div>
  )
}
