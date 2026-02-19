import { Link } from 'react-router-dom'
import type { Property } from '../../types/property'
import StarRating from '../ui/StarRating'

export default function PropertyCard({ property }: { property: Property }) {
  return (
    <Link
      to={`/properties/${property.id}`}
      className="block bg-white rounded-lg border border-gray-200 hover:shadow-md transition-shadow p-4"
    >
      <div className="flex justify-between items-start">
        <div>
          <h3 className="font-semibold text-gray-900">
            {property.community_name}
          </h3>
          {property.building_name && (
            <p className="text-sm text-gray-500">{property.building_name}</p>
          )}
          <div className="mt-1 flex items-center gap-2 text-sm text-gray-500">
            <span className="capitalize">{property.property_type}</span>
            {property.bedrooms !== undefined && (
              <>
                <span>&middot;</span>
                <span>{property.bedrooms} BR</span>
              </>
            )}
          </div>
        </div>
        <div className="text-right">
          {property.avg_overall_rating ? (
            <StarRating rating={property.avg_overall_rating} size="sm" />
          ) : (
            <span className="text-xs text-gray-400">No reviews</span>
          )}
          <p className="text-xs text-gray-400 mt-1">
            {property.review_count} review{property.review_count !== 1 ? 's' : ''}
          </p>
        </div>
      </div>
    </Link>
  )
}
