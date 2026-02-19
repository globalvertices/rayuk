import type { ReviewSummary as ReviewSummaryType } from '../../types/review'
import StarRating from '../ui/StarRating'

const categoryLabels: Record<string, string> = {
  avg_plumbing: 'Plumbing',
  avg_electricity: 'Electricity',
  avg_water: 'Water',
  avg_hvac: 'HVAC',
  avg_it_cabling: 'IT Cabling',
  avg_amenity_stove: 'Stove',
  avg_amenity_washer: 'Washer',
  avg_amenity_fridge: 'Fridge',
  avg_infra_water_tank: 'Water Tank',
  avg_infra_irrigation: 'Irrigation',
  avg_health_dust: 'Dust',
  avg_health_breathing: 'Air Quality',
  avg_health_sewage: 'Sewage',
}

export default function ReviewSummary({ summary }: { summary: ReviewSummaryType }) {
  return (
    <div className="bg-white rounded-lg border border-gray-200 p-5">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold">Review Summary</h3>
        <span className="text-sm text-gray-500">
          {summary.review_count} review{summary.review_count !== 1 ? 's' : ''}
        </span>
      </div>

      <div className="flex items-center gap-3 mb-4">
        <span className="text-3xl font-bold text-gray-900">
          {summary.avg_overall.toFixed(1)}
        </span>
        <StarRating rating={summary.avg_overall} size="lg" />
      </div>

      <div className="grid grid-cols-2 gap-3">
        {Object.entries(categoryLabels).map(([key, label]) => {
          const value = summary[key as keyof ReviewSummaryType] as number | undefined
          if (!value) return null
          return (
            <div key={key} className="flex items-center justify-between">
              <span className="text-sm text-gray-600">{label}</span>
              <div className="flex items-center gap-1">
                <div className="w-16 h-2 bg-gray-200 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-blue-500 rounded-full"
                    style={{ width: `${(value / 5) * 100}%` }}
                  />
                </div>
                <span className="text-xs text-gray-500 w-6 text-right">{value.toFixed(1)}</span>
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}
