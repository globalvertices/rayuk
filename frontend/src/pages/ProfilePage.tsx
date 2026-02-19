import { useState, useEffect } from 'react'
import { useAuthStore } from '../store/authStore'
import { usersApi } from '../api/users'

export default function ProfilePage() {
  const { user, setUser } = useAuthStore()
  const [form, setForm] = useState({
    first_name: '', last_name: '', phone: '',
  })
  const [saving, setSaving] = useState(false)
  const [saved, setSaved] = useState(false)

  useEffect(() => {
    if (user) {
      setForm({
        first_name: user.first_name,
        last_name: user.last_name,
        phone: user.phone || '',
      })
    }
  }, [user])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setSaving(true)
    setSaved(false)
    try {
      const { data } = await usersApi.updateMe(form)
      setUser(data)
      setSaved(true)
    } catch {
      alert('Failed to update profile')
    } finally {
      setSaving(false)
    }
  }

  const toggleContactable = async () => {
    try {
      const { data } = await usersApi.updateContactable(!user?.is_contactable)
      setUser(data)
    } catch {
      alert('Failed to update setting')
    }
  }

  if (!user) return null

  return (
    <div className="max-w-2xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <h1 className="text-2xl font-bold mb-6">Profile</h1>

      <form onSubmit={handleSubmit} className="bg-white rounded-lg border border-gray-200 p-6 space-y-4 mb-6">
        {saved && <div className="bg-green-50 text-green-600 text-sm p-3 rounded-lg">Profile updated!</div>}

        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">First Name</label>
            <input type="text" value={form.first_name}
              onChange={(e) => setForm((f) => ({ ...f, first_name: e.target.value }))}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500" />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Last Name</label>
            <input type="text" value={form.last_name}
              onChange={(e) => setForm((f) => ({ ...f, last_name: e.target.value }))}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500" />
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
          <input type="email" value={user.email} disabled
            className="w-full border border-gray-200 bg-gray-50 rounded-lg px-3 py-2 text-gray-500" />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Phone</label>
          <input type="tel" value={form.phone}
            onChange={(e) => setForm((f) => ({ ...f, phone: e.target.value }))}
            className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500" />
        </div>

        <div>
          <span className="text-sm text-gray-500">Role: <span className="capitalize font-medium">{user.role}</span></span>
        </div>

        <button type="submit" disabled={saving}
          className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50 font-medium">
          {saving ? 'Saving...' : 'Save Changes'}
        </button>
      </form>

      {/* Contactable toggle (for tenants) */}
      {user.role === 'tenant' && (
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="font-semibold">Allow Contact Requests</h3>
              <p className="text-sm text-gray-500">Let leads pay to send you messages about your reviews.</p>
            </div>
            <button
              onClick={toggleContactable}
              className={`relative w-12 h-6 rounded-full transition-colors ${
                user.is_contactable ? 'bg-blue-600' : 'bg-gray-300'
              }`}
            >
              <span
                className={`absolute top-0.5 left-0.5 w-5 h-5 bg-white rounded-full transition-transform ${
                  user.is_contactable ? 'translate-x-6' : ''
                }`}
              />
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
