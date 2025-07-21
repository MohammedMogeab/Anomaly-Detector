import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog'
import { useToast } from '@/hooks/use-toast'
import { 
  Search, 
  AlertTriangle, 
  Shield, 
  TrendingUp,
  Settings,
  Target,
  Eye,
  Filter,
  Download,
  CheckCircle,
  XCircle
} from 'lucide-react'

const SEVERITY_COLORS = {
  'Critical': 'bg-red-500',
  'High': 'bg-orange-500',
  'Medium': 'bg-yellow-500',
  'Low': 'bg-green-500',
  'Info': 'bg-blue-500'
}

const SEVERITY_TEXT_COLORS = {
  'Critical': 'text-red-700',
  'High': 'text-orange-700',
  'Medium': 'text-yellow-700',
  'Low': 'text-green-700',
  'Info': 'text-blue-700'
}

export default function AnalysisResults({ currentFlow }) {
  const [anomalies, setAnomalies] = useState([])
  const [loading, setLoading] = useState(false)
  const [analyzing, setAnalyzing] = useState(false)
  const [threshold, setThreshold] = useState(0.7)
  const [isThresholdDialogOpen, setIsThresholdDialogOpen] = useState(false)
  const [filterSeverity, setFilterSeverity] = useState('all')
  const [filterType, setFilterType] = useState('all')
  const { toast } = useToast()

  useEffect(() => {
    if (currentFlow) {
      fetchAnomalies()
      fetchThreshold()
    }
  }, [currentFlow])

  const fetchAnomalies = async () => {
    if (!currentFlow) return
    
    try {
      setLoading(true)
      const response = await fetch(`/api/flows/${currentFlow.flow_id}/anomalies`)
      if (response.ok) {
        const data = await response.json()
        setAnomalies(data)
      }
    } catch (error) {
      console.error('Error fetching anomalies:', error)
    } finally {
      setLoading(false)
    }
  }

  const fetchThreshold = async () => {
    try {
      const response = await fetch('/api/analysis/threshold')
      if (response.ok) {
        const data = await response.json()
        setThreshold(data.threshold)
      }
    } catch (error) {
      console.error('Error fetching threshold:', error)
    }
  }

  const analyzeFlow = async () => {
    if (!currentFlow) return
    
    try {
      setAnalyzing(true)
      const response = await fetch(`/api/analysis/flow/${currentFlow.flow_id}`, {
        method: 'POST',
      })

      if (response.ok) {
        const data = await response.json()
        toast({
          title: "Analysis Complete",
          description: `Found ${data.anomalies_found} anomalies`,
        })
        fetchAnomalies()
      } else {
        const error = await response.json()
        throw new Error(error.error || 'Failed to analyze flow')
      }
    } catch (error) {
      console.error('Error analyzing flow:', error)
      toast({
        title: "Error",
        description: error.message,
        variant: "destructive",
      })
    } finally {
      setAnalyzing(false)
    }
  }

  const updateThreshold = async () => {
    try {
      const response = await fetch('/api/analysis/threshold', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ threshold }),
      })

      if (response.ok) {
        toast({
          title: "Threshold Updated",
          description: `Detection threshold set to ${threshold}`,
        })
        setIsThresholdDialogOpen(false)
      } else {
        const error = await response.json()
        throw new Error(error.error || 'Failed to update threshold')
      }
    } catch (error) {
      console.error('Error updating threshold:', error)
      toast({
        title: "Error",
        description: error.message,
        variant: "destructive",
      })
    }
  }

  const getSeverityStats = () => {
    const stats = {}
    anomalies.forEach(anomaly => {
      stats[anomaly.severity] = (stats[anomaly.severity] || 0) + 1
    })
    return stats
  }

  const getTypeStats = () => {
    const stats = {}
    anomalies.forEach(anomaly => {
      stats[anomaly.type] = (stats[anomaly.type] || 0) + 1
    })
    return stats
  }

  const getFilteredAnomalies = () => {
    return anomalies.filter(anomaly => {
      const severityMatch = filterSeverity === 'all' || anomaly.severity === filterSeverity
      const typeMatch = filterType === 'all' || anomaly.type === filterType
      return severityMatch && typeMatch
    })
  }

  if (!currentFlow) {
    return (
      <div className="p-8">
        <div className="text-center py-12">
          <Target className="h-16 w-16 mx-auto text-gray-300 mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">No Flow Selected</h3>
          <p className="text-gray-500">
            Please select a flow from the Flow Manager to view analysis results
          </p>
        </div>
      </div>
    )
  }

  const severityStats = getSeverityStats()
  const typeStats = getTypeStats()
  const filteredAnomalies = getFilteredAnomalies()
  const vulnerabilityCount = anomalies.filter(a => a.is_potential_vulnerability).length

  return (
    <div className="p-8 space-y-8">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Analysis Results</h1>
          <p className="text-gray-600 mt-2">
            Business logic anomalies and potential vulnerabilities
          </p>
        </div>
        <div className="flex space-x-2">
          <Dialog open={isThresholdDialogOpen} onOpenChange={setIsThresholdDialogOpen}>
            <DialogTrigger asChild>
              <Button variant="outline">
                <Settings className="h-4 w-4 mr-2" />
                Settings
              </Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Analysis Settings</DialogTitle>
                <DialogDescription>
                  Configure anomaly detection parameters
                </DialogDescription>
              </DialogHeader>
              <div className="space-y-4">
                <div>
                  <Label htmlFor="threshold">Detection Threshold (0.0 - 1.0)</Label>
                  <Input
                    id="threshold"
                    type="number"
                    min="0"
                    max="1"
                    step="0.1"
                    value={threshold}
                    onChange={(e) => setThreshold(parseFloat(e.target.value))}
                  />
                  <p className="text-sm text-gray-500 mt-1">
                    Higher values require more confidence to flag anomalies
                  </p>
                </div>
                <div className="flex justify-end space-x-2">
                  <Button variant="outline" onClick={() => setIsThresholdDialogOpen(false)}>
                    Cancel
                  </Button>
                  <Button onClick={updateThreshold}>
                    Update Threshold
                  </Button>
                </div>
              </div>
            </DialogContent>
          </Dialog>
          <Button onClick={analyzeFlow} disabled={analyzing}>
            {analyzing ? (
              <>
                <Search className="h-4 w-4 mr-2 animate-spin" />
                Analyzing...
              </>
            ) : (
              <>
                <Search className="h-4 w-4 mr-2" />
                Run Analysis
              </>
            )}
          </Button>
        </div>
      </div>

      {/* Current Flow Info */}
      <Card className="border-purple-200 bg-purple-50">
        <CardHeader>
          <CardTitle className="text-purple-900">Current Flow: {currentFlow.name}</CardTitle>
          <CardDescription className="text-purple-700">
            {currentFlow.description || 'No description provided'}
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-purple-900">{anomalies.length}</div>
              <div className="text-sm text-purple-600">Total Anomalies</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-red-600">{vulnerabilityCount}</div>
              <div className="text-sm text-purple-600">Vulnerabilities</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-purple-900">
                {Object.keys(typeStats).length}
              </div>
              <div className="text-sm text-purple-600">Anomaly Types</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-purple-900">{threshold}</div>
              <div className="text-sm text-purple-600">Detection Threshold</div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Statistics and Filters */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Severity Breakdown */}
        <Card>
          <CardHeader>
            <CardTitle>Severity Breakdown</CardTitle>
            <CardDescription>
              Distribution of anomalies by severity level
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {Object.entries(severityStats).map(([severity, count]) => (
                <div key={severity} className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <div className={`w-3 h-3 rounded-full ${SEVERITY_COLORS[severity]}`}></div>
                    <span className="font-medium">{severity}</span>
                  </div>
                  <Badge variant="secondary">{count}</Badge>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Type Breakdown */}
        <Card>
          <CardHeader>
            <CardTitle>Type Breakdown</CardTitle>
            <CardDescription>
              Distribution of anomalies by type
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {Object.entries(typeStats).map(([type, count]) => (
                <div key={type} className="flex items-center justify-between">
                  <span className="text-sm">{type.replace('_', ' ')}</span>
                  <Badge variant="outline">{count}</Badge>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Filters */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Filter className="h-5 w-5" />
            <span>Filters</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex space-x-4">
            <div>
              <Label htmlFor="severity-filter">Severity</Label>
              <select
                id="severity-filter"
                value={filterSeverity}
                onChange={(e) => setFilterSeverity(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md"
              >
                <option value="all">All Severities</option>
                {Object.keys(severityStats).map(severity => (
                  <option key={severity} value={severity}>{severity}</option>
                ))}
              </select>
            </div>
            <div>
              <Label htmlFor="type-filter">Type</Label>
              <select
                id="type-filter"
                value={filterType}
                onChange={(e) => setFilterType(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md"
              >
                <option value="all">All Types</option>
                {Object.keys(typeStats).map(type => (
                  <option key={type} value={type}>{type.replace('_', ' ')}</option>
                ))}
              </select>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Anomalies List */}
      <Card>
        <CardHeader>
          <div className="flex justify-between items-center">
            <div>
              <CardTitle>Detected Anomalies</CardTitle>
              <CardDescription>
                {filteredAnomalies.length} of {anomalies.length} anomalies shown
              </CardDescription>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          {filteredAnomalies.length > 0 ? (
            <div className="space-y-4 max-h-96 overflow-y-auto">
              {filteredAnomalies.map((anomaly) => (
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
                        className={`${SEVERITY_COLORS[anomaly.severity]} text-white`}
                      >
                        {anomaly.severity}
                      </Badge>
                      <Badge variant="secondary">{anomaly.type.replace('_', ' ')}</Badge>
                      {anomaly.is_potential_vulnerability && (
                        <Badge variant="destructive">Vulnerability</Badge>
                      )}
                    </div>
                    <div className="flex items-center space-x-2">
                      <span className="text-xs text-gray-500">
                        Confidence: {Math.round(anomaly.confidence_score * 100)}%
                      </span>
                      <span className="text-xs text-gray-500">
                        ID: {anomaly.anomaly_id}
                      </span>
                    </div>
                  </div>
                  
                  <p className="text-sm text-gray-700 mb-2">{anomaly.description}</p>
                  
                  {anomaly.vulnerability_type && (
                    <div className="text-xs text-red-600 mb-2">
                      <span className="font-medium">Vulnerability Type:</span>
                      <span className="ml-2">{anomaly.vulnerability_type.replace('_', ' ')}</span>
                    </div>
                  )}
                  
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-xs text-gray-600">
                    {anomaly.original_status && (
                      <div>
                        <span className="font-medium">Original Status:</span>
                        <div className="font-mono">{anomaly.original_status}</div>
                      </div>
                    )}
                    {anomaly.replayed_status && (
                      <div>
                        <span className="font-medium">Replayed Status:</span>
                        <div className="font-mono">{anomaly.replayed_status}</div>
                      </div>
                    )}
                    {anomaly.original_content_length && (
                      <div>
                        <span className="font-medium">Original Size:</span>
                        <div className="font-mono">{anomaly.original_content_length} bytes</div>
                      </div>
                    )}
                    {anomaly.replayed_content_length && (
                      <div>
                        <span className="font-medium">Replayed Size:</span>
                        <div className="font-mono">{anomaly.replayed_content_length} bytes</div>
                      </div>
                    )}
                  </div>
                  
                  {anomaly.created_timestamp && (
                    <div className="text-xs text-gray-500 mt-2">
                      Detected: {new Date(anomaly.created_timestamp).toLocaleString()}
                    </div>
                  )}
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8">
              {anomalies.length === 0 ? (
                <>
                  <Search className="h-12 w-12 mx-auto text-gray-300 mb-4" />
                  <h3 className="text-lg font-medium text-gray-900 mb-2">No Analysis Results</h3>
                  <p className="text-gray-500">
                    Run analysis on replayed test cases to detect anomalies
                  </p>
                </>
              ) : (
                <>
                  <Filter className="h-12 w-12 mx-auto text-gray-300 mb-4" />
                  <h3 className="text-lg font-medium text-gray-900 mb-2">No Matching Anomalies</h3>
                  <p className="text-gray-500">
                    Try adjusting your filters to see more results
                  </p>
                </>
              )}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}

