import { useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { reviewsApi } from '../api/reviews'
import StarRating from '../components/ui/StarRating'

const categories = [
  { key: 'rating_plumbing', label: 'Plumbing' },
  { key: 'rating_electricity', label: 'Electricity' },
  { key: 'rating_water', label: 'Water Supply' },
  { key: 'rating_hvac', label: 'HVAC / AC' },
  { key: 'rating_it_cabling', label: 'IT Cabling / Internet' },
  { key: 'rating_amenity_stove', label: 'Stove / Cooktop' },
  { key: 'rating_amenity_washer', label: 'Washer / Dryer' },
  { key: 'rating_amenity_fridge', label: 'Fridge' },
  { key: 'rating_infra_water_tank', label: 'Water Tank' },
  { key: 'rating_infra_irrigation', label: 'Irrigation / Garden' },
  { key: 'rating_health_dust', label: 'Dust Levels' },
  { key: 'rating_health_breathing', label: 'Air Quality / Breathing' },
  { key: 'rating_health_sewage', label: 'Sewage / Drainage' },
]

export default function WriteReviewPage() {
  const { id: propertyId } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const [ratings, setRatings] = useState<Record<string, number>>({})
  const [text, setText] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')

    const filledRatings = Object.values(ratings).filter((v) => v > 0)
    if (filledRatings.length < 3) {
      setError('Please rate at least 3 categories.')
      return
    }

    setLoading(true)
    try {
      await reviewsApi.createPropertyReview({
        property_id: propertyId,
        review_text: text || undefined,
        ...ratings,
      })
      navigate(`/properties/${propertyId}`)
    } catch (err: unknown) {
      const msg = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail
      setError(msg || 'Failed to submit review.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <h1 className="text-2xl font-bold mb-6">Write a Review</h1>

      <form onSubmit={handleSubmit} className="space-y-6">
        {error && (
          <div className="bg-red-50 text-red-600 text-sm p-3 rounded-lg">{error}</div>
        )}

        {/* Category Ratings */}
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <h2 className="font-semibold mb-4">Rate the Property</h2>
          <p className="text-sm text-gray-500 mb-4">Rate at least 3 categories. Skip any that don't apply.</p>
          <div className="space-y-4">
            {categories.map(({ key, label }) => (
              <div key={key} className="flex items-center justify-between">
                <span className="text-sm text-gray-700 w-40">{label}</span>
                <StarRating
                  rating={ratings[key] || 0}
                  interactive
                  onChange={(v) => setRatings((r) => ({ ...r, [key]: v }))}
                />
              </div>
            ))}
          </div>
        </div>

        {/* Review Text */}
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <h2 className="font-semibold mb-2">Your Experience</h2>
          <textarea
            value={text}
            onChange={(e) => setText(e.target.value)}
            rows={5}
            placeholder="Share your experience living at this property..."
            className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        <div className="flex justify-end gap-3">
          <button
            type="button"
            onClick={() => navigate(-1)}
            className="px-6 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
          >
            Cancel
          </button>
          <button
            type="submit"
            disabled={loading}
            className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50 font-medium"
          >
            {loading ? 'Submitting...' : 'Submit Review'}
          </button>
        </div>
      </form>
    </div>
  )
}
