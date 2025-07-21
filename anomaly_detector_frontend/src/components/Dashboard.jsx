import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { 
  Folder, 
  Radio, 
  Zap, 
  AlertTriangle, 
  TrendingUp,
  Activity,
  Shield,
  Clock
} from 'lucide-react'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts'

const SEVERITY_COLORS = {
  'Critical': '#ef4444',
  'High': '#f97316',
  'Medium': '#eab308',
  'Low': '#22c55e',
  'Info': '#3b82f6'
}

export default function Dashboard() {
  const [stats, setStats] = useState({
    totalFlows: 0,
    totalAnomalies: 0,
    vulnerabilities: 0,
    recentFlows: []
  })
  const [severityData, setSeverityData] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchDashboardData()
  }, [])

  const fetchDashboardData = async () => {
    try {
      setLoading(true)
      
      // Fetch all flows
      const flowsResponse = await fetch('/api/flows')
      const flows = await flowsResponse.json()
      
      let totalAnomalies = 0
      let totalVulnerabilities = 0
      const severityCounts = {}
      
      // Fetch anomalies for each flow
      for (const flow of flows) {
        try {
          const anomaliesResponse = await fetch(`/api/flows/${flow.flow_id}/anomalies`)
          if (anomaliesResponse.ok) {
            const anomalies = await anomaliesResponse.json()
            totalAnomalies += anomalies.length
            
            anomalies.forEach(anomaly => {
              if (anomaly.is_potential_vulnerability) {
                totalVulnerabilities++
              }
              severityCounts[anomaly.severity] = (severityCounts[anomaly.severity] || 0) + 1
            })
          }
        } catch (error) {
          console.error(`Failed to fetch anomalies for flow ${flow.flow_id}:`, error)
        }
      }
      
      // Convert severity counts to chart data
      const severityChartData = Object.entries(severityCounts).map(([severity, count]) => ({
        name: severity,
        value: count,
        color: SEVERITY_COLORS[severity] || '#6b7280'
      }))
      
      setStats({
        totalFlows: flows.length,
        totalAnomalies,
        vulnerabilities: totalVulnerabilities,
        recentFlows: flows.slice(-5).reverse()
      })
      
      setSeverityData(severityChartData)
    } catch (error) {
      console.error('Failed to fetch dashboard data:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="p-8">
        <div className="animate-pulse space-y-6">
          <div className="h-8 bg-gray-200 rounded w-1/4"></div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {[...Array(4)].map((_, i) => (
              <div key={i} className="h-32 bg-gray-200 rounded"></div>
            ))}
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="p-8 space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-gray-600 mt-2">
          Overview of your business logic anomaly detection activities
        </p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Flows</CardTitle>
            <Folder className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.totalFlows}</div>
            <p className="text-xs text-muted-foreground">
              Active testing flows
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Anomalies Found</CardTitle>
            <AlertTriangle className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.totalAnomalies}</div>
            <p className="text-xs text-muted-foreground">
              Across all flows
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Vulnerabilities</CardTitle>
            <Shield className="h-4 w-4 text-red-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-red-600">{stats.vulnerabilities}</div>
            <p className="text-xs text-muted-foreground">
              Potential security issues
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Detection Rate</CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {stats.totalFlows > 0 ? Math.round((stats.totalAnomalies / stats.totalFlows) * 100) / 100 : 0}
            </div>
            <p className="text-xs text-muted-foreground">
              Anomalies per flow
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Charts and Recent Activity */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Severity Distribution */}
        <Card>
          <CardHeader>
            <CardTitle>Anomaly Severity Distribution</CardTitle>
            <CardDescription>
              Breakdown of anomalies by severity level
            </CardDescription>
          </CardHeader>
          <CardContent>
            {severityData.length > 0 ? (
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={severityData}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    {severityData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            ) : (
              <div className="flex items-center justify-center h-[300px] text-gray-500">
                No anomaly data available
              </div>
            )}
          </CardContent>
        </Card>

        {/* Recent Flows */}
        <Card>
          <CardHeader>
            <CardTitle>Recent Flows</CardTitle>
            <CardDescription>
              Latest testing flows and their status
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {stats.recentFlows.length > 0 ? (
                stats.recentFlows.map((flow) => (
                  <div key={flow.flow_id} className="flex items-center justify-between p-3 border rounded-lg">
                    <div className="flex items-center space-x-3">
                      <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                      <div>
                        <p className="font-medium text-sm">{flow.name}</p>
                        <p className="text-xs text-gray-500">
                          {flow.target_domain || 'No domain specified'}
                        </p>
                      </div>
                    </div>
                    <div className="text-right">
                      <Badge variant="secondary" className="text-xs">
                        {flow.request_count} requests
                      </Badge>
                      <p className="text-xs text-gray-500 mt-1">
                        {flow.timestamp ? new Date(flow.timestamp).toLocaleDateString() : 'No date'}
                      </p>
                    </div>
                  </div>
                ))
              ) : (
                <div className="text-center py-8 text-gray-500">
                  <Folder className="h-12 w-12 mx-auto mb-4 text-gray-300" />
                  <p>No flows created yet</p>
                  <p className="text-sm">Start by creating your first flow</p>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Quick Actions */}
      <Card>
        <CardHeader>
          <CardTitle>Quick Actions</CardTitle>
          <CardDescription>
            Common tasks to get started with anomaly detection
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Button variant="outline" className="h-20 flex flex-col items-center justify-center space-y-2">
              <Radio className="h-6 w-6" />
              <span>Start Recording</span>
            </Button>
            <Button variant="outline" className="h-20 flex flex-col items-center justify-center space-y-2">
              <Zap className="h-6 w-6" />
              <span>Generate Payloads</span>
            </Button>
            <Button variant="outline" className="h-20 flex flex-col items-center justify-center space-y-2">
              <Activity className="h-6 w-6" />
              <span>Run Analysis</span>
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

