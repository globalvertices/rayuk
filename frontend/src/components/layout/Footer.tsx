import { Link } from 'react-router-dom'

export default function Footer() {
  return (
    <footer className="bg-gray-50 border-t border-gray-200 mt-auto">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div>
            <h3 className="text-lg font-bold text-blue-600">RayUK</h3>
            <p className="mt-2 text-sm text-gray-500">
              Honest tenant reviews for rental properties.
            </p>
          </div>
          <div>
            <h4 className="font-semibold text-gray-700">Quick Links</h4>
            <ul className="mt-2 space-y-1">
              <li><Link to="/properties" className="text-sm text-gray-500 hover:text-gray-700">Search Properties</Link></li>
              <li><Link to="/register" className="text-sm text-gray-500 hover:text-gray-700">Sign Up</Link></li>
            </ul>
          </div>
          <div>
            <h4 className="font-semibold text-gray-700">Legal</h4>
            <ul className="mt-2 space-y-1">
              <li><span className="text-sm text-gray-500">Privacy Policy</span></li>
              <li><span className="text-sm text-gray-500">Terms of Service</span></li>
            </ul>
          </div>
        </div>
        <div className="mt-8 pt-4 border-t border-gray-200 text-center text-sm text-gray-400">
          &copy; {new Date().getFullYear()} RayUK. All rights reserved.
        </div>
      </div>
    </footer>
  )
}
