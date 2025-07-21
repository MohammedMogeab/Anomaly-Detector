import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { useToast } from '@/hooks/use-toast'
import { 
  FileText, 
  Download, 
  Eye, 
  Target,
  BarChart3,
  PieChart,
  TrendingUp,
  Shield,
  AlertTriangle,
  CheckCircle
} from 'lucide-react'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart as RechartsPieChart, Pie, Cell } from 'recharts'

const SEVERITY_COLORS = {
  'Critical': '#ef4444',
  'High': '#f97316',
  'Medium': '#eab308',
  'Low': '#22c55e',
  'Info': '#3b82f6'
}

export default function ReportsView({ currentFlow }) {
  const [reportSummary, setReportSummary] = useState(null)
  const [loading, setLoading] = useState(false)
  const [generating, setGenerating] = useState(false)
  const { toast } = useToast()

  useEffect(() => {
    if (currentFlow) {
      fetchReportSummary()
    }
  }, [currentFlow])

  const fetchReportSummary = async () => {
    if (!currentFlow) return
    
    try {
      setLoading(true)
      const response = await fetch(`/api/reports/summary/${currentFlow.flow_id}`)
      if (response.ok) {
        const data = await response.json()
        setReportSummary(data)
      }
    } catch (error) {
      console.error('Error fetching report summary:', error)
    } finally {
      setLoading(false)
    }
  }

  const generateHtmlReport = async () => {
    if (!currentFlow) return
    
    try {
      setGenerating(true)
      const response = await fetch(`/api/reports/html/${currentFlow.flow_id}`)
      
      if (response.ok) {
        const blob = await response.blob()
        const url = window.URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.style.display = 'none'
        a.href = url
        a.download = `anomaly_report_flow_${currentFlow.flow_id}.html`
        document.body.appendChild(a)
        a.click()
        window.URL.revokeObjectURL(url)
        
        toast({
          title: "Report Generated",
          description: "HTML report has been downloaded",
        })
      } else {
        const error = await response.json()
        throw new Error(error.error || 'Failed to generate HTML report')
      }
    } catch (error) {
      console.error('Error generating HTML report:', error)
      toast({
        title: "Error",
        description: error.message,
        variant: "destructive",
      })
    } finally {
      setGenerating(false)
    }
  }

  const generateJsonReport = async () => {
    if (!currentFlow) return
    
    try {
      setGenerating(true)
      const response = await fetch(`/api/reports/json/${currentFlow.flow_id}`)
      
      if (response.ok) {
        const blob = await response.blob()
        const url = window.URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.style.display = 'none'
        a.href = url
        a.download = `anomaly_report_flow_${currentFlow.flow_id}.json`
        document.body.appendChild(a)
        a.click()
        window.URL.revokeObjectURL(url)
        
        toast({
          title: "Report Generated",
          description: "JSON report has been downloaded",
        })
      } else {
        const error = await response.json()
        throw new Error(error.error || 'Failed to generate JSON report')
      }
    } catch (error) {
      console.error('Error generating JSON report:', error)
      toast({
        title: "Error",
        description: error.message,
        variant: "destructive",
      })
    } finally {
      setGenerating(false)
    }
  }

  if (!currentFlow) {
    return (
      <div className="p-8">
        <div className="text-center py-12">
          <Target className="h-16 w-16 mx-auto text-gray-300 mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">No Flow Selected</h3>
          <p className="text-gray-500">
            Please select a flow from the Flow Manager to view reports
          </p>
        </div>
      </div>
    )
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

  const severityChartData = reportSummary?.summary.severity_breakdown 
    ? Object.entries(reportSummary.summary.severity_breakdown).map(([severity, count]) => ({
        name: severity,
        value: count,
        color: SEVERITY_COLORS[severity] || '#6b7280'
      }))
    : []

  const typeChartData = reportSummary?.summary.type_breakdown
    ? Object.entries(reportSummary.summary.type_breakdown).map(([type, count]) => ({
        name: type.replace('_', ' '),
        count: count
      }))
    : []

  return (
    <div className="p-8 space-y-8">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Reports</h1>
          <p className="text-gray-600 mt-2">
            Generate and download comprehensive anomaly detection reports
          </p>
        </div>
        <div className="flex space-x-2">
          <Button 
            variant="outline" 
            onClick={generateJsonReport}
            disabled={generating || !reportSummary}
          >
            <Download className="h-4 w-4 mr-2" />
            JSON Report
          </Button>
          <Button 
            onClick={generateHtmlReport}
            disabled={generating || !reportSummary}
          >
            <FileText className="h-4 w-4 mr-2" />
            HTML Report
          </Button>
        </div>
      </div>

      {/* Current Flow Info */}
      <Card className="border-indigo-200 bg-indigo-50">
        <CardHeader>
          <CardTitle className="text-indigo-900">Report for: {currentFlow.name}</CardTitle>
          <CardDescription className="text-indigo-700">
            {currentFlow.description || 'No description provided'}
          </CardDescription>
        </CardHeader>
        <CardContent>
          {reportSummary && (
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div className="text-center">
                <div className="text-2xl font-bold text-indigo-900">
                  {reportSummary.summary.total_anomalies}
                </div>
                <div className="text-sm text-indigo-600">Total Anomalies</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-red-600">
                  {reportSummary.summary.potential_vulnerabilities}
                </div>
                <div className="text-sm text-indigo-600">Vulnerabilities</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-indigo-900">
                  {reportSummary.flow.request_count}
                </div>
                <div className="text-sm text-indigo-600">Requests Tested</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-indigo-900">
                  {reportSummary.flow.timestamp ? new Date(reportSummary.flow.timestamp).toLocaleDateString() : 'N/A'}
                </div>
                <div className="text-sm text-indigo-600">Flow Created</div>
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {reportSummary ? (
        <>
          {/* Summary Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Critical Issues</CardTitle>
                <AlertTriangle className="h-4 w-4 text-red-500" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-red-600">
                  {reportSummary.summary.severity_breakdown.Critical || 0}
                </div>
                <p className="text-xs text-muted-foreground">
                  Require immediate attention
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">High Priority</CardTitle>
                <Shield className="h-4 w-4 text-orange-500" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-orange-600">
                  {reportSummary.summary.severity_breakdown.High || 0}
                </div>
                <p className="text-xs text-muted-foreground">
                  Should be addressed soon
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Medium Priority</CardTitle>
                <TrendingUp className="h-4 w-4 text-yellow-500" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-yellow-600">
                  {reportSummary.summary.severity_breakdown.Medium || 0}
                </div>
                <p className="text-xs text-muted-foreground">
                  Monitor and plan fixes
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Low Priority</CardTitle>
                <CheckCircle className="h-4 w-4 text-green-500" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-green-600">
                  {reportSummary.summary.severity_breakdown.Low || 0}
                </div>
                <p className="text-xs text-muted-foreground">
                  Address when convenient
                </p>
              </CardContent>
            </Card>
          </div>

          {/* Charts */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {/* Severity Distribution */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <PieChart className="h-5 w-5" />
                  <span>Severity Distribution</span>
                </CardTitle>
                <CardDescription>
                  Breakdown of anomalies by severity level
                </CardDescription>
              </CardHeader>
              <CardContent>
                {severityChartData.length > 0 ? (
                  <ResponsiveContainer width="100%" height={300}>
                    <RechartsPieChart>
                      <Pie
                        data={severityChartData}
                        cx="50%"
                        cy="50%"
                        labelLine={false}
                        label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                        outerRadius={80}
                        fill="#8884d8"
                        dataKey="value"
                      >
                        {severityChartData.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={entry.color} />
                        ))}
                      </Pie>
                      <Tooltip />
                    </RechartsPieChart>
                  </ResponsiveContainer>
                ) : (
                  <div className="flex items-center justify-center h-[300px] text-gray-500">
                    No severity data available
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Type Distribution */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <BarChart3 className="h-5 w-5" />
                  <span>Anomaly Types</span>
                </CardTitle>
                <CardDescription>
                  Distribution of anomalies by type
                </CardDescription>
              </CardHeader>
              <CardContent>
                {typeChartData.length > 0 ? (
                  <ResponsiveContainer width="100%" height={300}>
                    <BarChart data={typeChartData}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis 
                        dataKey="name" 
                        angle={-45}
                        textAnchor="end"
                        height={80}
                        fontSize={12}
                      />
                      <YAxis />
                      <Tooltip />
                      <Bar dataKey="count" fill="#3b82f6" />
                    </BarChart>
                  </ResponsiveContainer>
                ) : (
                  <div className="flex items-center justify-center h-[300px] text-gray-500">
                    No type data available
                  </div>
                )}
              </CardContent>
            </Card>
          </div>

          {/* Recent Anomalies */}
          <Card>
            <CardHeader>
              <CardTitle>Recent Anomalies</CardTitle>
              <CardDescription>
                Latest detected anomalies in this flow
              </CardDescription>
            </CardHeader>
            <CardContent>
              {reportSummary.anomalies.length > 0 ? (
                <div className="space-y-4 max-h-96 overflow-y-auto">
                  {reportSummary.anomalies.slice(0, 10).map((anomaly) => (
                    <div key={anomaly.anomaly_id} className="border rounded-lg p-4">
                      <div className="flex items-center justify-between mb-2">
                        <div className="flex items-center space-x-2">
                          {anomaly.is_potential_vulnerability ? (
                            <Shield className="h-4 w-4 text-red-500" />
                          ) : (
                            <AlertTriangle className="h-4 w-4 text-yellow-500" />
                          )}
                          <Badge 
                            variant="outline" 
                            style={{ 
                              backgroundColor: SEVERITY_COLORS[anomaly.severity],
                              color: 'white',
                              borderColor: SEVERITY_COLORS[anomaly.severity]
                            }}
                          >
                            {anomaly.severity}
                          </Badge>
                          <Badge variant="secondary">{anomaly.type.replace('_', ' ')}</Badge>
                          {anomaly.is_potential_vulnerability && (
                            <Badge variant="destructive">Vulnerability</Badge>
                          )}
                        </div>
                        <div className="text-xs text-gray-500">
                          Confidence: {Math.round(anomaly.confidence_score * 100)}%
                        </div>
                      </div>
                      <p className="text-sm text-gray-700">{anomaly.description}</p>
                      {anomaly.created_timestamp && (
                        <div className="text-xs text-gray-500 mt-2">
                          {new Date(anomaly.created_timestamp).toLocaleString()}
                        </div>
                      )}
                    </div>
                  ))}
                  {reportSummary.anomalies.length > 10 && (
                    <div className="text-center py-4 text-gray-500">
                      ... and {reportSummary.anomalies.length - 10} more anomalies
                    </div>
                  )}
                </div>
              ) : (
                <div className="text-center py-8">
                  <CheckCircle className="h-12 w-12 mx-auto text-green-500 mb-4" />
                  <h3 className="text-lg font-medium text-gray-900 mb-2">No Anomalies Found</h3>
                  <p className="text-gray-500">
                    This flow appears to be functioning normally
                  </p>
                </div>
              )}
            </CardContent>
          </Card>
        </>
      ) : (
        <div className="text-center py-12">
          <FileText className="h-16 w-16 mx-auto text-gray-300 mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">No Report Data</h3>
          <p className="text-gray-500">
            Run analysis on this flow to generate report data
          </p>
        </div>
      )}
    </div>
  )
}

