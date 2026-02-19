import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import client from '../api/client'
import Spinner from '../components/ui/Spinner'

interface Dispute {
  id: string
  review_type: string
  review_id: string
  reason: string
  status: string
  admin_notes?: string
  created_at: string
}

export default function LandlordDashboardPage() {
  const queryClient = useQueryClient()

  const { data: disputes, isLoading } = useQuery({
    queryKey: ['myDisputes'],
    queryFn: () => client.get<Dispute[]>('/disputes/my').then((r) => r.data),
  })

  const disputeMutation = useMutation({
    mutationFn: (data: { review_type: string; review_id: string; reason: string }) =>
      client.post('/disputes', data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['myDisputes'] }),
  })

  if (isLoading) return <Spinner />

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <h1 className="text-2xl font-bold mb-6">Landlord Dashboard</h1>

      {/* Quick Actions */}
      <div className="grid md:grid-cols-2 gap-4 mb-8">
        <div className="bg-white rounded-lg border border-gray-200 p-5">
          <h3 className="font-semibold mb-2">Claim a Property</h3>
          <p className="text-sm text-gray-500 mb-3">
            Claim ownership of a property to respond to reviews and manage disputes.
          </p>
          <a href="/properties" className="text-blue-600 hover:underline text-sm">
            Search Properties
          </a>
        </div>
        <div className="bg-white rounded-lg border border-gray-200 p-5">
          <h3 className="font-semibold mb-2">My Verifications</h3>
          <p className="text-sm text-gray-500 mb-3">
            View your ownership claims and verification status.
          </p>
          <a href="/verification" className="text-blue-600 hover:underline text-sm">
            View Verifications
          </a>
        </div>
      </div>

      {/* Disputes */}
      <h2 className="text-lg font-semibold mb-3">My Disputes</h2>
      {disputes?.length ? (
        <div className="space-y-3">
          {disputes.map((dispute) => (
            <div key={dispute.id} className="bg-white rounded-lg border border-gray-200 p-4">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium capitalize">{dispute.review_type} Review Dispute</span>
                <span className={`text-xs px-2 py-0.5 rounded-full capitalize font-medium ${
                  dispute.status === 'resolved_kept' ? 'bg-gray-100 text-gray-600' :
                  dispute.status === 'resolved_removed' ? 'bg-green-50 text-green-600' :
                  'bg-yellow-50 text-yellow-600'
                }`}>
                  {dispute.status.replace('_', ' ')}
                </span>
              </div>
              <p className="text-sm text-gray-600">{dispute.reason}</p>
              {dispute.admin_notes && (
                <p className="text-sm text-gray-400 mt-2 italic">Admin: {dispute.admin_notes}</p>
              )}
              <p className="text-xs text-gray-400 mt-2">{new Date(dispute.created_at).toLocaleDateString()}</p>
            </div>
          ))}
        </div>
      ) : (
        <p className="text-gray-500 text-sm">No disputes filed yet.</p>
      )}

      {/* File Dispute (simplified inline form) */}
      <div className="mt-8 bg-white rounded-lg border border-gray-200 p-6">
        <h2 className="font-semibold mb-3">File a New Dispute</h2>
        <form
          onSubmit={(e) => {
            e.preventDefault()
            const form = e.target as HTMLFormElement
            const data = new FormData(form)
            disputeMutation.mutate({
              review_type: data.get('review_type') as string,
              review_id: data.get('review_id') as string,
              reason: data.get('reason') as string,
            })
            form.reset()
          }}
          className="space-y-3"
        >
          <div className="grid grid-cols-2 gap-3">
            <select name="review_type" required
              className="border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500">
              <option value="property">Property Review</option>
              <option value="landlord">Landlord Review</option>
            </select>
            <input name="review_id" placeholder="Review ID" required
              className="border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500" />
          </div>
          <textarea name="reason" placeholder="Explain why this review is inaccurate..." required rows={3}
            className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500" />
          <button type="submit"
            className="bg-red-600 text-white px-6 py-2 rounded-lg hover:bg-red-700 font-medium text-sm">
            File Dispute
          </button>
        </form>
      </div>
    </div>
  )
}
