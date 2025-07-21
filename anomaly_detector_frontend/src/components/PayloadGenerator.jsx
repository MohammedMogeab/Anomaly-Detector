import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import { useToast } from '@/hooks/use-toast'
import { 
  Zap, 
  Play, 
  FileText, 
  AlertCircle,
  CheckCircle,
  Clock,
  Target,
  Settings
} from 'lucide-react'

export default function PayloadGenerator({ currentFlow }) {
  const [requests, setRequests] = useState([])
  const [testCases, setTestCases] = useState([])
  const [loading, setLoading] = useState(false)
  const [generating, setGenerating] = useState(false)
  const [selectedRequest, setSelectedRequest] = useState(null)
  const { toast } = useToast()

  useEffect(() => {
    if (currentFlow) {
      fetchRequests()
      fetchTestCases()
    }
  }, [currentFlow])

  const fetchRequests = async () => {
    if (!currentFlow) return
    
    try {
      const response = await fetch(`/api/flows/${currentFlow.flow_id}/requests`)
      if (response.ok) {
        const data = await response.json()
        setRequests(data)
      }
    } catch (error) {
      console.error('Error fetching requests:', error)
    }
  }

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

  const generatePayloadsForRequest = async (requestId) => {
    try {
      setGenerating(true)
      const response = await fetch(`/api/payloads/generate/request/${requestId}`, {
        method: 'POST',
      })

      if (response.ok) {
        const data = await response.json()
        toast({
          title: "Success",
          description: `Generated ${data.generated_count} test cases for request`,
        })
        fetchTestCases()
      } else {
        const error = await response.json()
        throw new Error(error.error || 'Failed to generate payloads')
      }
    } catch (error) {
      console.error('Error generating payloads:', error)
      toast({
        title: "Error",
        description: error.message,
        variant: "destructive",
      })
    } finally {
      setGenerating(false)
    }
  }

  const generatePayloadsForFlow = async () => {
    if (!currentFlow) return
    
    try {
      setGenerating(true)
      const response = await fetch(`/api/payloads/generate/flow/${currentFlow.flow_id}`, {
        method: 'POST',
      })

      if (response.ok) {
        const data = await response.json()
        toast({
          title: "Success",
          description: `Generated ${data.total_generated} test cases for entire flow`,
        })
        fetchTestCases()
      } else {
        const error = await response.json()
        throw new Error(error.error || 'Failed to generate payloads')
      }
    } catch (error) {
      console.error('Error generating payloads:', error)
      toast({
        title: "Error",
        description: error.message,
        variant: "destructive",
      })
    } finally {
      setGenerating(false)
    }
  }

  const getTestCasesByType = () => {
    const grouped = {}
    testCases.forEach(tc => {
      if (!grouped[tc.type]) {
        grouped[tc.type] = []
      }
      grouped[tc.type].push(tc)
    })
    return grouped
  }

  const getTestCasesByCategory = () => {
    const grouped = {}
    testCases.forEach(tc => {
      if (!grouped[tc.category]) {
        grouped[tc.category] = []
      }
      grouped[tc.category].push(tc)
    })
    return grouped
  }

  if (!currentFlow) {
    return (
      <div className="p-8">
        <div className="text-center py-12">
          <Target className="h-16 w-16 mx-auto text-gray-300 mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">No Flow Selected</h3>
          <p className="text-gray-500">
            Please select a flow from the Flow Manager to generate payloads
          </p>
        </div>
      </div>
    )
  }

  const testCasesByType = getTestCasesByType()
  const testCasesByCategory = getTestCasesByCategory()

  return (
    <div className="p-8 space-y-8">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Payload Generator</h1>
          <p className="text-gray-600 mt-2">
            Generate test payloads for business logic anomaly detection
          </p>
        </div>
        <Button 
          onClick={generatePayloadsForFlow}
          disabled={generating || requests.length === 0}
        >
          {generating ? (
            <>
              <Settings className="h-4 w-4 mr-2 animate-spin" />
              Generating...
            </>
          ) : (
            <>
              <Zap className="h-4 w-4 mr-2" />
              Generate All Payloads
            </>
          )}
        </Button>
      </div>

      {/* Current Flow Info */}
      <Card className="border-blue-200 bg-blue-50">
        <CardHeader>
          <CardTitle className="text-blue-900">Current Flow: {currentFlow.name}</CardTitle>
          <CardDescription className="text-blue-700">
            {currentFlow.description || 'No description provided'}
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-900">{requests.length}</div>
              <div className="text-sm text-blue-600">Requests</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-900">{testCases.length}</div>
              <div className="text-sm text-blue-600">Test Cases</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-900">
                {Object.keys(testCasesByType).length}
              </div>
              <div className="text-sm text-blue-600">Payload Types</div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Requests and Generation */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Requests */}
        <Card>
          <CardHeader>
            <CardTitle>Requests</CardTitle>
            <CardDescription>
              HTTP requests available for payload generation
            </CardDescription>
          </CardHeader>
          <CardContent>
            {requests.length > 0 ? (
              <div className="space-y-4">
                {requests.map((request) => {
                  const requestTestCases = testCases.filter(tc => tc.request_id === request.request_id)
                  return (
                    <div key={request.request_id} className="border rounded-lg p-4">
                      <div className="flex items-center justify-between mb-2">
                        <div className="flex items-center space-x-2">
                          <Badge variant="outline">{request.method}</Badge>
                          <span className="font-mono text-sm truncate">{request.url}</span>
                        </div>
                        <Badge variant="secondary">
                          {requestTestCases.length} test cases
                        </Badge>
                      </div>
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-2 text-sm text-gray-600">
                          <span>Status: {request.response_status}</span>
                          <span>•</span>
                          <span>{request.response_content_length || 0} bytes</span>
                        </div>
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => generatePayloadsForRequest(request.request_id)}
                          disabled={generating}
                        >
                          {generating ? (
                            <Settings className="h-4 w-4 animate-spin" />
                          ) : (
                            <>
                              <Zap className="h-4 w-4 mr-1" />
                              Generate
                            </>
                          )}
                        </Button>
                      </div>
                    </div>
                  )
                })}
              </div>
            ) : (
              <div className="text-center py-8">
                <FileText className="h-12 w-12 mx-auto text-gray-300 mb-4" />
                <p className="text-gray-500">No requests found in this flow</p>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Test Case Summary */}
        <Card>
          <CardHeader>
            <CardTitle>Generated Test Cases</CardTitle>
            <CardDescription>
              Summary of generated payload test cases
            </CardDescription>
          </CardHeader>
          <CardContent>
            {testCases.length > 0 ? (
              <div className="space-y-4">
                {/* By Category */}
                <div>
                  <h4 className="font-medium mb-2">By Category</h4>
                  <div className="space-y-2">
                    {Object.entries(testCasesByCategory).map(([category, cases]) => (
                      <div key={category} className="flex items-center justify-between p-2 bg-gray-50 rounded">
                        <span className="capitalize font-medium">{category}</span>
                        <Badge variant="secondary">{cases.length}</Badge>
                      </div>
                    ))}
                  </div>
                </div>

                {/* By Type */}
                <div>
                  <h4 className="font-medium mb-2">By Type</h4>
                  <div className="space-y-2">
                    {Object.entries(testCasesByType).map(([type, cases]) => (
                      <div key={type} className="flex items-center justify-between p-2 bg-gray-50 rounded">
                        <span className="text-sm">{type.replace('_', ' ')}</span>
                        <Badge variant="outline">{cases.length}</Badge>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            ) : (
              <div className="text-center py-8">
                <AlertCircle className="h-12 w-12 mx-auto text-gray-300 mb-4" />
                <p className="text-gray-500">No test cases generated yet</p>
                <p className="text-sm text-gray-400">Click "Generate" to create payload test cases</p>
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Detailed Test Cases */}
      {testCases.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Test Case Details</CardTitle>
            <CardDescription>
              Detailed view of all generated test cases
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4 max-h-96 overflow-y-auto">
              {testCases.map((testCase) => (
                <div key={testCase.test_case_id} className="border rounded-lg p-4">
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center space-x-2">
                      <Badge variant="outline">{testCase.category}</Badge>
                      <Badge variant="secondary">{testCase.type}</Badge>
                    </div>
                    <div className="text-xs text-gray-500">
                      ID: {testCase.test_case_id}
                    </div>
                  </div>
                  <p className="text-sm text-gray-700 mb-2">{testCase.description}</p>
                  {testCase.modified_url && (
                    <div className="text-xs text-gray-600">
                      <span className="font-medium">Modified URL:</span>
                      <code className="ml-2 bg-gray-100 px-1 rounded">{testCase.modified_url}</code>
                    </div>
                  )}
                  {testCase.payload_value && (
                    <div className="text-xs text-gray-600 mt-1">
                      <span className="font-medium">Payload:</span>
                      <code className="ml-2 bg-gray-100 px-1 rounded">{testCase.payload_value}</code>
                    </div>
                  )}
                  {testCase.timestamp && (
                    <div className="text-xs text-gray-500 mt-2 flex items-center">
                      <Clock className="h-3 w-3 mr-1" />
                      {new Date(testCase.timestamp).toLocaleString()}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}

