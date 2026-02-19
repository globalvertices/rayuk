import { Routes, Route } from 'react-router-dom'
import { useEffect } from 'react'
import { useAuthStore } from './store/authStore'
import PageLayout from './components/layout/PageLayout'
import ProtectedRoute from './components/auth/ProtectedRoute'
import RoleGuard from './components/auth/RoleGuard'
import HomePage from './pages/HomePage'
import LoginPage from './pages/LoginPage'
import RegisterPage from './pages/RegisterPage'
import PropertySearchPage from './pages/PropertySearchPage'
import PropertyDetailPage from './pages/PropertyDetailPage'
import WriteReviewPage from './pages/WriteReviewPage'
import MyReviewsPage from './pages/MyReviewsPage'
import ProfilePage from './pages/ProfilePage'
import VerificationPage from './pages/VerificationPage'
import PaymentPage from './pages/PaymentPage'
import MessagesPage from './pages/MessagesPage'
import LandlordDashboardPage from './pages/LandlordDashboardPage'
import AdminDashboardPage from './pages/AdminDashboardPage'
import NotFoundPage from './pages/NotFoundPage'

export default function App() {
  const { isAuthenticated, fetchUser } = useAuthStore()

  useEffect(() => {
    if (isAuthenticated) {
      fetchUser()
    }
  }, [isAuthenticated, fetchUser])

  return (
    <Routes>
      <Route element={<PageLayout />}>
        {/* Public routes */}
        <Route path="/" element={<HomePage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route path="/properties" element={<PropertySearchPage />} />
        <Route path="/properties/:id" element={<PropertyDetailPage />} />

        {/* Protected routes (any authenticated user) */}
        <Route element={<ProtectedRoute />}>
          <Route path="/profile" element={<ProfilePage />} />
          <Route path="/my-reviews" element={<MyReviewsPage />} />
          <Route path="/verification" element={<VerificationPage />} />
          <Route path="/payments" element={<PaymentPage />} />
          <Route path="/messages" element={<MessagesPage />} />

          {/* Tenant-only routes */}
          <Route element={<RoleGuard roles={['tenant']} />}>
            <Route path="/properties/:id/review" element={<WriteReviewPage />} />
          </Route>

          {/* Landlord-only routes */}
          <Route element={<RoleGuard roles={['landlord']} />}>
            <Route path="/landlord" element={<LandlordDashboardPage />} />
          </Route>

          {/* Admin-only routes */}
          <Route element={<RoleGuard roles={['admin']} />}>
            <Route path="/admin" element={<AdminDashboardPage />} />
          </Route>
        </Route>

        {/* 404 */}
        <Route path="*" element={<NotFoundPage />} />
      </Route>
    </Routes>
  )
}
