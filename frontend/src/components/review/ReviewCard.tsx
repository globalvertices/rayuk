import type { PropertyReview } from '../../types/review'
import StarRating from '../ui/StarRating'

interface ReviewCardProps {
  review: PropertyReview
  /** When true, shows only excerpt + overall rating (snippet view) */
  snippetOnly?: boolean
}

export default function ReviewCard({ review, snippetOnly }: ReviewCardProps) {
  const isVerified = review.verification_status === 'verified'

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-5">
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <StarRating rating={review.overall_rating} size="sm" />
          {isVerified && (
            <span className="text-xs bg-green-100 text-green-700 px-2 py-0.5 rounded-full font-medium">
              Verified Tenant
            </span>
          )}
        </div>
        <span className="text-xs text-gray-400">
          {new Date(review.created_at).toLocaleDateString()}
        </span>
      </div>

      {snippetOnly ? (
        review.public_excerpt && (
          <p className="text-gray-500 text-sm italic">{review.public_excerpt}</p>
        )
      ) : (
        <>
          {review.review_text && (
            <p className="text-gray-700 text-sm mb-3">{review.review_text}</p>
          )}

          <div className="grid grid-cols-2 sm:grid-cols-3 gap-2 text-xs">
            {review.rating_plumbing && <RatingBadge label="Plumbing" value={review.rating_plumbing} />}
            {review.rating_electricity && <RatingBadge label="Electricity" value={review.rating_electricity} />}
            {review.rating_water && <RatingBadge label="Water" value={review.rating_water} />}
            {review.rating_hvac && <RatingBadge label="HVAC" value={review.rating_hvac} />}
            {review.rating_it_cabling && <RatingBadge label="IT Cabling" value={review.rating_it_cabling} />}
            {review.rating_amenity_stove && <RatingBadge label="Stove" value={review.rating_amenity_stove} />}
            {review.rating_amenity_washer && <RatingBadge label="Washer" value={review.rating_amenity_washer} />}
            {review.rating_amenity_fridge && <RatingBadge label="Fridge" value={review.rating_amenity_fridge} />}
            {review.rating_infra_water_tank && <RatingBadge label="Water Tank" value={review.rating_infra_water_tank} />}
            {review.rating_infra_irrigation && <RatingBadge label="Irrigation" value={review.rating_infra_irrigation} />}
            {review.rating_health_dust && <RatingBadge label="Dust" value={review.rating_health_dust} />}
            {review.rating_health_breathing && <RatingBadge label="Air Quality" value={review.rating_health_breathing} />}
            {review.rating_health_sewage && <RatingBadge label="Sewage" value={review.rating_health_sewage} />}
          </div>

          {review.photos && review.photos.length > 0 && (
            <div className="mt-3 flex gap-2 overflow-x-auto">
              {review.photos.map((photo) => (
                <img
                  key={photo.id}
                  src={photo.file_url}
                  alt="Review photo"
                  className="w-20 h-20 object-cover rounded-lg"
                />
              ))}
            </div>
          )}
        </>
      )}
    </div>
  )
}

function RatingBadge({ label, value }: { label: string; value: number }) {
  const color =
    value >= 4 ? 'bg-green-50 text-green-700' :
    value >= 3 ? 'bg-yellow-50 text-yellow-700' :
    'bg-red-50 text-red-700'

  return (
    <span className={`px-2 py-1 rounded ${color}`}>
      {label}: {value}/5
    </span>
  )
}
