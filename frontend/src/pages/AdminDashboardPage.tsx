import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import client from '../api/client'
import Spinner from '../components/ui/Spinner'

export default function AdminDashboardPage() {
  const queryClient = useQueryClient()

  const { data: stats, isLoading: loadingStats } = useQuery({
    queryKey: ['adminStats'],
    queryFn: () => client.get('/admin/stats').then((r) => r.data),
  })

  const { data: pendingVerifications } = useQuery({
    queryKey: ['pendingVerifications'],
    queryFn: () => client.get('/admin/verifications?status=pending').then((r) => r.data),
  })

  const { data: openDisputes } = useQuery({
    queryKey: ['openDisputes'],
    queryFn: () => client.get('/admin/disputes?status=open').then((r) => r.data),
  })

  const verifyMutation = useMutation({
    mutationFn: ({ id, status, notes }: { id: string; status: string; notes?: string }) =>
      client.patch(`/admin/verifications/${id}`, { status, admin_notes: notes }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['pendingVerifications'] })
      queryClient.invalidateQueries({ queryKey: ['adminStats'] })
    },
  })

  const disputeMutation = useMutation({
    mutationFn: ({ id, status, notes }: { id: string; status: string; notes?: string }) =>
      client.patch(`/admin/disputes/${id}`, { status, admin_notes: notes }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['openDisputes'] })
      queryClient.invalidateQueries({ queryKey: ['adminStats'] })
    },
  })

  if (loadingStats) return <Spinner />

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <h1 className="text-2xl font-bold mb-6">Admin Dashboard</h1>

      {/* Stats Grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
        {[
          { label: 'Users', value: stats?.total_users },
          { label: 'Properties', value: stats?.total_properties },
          { label: 'Reviews', value: stats?.total_reviews },
          { label: 'Pending Verifications', value: stats?.pending_verifications },
        ].map((stat) => (
          <div key={stat.label} className="bg-white rounded-lg border border-gray-200 p-4 text-center">
            <p className="text-2xl font-bold text-gray-900">{stat.value ?? '—'}</p>
            <p className="text-sm text-gray-500">{stat.label}</p>
          </div>
        ))}
      </div>

      {/* Pending Verifications */}
      <h2 className="text-lg font-semibold mb-3">Pending Verifications</h2>
      <div className="space-y-3 mb-8">
        {pendingVerifications?.length ? (
          pendingVerifications.map((v: { id: string; document_type: string; file_url: string; created_at: string }) => (
            <div key={v.id} className="bg-white rounded-lg border border-gray-200 p-4 flex items-center justify-between">
              <div>
                <p className="text-sm font-medium capitalize">{v.document_type}</p>
                <a href={v.file_url} target="_blank" rel="noopener noreferrer" className="text-xs text-blue-600 hover:underline">
                  View Document
                </a>
                <p className="text-xs text-gray-400 mt-1">{new Date(v.created_at).toLocaleDateString()}</p>
              </div>
              <div className="flex gap-2">
                <button
                  onClick={() => verifyMutation.mutate({ id: v.id, status: 'approved' })}
                  className="bg-green-600 text-white text-sm px-3 py-1 rounded-lg hover:bg-green-700"
                >
                  Approve
                </button>
                <button
                  onClick={() => verifyMutation.mutate({ id: v.id, status: 'rejected', notes: 'Insufficient documentation' })}
                  className="bg-red-100 text-red-600 text-sm px-3 py-1 rounded-lg hover:bg-red-200"
                >
                  Reject
                </button>
              </div>
            </div>
          ))
        ) : (
          <p className="text-gray-500 text-sm">No pending verifications.</p>
        )}
      </div>

      {/* Open Disputes */}
      <h2 className="text-lg font-semibold mb-3">Open Disputes</h2>
      <div className="space-y-3">
        {openDisputes?.length ? (
          openDisputes.map((d: { id: string; review_type: string; reason: string; created_at: string }) => (
            <div key={d.id} className="bg-white rounded-lg border border-gray-200 p-4">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium capitalize">{d.review_type} Review Dispute</span>
                <span className="text-xs text-gray-400">{new Date(d.created_at).toLocaleDateString()}</span>
              </div>
              <p className="text-sm text-gray-600 mb-3">{d.reason}</p>
              <div className="flex gap-2">
                <button
                  onClick={() => disputeMutation.mutate({ id: d.id, status: 'resolved_kept', notes: 'Review is accurate.' })}
                  className="text-sm border border-gray-300 px-3 py-1 rounded-lg hover:bg-gray-50"
                >
                  Keep Review
                </button>
                <button
                  onClick={() => disputeMutation.mutate({ id: d.id, status: 'resolved_removed', notes: 'Review removed after investigation.' })}
                  className="text-sm bg-red-600 text-white px-3 py-1 rounded-lg hover:bg-red-700"
                >
                  Remove Review
                </button>
              </div>
            </div>
          ))
        ) : (
          <p className="text-gray-500 text-sm">No open disputes.</p>
        )}
      </div>
    </div>
  )
}
