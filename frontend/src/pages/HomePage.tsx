import { Link } from 'react-router-dom'
import { useAuthStore } from '../store/authStore'

export default function HomePage() {
  const { isAuthenticated } = useAuthStore()

  return (
    <div>
      {/* Hero */}
      <section className="bg-gradient-to-br from-blue-600 to-blue-800 text-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20 text-center">
          <h1 className="text-4xl md:text-5xl font-bold mb-4">
            Know Before You Rent
          </h1>
          <p className="text-xl text-blue-100 mb-8 max-w-2xl mx-auto">
            Real reviews from verified tenants about rental properties.
            Plumbing, electricity, landlord responsiveness — get the full picture.
          </p>
          <div className="flex justify-center gap-4">
            <Link
              to="/properties"
              className="bg-white text-blue-700 px-6 py-3 rounded-lg font-semibold hover:bg-blue-50 transition-colors"
            >
              Search Properties
            </Link>
            {!isAuthenticated && (
              <Link
                to="/register"
                className="border-2 border-white text-white px-6 py-3 rounded-lg font-semibold hover:bg-white/10 transition-colors"
              >
                Leave a Review
              </Link>
            )}
          </div>
        </div>
      </section>

      {/* How it works */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <h2 className="text-2xl font-bold text-center mb-10">How It Works</h2>
        <div className="grid md:grid-cols-3 gap-8">
          {[
            {
              title: 'For Tenants',
              desc: 'Share your rental experience. Rate your property across 13 categories and help future tenants make informed decisions.',
              icon: '🏠',
            },
            {
              title: 'For Leads',
              desc: 'Browse properties and see average ratings for free. Unlock detailed reviews and contact ex-tenants for a small fee.',
              icon: '🔍',
            },
            {
              title: 'For Landlords',
              desc: 'Claim your property, respond to reviews, and dispute inaccurate claims. Build your reputation.',
              icon: '🏢',
            },
          ].map((item) => (
            <div key={item.title} className="bg-white rounded-lg border border-gray-200 p-6 text-center">
              <div className="text-4xl mb-3">{item.icon}</div>
              <h3 className="font-semibold text-lg mb-2">{item.title}</h3>
              <p className="text-gray-500 text-sm">{item.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Categories */}
      <section className="bg-white py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <h2 className="text-2xl font-bold text-center mb-10">What We Review</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-5 gap-3">
            {[
              'Plumbing', 'Electricity', 'Water', 'HVAC', 'IT Cabling',
              'Stove', 'Washer', 'Fridge', 'Water Tank', 'Irrigation',
              'Dust Levels', 'Air Quality', 'Sewage',
            ].map((cat) => (
              <div key={cat} className="bg-gray-50 rounded-lg px-4 py-3 text-center text-sm font-medium text-gray-700">
                {cat}
              </div>
            ))}
          </div>
        </div>
      </section>
    </div>
  )
}
