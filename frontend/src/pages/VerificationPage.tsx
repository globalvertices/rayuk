import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import client from '../api/client'
import Spinner from '../components/ui/Spinner'

interface TenancyRecord {
  id: string
  property_id: string
  move_in_date: string
  move_out_date?: string
  verification_status: string
  created_at: string
}

interface VerificationDocument {
  id: string
  tenancy_record_id: string
  document_type: string
  file_url: string
  status: string
  created_at: string
}

export default function VerificationPage() {
  const [propertyId, setPropertyId] = useState('')
  const [moveIn, setMoveIn] = useState('')
  const [moveOut, setMoveOut] = useState('')
  const [file, setFile] = useState<File | null>(null)
  const [docType, setDocType] = useState('tenancy_contract')
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')

  const { data: records, isLoading, refetch } = useQuery({
    queryKey: ['myVerifications'],
    queryFn: () => client.get<{ tenancy_records: TenancyRecord[]; documents: VerificationDocument[] }>('/verifications/my').then(r => r.data),
  })

  const handleSubmitTenancy = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setSuccess('')
    setSubmitting(true)
    try {
      await client.post('/verifications/tenancy', {
        property_id: propertyId,
        move_in_date: moveIn,
        move_out_date: moveOut || undefined,
      })
      setSuccess('Tenancy record submitted! Now upload your verification document.')
      setPropertyId('')
      setMoveIn('')
      setMoveOut('')
      refetch()
    } catch (err: unknown) {
      const msg = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail
      setError(msg || 'Failed to submit tenancy record.')
    } finally {
      setSubmitting(false)
    }
  }

  const handleUploadDoc = async (tenancyRecordId: string) => {
    if (!file) return
    const formData = new FormData()
    formData.append('file', file)
    formData.append('tenancy_record_id', tenancyRecordId)
    formData.append('document_type', docType)
    try {
      await client.post('/verifications/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })
      setFile(null)
      refetch()
    } catch {
      alert('Failed to upload document')
    }
  }

  if (isLoading) return <Spinner />

  const statusColor = (s: string) =>
    s === 'approved' ? 'text-green-600 bg-green-50' :
    s === 'rejected' ? 'text-red-600 bg-red-50' :
    'text-yellow-600 bg-yellow-50'

  return (
    <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <h1 className="text-2xl font-bold mb-6">Verification</h1>

      {/* Submit Tenancy */}
      <form onSubmit={handleSubmitTenancy} className="bg-white rounded-lg border border-gray-200 p-6 space-y-4 mb-6">
        <h2 className="font-semibold">Add Tenancy Record</h2>
        {error && <div className="bg-red-50 text-red-600 text-sm p-3 rounded-lg">{error}</div>}
        {success && <div className="bg-green-50 text-green-600 text-sm p-3 rounded-lg">{success}</div>}

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Property ID</label>
          <input type="text" value={propertyId} onChange={(e) => setPropertyId(e.target.value)} required
            placeholder="Enter the property ID"
            className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500" />
        </div>
        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Move-in Date</label>
            <input type="date" value={moveIn} onChange={(e) => setMoveIn(e.target.value)} required
              className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500" />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Move-out Date</label>
            <input type="date" value={moveOut} onChange={(e) => setMoveOut(e.target.value)}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500" />
          </div>
        </div>
        <button type="submit" disabled={submitting}
          className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50 font-medium">
          {submitting ? 'Submitting...' : 'Submit Tenancy'}
        </button>
      </form>

      {/* My Records */}
      <h2 className="text-lg font-semibold mb-3">My Tenancy Records</h2>
      {records?.tenancy_records.length ? (
        <div className="space-y-3">
          {records.tenancy_records.map((rec) => (
            <div key={rec.id} className="bg-white rounded-lg border border-gray-200 p-4">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-mono text-gray-500">{rec.property_id}</span>
                <span className={`text-xs px-2 py-0.5 rounded-full capitalize font-medium ${statusColor(rec.verification_status)}`}>
                  {rec.verification_status}
                </span>
              </div>
              <p className="text-sm text-gray-600">
                {rec.move_in_date} — {rec.move_out_date || 'present'}
              </p>
              {rec.verification_status === 'pending' && (
                <div className="mt-3 space-y-2">
                  <select value={docType} onChange={(e) => setDocType(e.target.value)}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500">
                    <option value="tenancy_contract">Tenancy Contract</option>
                    <option value="lease_agreement">Lease Agreement</option>
                    <option value="utility_bill">Utility Bill</option>
                    <option value="bank_statement">Bank Statement</option>
                    <option value="title_deed">Title Deed</option>
                    <option value="management_agreement">Management Agreement</option>
                    <option value="other">Other</option>
                  </select>
                  <div className="flex items-center gap-2">
                    <input type="file" onChange={(e) => setFile(e.target.files?.[0] || null)}
                      className="text-sm" />
                    <button onClick={() => handleUploadDoc(rec.id)} disabled={!file}
                      className="text-sm bg-gray-100 px-3 py-1 rounded-lg hover:bg-gray-200 disabled:opacity-50">
                      Upload Proof
                    </button>
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      ) : (
        <p className="text-gray-500 text-sm">No tenancy records yet.</p>
      )}
    </div>
  )
}
