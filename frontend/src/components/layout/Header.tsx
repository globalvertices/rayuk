import { Link, useNavigate } from 'react-router-dom'
import { useAuthStore } from '../../store/authStore'

export default function Header() {
  const { user, isAuthenticated, logout } = useAuthStore()
  const navigate = useNavigate()

  const handleLogout = async () => {
    await logout()
    navigate('/login')
  }

  return (
    <header className="bg-white border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          <Link to="/" className="text-2xl font-bold text-blue-600">
            RayUK
          </Link>

          <nav className="hidden md:flex items-center gap-6">
            <Link to="/properties" className="text-gray-600 hover:text-gray-900">
              Properties
            </Link>
            {isAuthenticated && user?.role === 'tenant' && (
              <Link to="/my-reviews" className="text-gray-600 hover:text-gray-900">
                My Reviews
              </Link>
            )}
            {isAuthenticated && user?.role === 'landlord' && (
              <Link to="/landlord" className="text-gray-600 hover:text-gray-900">
                Dashboard
              </Link>
            )}
            {isAuthenticated && user?.role === 'admin' && (
              <Link to="/admin" className="text-gray-600 hover:text-gray-900">
                Admin
              </Link>
            )}
          </nav>

          <div className="flex items-center gap-4">
            {isAuthenticated ? (
              <>
                <Link to="/profile" className="text-gray-600 hover:text-gray-900">
                  {user?.first_name}
                </Link>
                <Link to="/payments" className="text-gray-600 hover:text-gray-900">
                  Wallet
                </Link>
                <Link to="/messages" className="text-gray-600 hover:text-gray-900">
                  Messages
                </Link>
                <button
                  onClick={handleLogout}
                  className="text-sm text-gray-500 hover:text-gray-700"
                >
                  Logout
                </button>
              </>
            ) : (
              <>
                <Link
                  to="/login"
                  className="text-gray-600 hover:text-gray-900"
                >
                  Login
                </Link>
                <Link
                  to="/register"
                  className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"
                >
                  Sign Up
                </Link>
              </>
            )}
          </div>
        </div>
      </div>
    </header>
  )
}
