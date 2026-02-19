import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { propertiesApi } from '../api/properties'
import PropertyCard from '../components/property/PropertyCard'
import Spinner from '../components/ui/Spinner'
import type { Property } from '../types/property'

export default function PropertySearchPage() {
  const [search, setSearch] = useState('')
  const [community, setCommunity] = useState('')
  const [propertyType, setPropertyType] = useState('')
  const [bedrooms, setBedrooms] = useState('')
  const [page, setPage] = useState(1)

  const params: Record<string, string | number | undefined> = {
    page,
    page_size: 20,
    ...(search && { q: search }),
    ...(community && { community }),
    ...(propertyType && { property_type: propertyType }),
    ...(bedrooms && { bedrooms: Number(bedrooms) }),
  }

  const { data, isLoading } = useQuery({
    queryKey: ['properties', params],
    queryFn: () => propertiesApi.search(params).then((r) => r.data),
  })

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <h1 className="text-2xl font-bold mb-6">Search Properties</h1>

      {/* Filters */}
      <div className="bg-white rounded-lg border border-gray-200 p-4 mb-6">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-3">
          <input
            type="text"
            placeholder="Search by community, building..."
            value={search}
            onChange={(e) => { setSearch(e.target.value); setPage(1) }}
            className="border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <input
            type="text"
            placeholder="Community"
            value={community}
            onChange={(e) => { setCommunity(e.target.value); setPage(1) }}
            className="border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <select
            value={propertyType}
            onChange={(e) => { setPropertyType(e.target.value); setPage(1) }}
            className="border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="">All Types</option>
            <option value="apartment">Apartment</option>
            <option value="villa">Villa</option>
            <option value="townhouse">Townhouse</option>
            <option value="studio">Studio</option>
            <option value="penthouse">Penthouse</option>
          </select>
          <select
            value={bedrooms}
            onChange={(e) => { setBedrooms(e.target.value); setPage(1) }}
            className="border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="">Any Bedrooms</option>
            {[0, 1, 2, 3, 4, 5, 6].map((n) => (
              <option key={n} value={n}>{n === 0 ? 'Studio' : `${n} BR`}</option>
            ))}
          </select>
        </div>
      </div>

      {/* Results */}
      {isLoading ? (
        <Spinner />
      ) : data?.items.length ? (
        <>
          <p className="text-sm text-gray-500 mb-4">{data.total} properties found</p>
          <div className="grid gap-3">
            {data.items.map((property: Property) => (
              <PropertyCard key={property.id} property={property} />
            ))}
          </div>

          {/* Pagination */}
          {data.total_pages > 1 && (
            <div className="flex justify-center gap-2 mt-6">
              <button
                onClick={() => setPage((p) => Math.max(1, p - 1))}
                disabled={page === 1}
                className="px-4 py-2 border border-gray-300 rounded-lg disabled:opacity-50 hover:bg-gray-50"
              >
                Previous
              </button>
              <span className="px-4 py-2 text-sm text-gray-600">
                Page {page} of {data.total_pages}
              </span>
              <button
                onClick={() => setPage((p) => Math.min(data.total_pages, p + 1))}
                disabled={page === data.total_pages}
                className="px-4 py-2 border border-gray-300 rounded-lg disabled:opacity-50 hover:bg-gray-50"
              >
                Next
              </button>
            </div>
          )}
        </>
      ) : (
        <div className="text-center py-12 text-gray-500">
          <p className="text-lg font-medium">No properties found</p>
          <p className="text-sm mt-1">Try adjusting your search filters</p>
        </div>
      )}
    </div>
  )
}
