import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import { useToast } from '@/hooks/use-toast'
import { 
  Play, 
  Square, 
  RotateCcw, 
  Clock, 
  CheckCircle,
  XCircle,
  AlertTriangle,
  Target,
  Activity,
  Zap
} from 'lucide-react'

export default function ReplayInterface({ currentFlow }) {
  const [testCases, setTestCases] = useState([])
  const [replayedResponses, setReplayedResponses] = useState({})
  const [loading, setLoading] = useState(false)
  const [replaying, setReplaying] = useState(false)
  const [replayProgress, setReplayProgress] = useState(0)
  const { toast } = useToast()

  useEffect(() => {
    if (currentFlow) {
      fetchTestCases()
      fetchReplayedResponses()
    }
  }, [currentFlow])

  const fetchTestCases = async () => {
    if (!currentFlow) return
    
    try {
      const response = await fetch(`/api/flows/${currentFlow.flow_id}/test-cases`)
      if (response.ok) {
        const data = await response.json()
        setTestCases(data)
      }
    } catch (error) {
      console.error('Error fetching test cases:', error)
    }
  }

  const fetchReplayedResponses = async () => {
    if (!currentFlow) return
    
    try {
      const responses = {}
      for (const testCase of testCases) {
        try {
          const response = await fetch(`/api/replay/responses/${testCase.test_case_id}`)
          if (response.ok) {
            const data = await response.json()
            responses[testCase.test_case_id] = data
          }
        } catch (error) {
          // Response not found, which is normal for unplayed test cases
        }
      }
      setReplayedResponses(responses)
    } catch (error) {
      console.error('Error fetching replayed responses:', error)
    }
  }

  const replayFlow = async () => {
    if (!currentFlow) return
    
    try {
      setReplaying(true)
      setReplayProgress(0)
      
      const response = await fetch(`/api/replay/flow/${currentFlow.flow_id}`, {
        method: 'POST',
      })

      if (response.ok) {
        const data = await response.json()
        toast({
          title: "Replay Complete",
          description: `Successfully replayed ${data.replayed_count} test cases`,
        })
        setReplayProgress(100)
        fetchReplayedResponses()
      } else {
        const error = await response.json()
        throw new Error(error.error || 'Failed to replay flow')
      }
    } catch (error) {
      console.error('Error replaying flow:', error)
      toast({
        title: "Error",
        description: error.message,
        variant: "destructive",
      })
    } finally {
      setReplaying(false)
    }
  }

  const replayTestCase = async (testCaseId) => {
    try {
      const response = await fetch(`/api/replay/test-case/${testCaseId}`, {
        method: 'POST',
      })

      if (response.ok) {
        const data = await response.json()
        toast({
          title: "Test Case Replayed",
          description: `Test case ${testCaseId} replayed successfully`,
        })
        fetchReplayedResponses()
      } else {
        const error = await response.json()
        throw new Error(error.error || 'Failed to replay test case')
      }
    } catch (error) {
      console.error('Error replaying test case:', error)
      toast({
        title: "Error",
        description: error.message,
        variant: "destructive",
      })
    }
  }

  const getStatusBadge = (testCaseId) => {
    const response = replayedResponses[testCaseId]
    if (!response) {
      return <Badge variant="secondary">Not Replayed</Badge>
    }
    
    if (response.status_code >= 200 && response.status_code < 300) {
      return <Badge variant="default" className="bg-green-500">Success</Badge>
    } else if (response.status_code >= 400 && response.status_code < 500) {
      return <Badge variant="destructive">Client Error</Badge>
    } else if (response.status_code >= 500) {
      return <Badge variant="destructive">Server Error</Badge>
    } else {
      return <Badge variant="outline">Status {response.status_code}</Badge>
    }
  }

  const getResponseIcon = (testCaseId) => {
    const response = replayedResponses[testCaseId]
    if (!response) {
      return <Clock className="h-4 w-4 text-gray-400" />
    }
    
    if (response.status_code >= 200 && response.status_code < 300) {
      return <CheckCircle className="h-4 w-4 text-green-500" />
    } else if (response.status_code >= 400) {
      return <XCircle className="h-4 w-4 text-red-500" />
    } else {
      return <AlertTriangle className="h-4 w-4 text-yellow-500" />
    }
  }

  if (!currentFlow) {
    return (
      <div className="p-8">
        <div className="text-center py-12">
          <Target className="h-16 w-16 mx-auto text-gray-300 mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">No Flow Selected</h3>
          <p className="text-gray-500">
            Please select a flow from the Flow Manager to replay test cases
          </p>
        </div>
      </div>
    )
  }

  const replayedCount = Object.keys(replayedResponses).length
  const totalCount = testCases.length

  return (
    <div className="p-8 space-y-8">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Replay Interface</h1>
          <p className="text-gray-600 mt-2">
            Execute test cases and capture responses for analysis
          </p>
        </div>
        <Button 
          onClick={replayFlow}
          disabled={replaying || testCases.length === 0}
        >
          {replaying ? (
            <>
              <RotateCcw className="h-4 w-4 mr-2 animate-spin" />
              Replaying...
            </>
          ) : (
            <>
              <Play className="h-4 w-4 mr-2" />
              Replay All
            </>
          )}
        </Button>
      </div>

      {/* Current Flow Info */}
      <Card className="border-green-200 bg-green-50">
        <CardHeader>
          <CardTitle className="text-green-900">Current Flow: {currentFlow.name}</CardTitle>
          <CardDescription className="text-green-700">
            {currentFlow.description || 'No description provided'}
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-green-900">{totalCount}</div>
              <div className="text-sm text-green-600">Total Test Cases</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-green-900">{replayedCount}</div>
              <div className="text-sm text-green-600">Replayed</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-green-900">{totalCount - replayedCount}</div>
              <div className="text-sm text-green-600">Pending</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-green-900">
                {totalCount > 0 ? Math.round((replayedCount / totalCount) * 100) : 0}%
              </div>
              <div className="text-sm text-green-600">Complete</div>
            </div>
          </div>
          {replaying && (
            <div className="mt-4">
              <Progress value={replayProgress} className="w-full" />
              <p className="text-sm text-green-600 mt-2">Replaying test cases...</p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Test Cases */}
      <Card>
        <CardHeader>
          <CardTitle>Test Cases</CardTitle>
          <CardDescription>
            Generated test cases and their replay status
          </CardDescription>
        </CardHeader>
        <CardContent>
          {testCases.length > 0 ? (
            <div className="space-y-4 max-h-96 overflow-y-auto">
              {testCases.map((testCase) => {
                const response = replayedResponses[testCase.test_case_id]
                return (
                  <div key={testCase.test_case_id} className="border rounded-lg p-4">
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center space-x-2">
                        {getResponseIcon(testCase.test_case_id)}
                        <Badge variant="outline">{testCase.category}</Badge>
                        <Badge variant="secondary">{testCase.type}</Badge>
                        {getStatusBadge(testCase.test_case_id)}
                      </div>
                      <div className="flex items-center space-x-2">
                        <span className="text-xs text-gray-500">ID: {testCase.test_case_id}</span>
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => replayTestCase(testCase.test_case_id)}
                          disabled={replaying}
                        >
                          <Play className="h-3 w-3 mr-1" />
                          Replay
                        </Button>
                      </div>
                    </div>
                    
                    <p className="text-sm text-gray-700 mb-2">{testCase.description}</p>
                    
                    {testCase.modified_url && (
                      <div className="text-xs text-gray-600 mb-2">
                        <span className="font-medium">URL:</span>
                        <code className="ml-2 bg-gray-100 px-1 rounded text-xs">{testCase.modified_url}</code>
                      </div>
                    )}
                    
                    {response && (
                      <div className="mt-3 p-3 bg-gray-50 rounded border-l-4 border-l-blue-500">
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-xs">
                          <div>
                            <span className="font-medium text-gray-600">Status:</span>
                            <div className="font-mono">{response.status_code}</div>
                          </div>
                          <div>
                            <span className="font-medium text-gray-600">Size:</span>
                            <div className="font-mono">{response.content_length || 0} bytes</div>
                          </div>
                          <div>
                            <span className="font-medium text-gray-600">Time:</span>
                            <div className="font-mono">{response.response_time_ms || 0}ms</div>
                          </div>
                          <div>
                            <span className="font-medium text-gray-600">Timestamp:</span>
                            <div className="font-mono">
                              {response.timestamp ? new Date(response.timestamp).toLocaleTimeString() : 'N/A'}
                            </div>
                          </div>
                        </div>
                      </div>
                    )}
                  </div>
                )
              })}
            </div>
          ) : (
            <div className="text-center py-8">
              <Zap className="h-12 w-12 mx-auto text-gray-300 mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">No Test Cases</h3>
              <p className="text-gray-500">
                Generate payloads first to create test cases for replay
              </p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Replay Statistics */}
      {replayedCount > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Success Rate</CardTitle>
              <CheckCircle className="h-4 w-4 text-green-500" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {Math.round((Object.values(replayedResponses).filter(r => r.status_code < 400).length / replayedCount) * 100)}%
              </div>
              <p className="text-xs text-muted-foreground">
                Successful responses (2xx-3xx)
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Avg Response Time</CardTitle>
              <Activity className="h-4 w-4 text-blue-500" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {Math.round(Object.values(replayedResponses).reduce((acc, r) => acc + (r.response_time_ms || 0), 0) / replayedCount)}ms
              </div>
              <p className="text-xs text-muted-foreground">
                Average response time
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Error Rate</CardTitle>
              <XCircle className="h-4 w-4 text-red-500" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {Math.round((Object.values(replayedResponses).filter(r => r.status_code >= 400).length / replayedCount) * 100)}%
              </div>
              <p className="text-xs text-muted-foreground">
                Error responses (4xx-5xx)
              </p>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  )
}

