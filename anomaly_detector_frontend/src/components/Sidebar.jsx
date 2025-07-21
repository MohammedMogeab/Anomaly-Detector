import { Link, useLocation } from 'react-router-dom'
import { cn } from '@/lib/utils'
import { 
  LayoutDashboard, 
  Folder, 
  Radio, 
  Zap, 
  Play, 
  Search, 
  FileText,
  Shield
} from 'lucide-react'

const navigation = [
  { name: 'Dashboard', href: '/dashboard', icon: LayoutDashboard },
  { name: 'Flows', href: '/flows', icon: Folder },
  { name: 'Recording', href: '/recording', icon: Radio },
  { name: 'Payloads', href: '/payloads', icon: Zap },
  { name: 'Replay', href: '/replay', icon: Play },
  { name: 'Analysis', href: '/analysis', icon: Search },
  { name: 'Reports', href: '/reports', icon: FileText },
]

export default function Sidebar({ currentFlow, isRecording }) {
  const location = useLocation()

  return (
    <div className="flex flex-col w-64 bg-white border-r border-gray-200">
      {/* Header */}
      <div className="flex items-center px-6 py-4 border-b border-gray-200">
        <Shield className="h-8 w-8 text-blue-600" />
        <div className="ml-3">
          <h1 className="text-lg font-semibold text-gray-900">Anomaly Detector</h1>
          <p className="text-sm text-gray-500">Business Logic Testing</p>
        </div>
      </div>

      {/* Current Flow Status */}
      {currentFlow && (
        <div className="px-6 py-4 bg-blue-50 border-b border-gray-200">
          <div className="flex items-center">
            <div className={cn(
              "w-2 h-2 rounded-full mr-2",
              isRecording ? "bg-red-500 animate-pulse" : "bg-green-500"
            )} />
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-gray-900 truncate">
                {currentFlow.name}
              </p>
              <p className="text-xs text-gray-500">
                {isRecording ? 'Recording...' : `${currentFlow.request_count} requests`}
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Navigation */}
      <nav className="flex-1 px-4 py-4 space-y-1">
        {navigation.map((item) => {
          const isActive = location.pathname === item.href
          return (
            <Link
              key={item.name}
              to={item.href}
              className={cn(
                "group flex items-center px-2 py-2 text-sm font-medium rounded-md transition-colors",
                isActive
                  ? "bg-blue-100 text-blue-700"
                  : "text-gray-600 hover:bg-gray-50 hover:text-gray-900"
              )}
            >
              <item.icon
                className={cn(
                  "mr-3 h-5 w-5 flex-shrink-0",
                  isActive ? "text-blue-500" : "text-gray-400 group-hover:text-gray-500"
                )}
              />
              {item.name}
            </Link>
          )
        })}
      </nav>

      {/* Footer */}
      <div className="px-6 py-4 border-t border-gray-200">
        <p className="text-xs text-gray-500">
          v1.0.0 - Business Logic Anomaly Detector
        </p>
      </div>
    </div>
  )
}

