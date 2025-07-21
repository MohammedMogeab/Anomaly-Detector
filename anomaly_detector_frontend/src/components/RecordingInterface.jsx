import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Badge } from '@/components/ui/badge'
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog'
import { useToast } from '@/hooks/use-toast'
import { 
  Radio, 
  Square, 
  Plus, 
  Globe, 
  Clock,
  FileText,
  AlertCircle,
  CheckCircle
} from 'lucide-react'

export default function RecordingInterface({ 
  isRecording, 
  setIsRecording, 
  currentFlow, 
  setCurrentFlow,
  onRecordingStatusChange 
}) {
  const [requests, setRequests] = useState([])
  const [isStartDialogOpen, setIsStartDialogOpen] = useState(false)
  const [isAddRequestDialogOpen, setIsAddRequestDialogOpen] = useState(false)
  const [newFlow, setNewFlow] = useState({
    name: '',
    description: '',
    target_domain: ''
  })
  const [newRequest, setNewRequest] = useState({
    url: '',
    method: 'GET',
    headers: '{}',
    body: '',
    response_status: 200,
    response_headers: '{}',
    response_content: ''
  })
  const { toast } = useToast()

  useEffect(() => {
    if (currentFlow) {
      fetchRequests()
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

  const startRecording = async () => {
    if (!newFlow.name.trim()) {
      toast({
        title: "Error",
        description: "Flow name is required",
        variant: "destructive",
      })
      return
    }

    try {
      const response = await fetch('/api/recording/start', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(newFlow),
      })

      if (response.ok) {
        const data = await response.json()
        setIsRecording(true)
        setCurrentFlow({
          flow_id: data.flow_id,
          name: newFlow.name,
          description: newFlow.description,
          target_domain: newFlow.target_domain,
          request_count: 0
        })
        setIsStartDialogOpen(false)
        setNewFlow({ name: '', description: '', target_domain: '' })
        toast({
          title: "Recording Started",
          description: "Successfully started recording new flow",
        })
        onRecordingStatusChange()
      } else {
        const error = await response.json()
        throw new Error(error.error || 'Failed to start recording')
      }
    } catch (error) {
      console.error('Error starting recording:', error)
      toast({
        title: "Error",
        description: error.message,
        variant: "destructive",
      })
    }
  }

  const stopRecording = async () => {
    try {
      const response = await fetch('/api/recording/stop', {
        method: 'POST',
      })

      if (response.ok) {
        setIsRecording(false)
        toast({
          title: "Recording Stopped",
          description: "Recording has been stopped successfully",
        })
        onRecordingStatusChange()
        fetchRequests() // Refresh requests
      } else {
        const error = await response.json()
        throw new Error(error.error || 'Failed to stop recording')
      }
    } catch (error) {
      console.error('Error stopping recording:', error)
      toast({
        title: "Error",
        description: error.message,
        variant: "destructive",
      })
    }
  }

  const addRequest = async () => {
    if (!newRequest.url.trim()) {
      toast({
        title: "Error",
        description: "URL is required",
        variant: "destructive",
      })
      return
    }

    try {
      // Parse JSON fields
      const headers = JSON.parse(newRequest.headers || '{}')
      const response_headers = JSON.parse(newRequest.response_headers || '{}')

      const response = await fetch('/api/recording/request', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          ...newRequest,
          headers,
          response_headers,
          response_status: parseInt(newRequest.response_status)
        }),
      })

      if (response.ok) {
        setIsAddRequestDialogOpen(false)
        setNewRequest({
          url: '',
          method: 'GET',
          headers: '{}',
          body: '',
          response_status: 200,
          response_headers: '{}',
          response_content: ''
        })
        toast({
          title: "Request Added",
          description: "Request has been added to the recording",
        })
        fetchRequests()
        onRecordingStatusChange() // Update request count
      } else {
        const error = await response.json()
        throw new Error(error.error || 'Failed to add request')
      }
    } catch (error) {
      console.error('Error adding request:', error)
      toast({
        title: "Error",
        description: error.message,
        variant: "destructive",
      })
    }
  }

  return (
    <div className="p-8 space-y-8">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Recording Interface</h1>
          <p className="text-gray-600 mt-2">
            Record HTTP requests and responses for anomaly testing
          </p>
        </div>
        <div className="flex space-x-2">
          {!isRecording ? (
            <Dialog open={isStartDialogOpen} onOpenChange={setIsStartDialogOpen}>
              <DialogTrigger asChild>
                <Button>
                  <Radio className="h-4 w-4 mr-2" />
                  Start Recording
                </Button>
              </DialogTrigger>
              <DialogContent>
                <DialogHeader>
                  <DialogTitle>Start New Recording</DialogTitle>
                  <DialogDescription>
                    Create a new flow and start recording HTTP requests.
                  </DialogDescription>
                </DialogHeader>
                <div className="space-y-4">
                  <div>
                    <Label htmlFor="name">Flow Name *</Label>
                    <Input
                      id="name"
                      value={newFlow.name}
                      onChange={(e) => setNewFlow({ ...newFlow, name: e.target.value })}
                      placeholder="Enter flow name"
                    />
                  </div>
                  <div>
                    <Label htmlFor="description">Description</Label>
                    <Textarea
                      id="description"
                      value={newFlow.description}
                      onChange={(e) => setNewFlow({ ...newFlow, description: e.target.value })}
                      placeholder="Enter flow description"
                      rows={3}
                    />
                  </div>
                  <div>
                    <Label htmlFor="target_domain">Target Domain</Label>
                    <Input
                      id="target_domain"
                      value={newFlow.target_domain}
                      onChange={(e) => setNewFlow({ ...newFlow, target_domain: e.target.value })}
                      placeholder="e.g., example.com"
                    />
                  </div>
                  <div className="flex justify-end space-x-2">
                    <Button variant="outline" onClick={() => setIsStartDialogOpen(false)}>
                      Cancel
                    </Button>
                    <Button onClick={startRecording}>
                      Start Recording
                    </Button>
                  </div>
                </div>
              </DialogContent>
            </Dialog>
          ) : (
            <>
              <Dialog open={isAddRequestDialogOpen} onOpenChange={setIsAddRequestDialogOpen}>
                <DialogTrigger asChild>
                  <Button variant="outline">
                    <Plus className="h-4 w-4 mr-2" />
                    Add Request
                  </Button>
                </DialogTrigger>
                <DialogContent className="max-w-2xl">
                  <DialogHeader>
                    <DialogTitle>Add Request to Recording</DialogTitle>
                    <DialogDescription>
                      Manually add an HTTP request and response to the current recording.
                    </DialogDescription>
                  </DialogHeader>
                  <div className="space-y-4 max-h-96 overflow-y-auto">
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <Label htmlFor="url">URL *</Label>
                        <Input
                          id="url"
                          value={newRequest.url}
                          onChange={(e) => setNewRequest({ ...newRequest, url: e.target.value })}
                          placeholder="https://example.com/api/endpoint"
                        />
                      </div>
                      <div>
                        <Label htmlFor="method">Method</Label>
                        <select
                          id="method"
                          value={newRequest.method}
                          onChange={(e) => setNewRequest({ ...newRequest, method: e.target.value })}
                          className="w-full px-3 py-2 border border-gray-300 rounded-md"
                        >
                          <option value="GET">GET</option>
                          <option value="POST">POST</option>
                          <option value="PUT">PUT</option>
                          <option value="DELETE">DELETE</option>
                          <option value="PATCH">PATCH</option>
                        </select>
                      </div>
                    </div>
                    <div>
                      <Label htmlFor="headers">Request Headers (JSON)</Label>
                      <Textarea
                        id="headers"
                        value={newRequest.headers}
                        onChange={(e) => setNewRequest({ ...newRequest, headers: e.target.value })}
                        placeholder='{"Content-Type": "application/json"}'
                        rows={3}
                      />
                    </div>
                    <div>
                      <Label htmlFor="body">Request Body</Label>
                      <Textarea
                        id="body"
                        value={newRequest.body}
                        onChange={(e) => setNewRequest({ ...newRequest, body: e.target.value })}
                        placeholder="Request body content"
                        rows={3}
                      />
                    </div>
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <Label htmlFor="response_status">Response Status</Label>
                        <Input
                          id="response_status"
                          type="number"
                          value={newRequest.response_status}
                          onChange={(e) => setNewRequest({ ...newRequest, response_status: e.target.value })}
                          placeholder="200"
                        />
                      </div>
                      <div>
                        <Label htmlFor="response_headers">Response Headers (JSON)</Label>
                        <Textarea
                          id="response_headers"
                          value={newRequest.response_headers}
                          onChange={(e) => setNewRequest({ ...newRequest, response_headers: e.target.value })}
                          placeholder='{"Content-Type": "application/json"}'
                          rows={2}
                        />
                      </div>
                    </div>
                    <div>
                      <Label htmlFor="response_content">Response Content</Label>
                      <Textarea
                        id="response_content"
                        value={newRequest.response_content}
                        onChange={(e) => setNewRequest({ ...newRequest, response_content: e.target.value })}
                        placeholder="Response body content"
                        rows={3}
                      />
                    </div>
                  </div>
                  <div className="flex justify-end space-x-2">
                    <Button variant="outline" onClick={() => setIsAddRequestDialogOpen(false)}>
                      Cancel
                    </Button>
                    <Button onClick={addRequest}>
                      Add Request
                    </Button>
                  </div>
                </DialogContent>
              </Dialog>
              <Button variant="destructive" onClick={stopRecording}>
                <Square className="h-4 w-4 mr-2" />
                Stop Recording
              </Button>
            </>
          )}
        </div>
      </div>

      {/* Recording Status */}
      <Card className={isRecording ? "border-red-200 bg-red-50" : "border-gray-200"}>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <div className={`w-3 h-3 rounded-full ${isRecording ? 'bg-red-500 animate-pulse' : 'bg-gray-400'}`}></div>
              <CardTitle className={isRecording ? "text-red-900" : "text-gray-900"}>
                Recording Status
              </CardTitle>
            </div>
            <Badge variant={isRecording ? "destructive" : "secondary"}>
              {isRecording ? "Recording" : "Stopped"}
            </Badge>
          </div>
        </CardHeader>
        <CardContent>
          {isRecording && currentFlow ? (
            <div className="space-y-2">
              <h3 className="font-semibold text-red-900">{currentFlow.name}</h3>
              {currentFlow.description && (
                <p className="text-red-700 text-sm">{currentFlow.description}</p>
              )}
              <div className="flex items-center space-x-4 text-sm text-red-600">
                {currentFlow.target_domain && (
                  <div className="flex items-center space-x-1">
                    <Globe className="h-4 w-4" />
                    <span>{currentFlow.target_domain}</span>
                  </div>
                )}
                <div className="flex items-center space-x-1">
                  <FileText className="h-4 w-4" />
                  <span>{requests.length} requests recorded</span>
                </div>
              </div>
            </div>
          ) : (
            <div className="text-center py-4">
              <AlertCircle className="h-12 w-12 mx-auto text-gray-400 mb-2" />
              <p className="text-gray-600">No active recording</p>
              <p className="text-sm text-gray-500">Start a new recording to capture HTTP requests</p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Recorded Requests */}
      <Card>
        <CardHeader>
          <CardTitle>Recorded Requests</CardTitle>
          <CardDescription>
            HTTP requests captured in the current or selected flow
          </CardDescription>
        </CardHeader>
        <CardContent>
          {requests.length > 0 ? (
            <div className="space-y-4">
              {requests.map((request, index) => (
                <div key={request.request_id} className="border rounded-lg p-4">
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center space-x-2">
                      <Badge variant="outline">{request.method}</Badge>
                      <span className="font-mono text-sm">{request.url}</span>
                    </div>
                    <div className="flex items-center space-x-2">
                      <Badge 
                        variant={request.response_status < 400 ? "default" : "destructive"}
                      >
                        {request.response_status}
                      </Badge>
                      <span className="text-xs text-gray-500">#{index + 1}</span>
                    </div>
                  </div>
                  <div className="flex items-center space-x-4 text-sm text-gray-600">
                    <div className="flex items-center space-x-1">
                      <FileText className="h-4 w-4" />
                      <span>{request.response_content_length || 0} bytes</span>
                    </div>
                    {request.timestamp && (
                      <div className="flex items-center space-x-1">
                        <Clock className="h-4 w-4" />
                        <span>{new Date(request.timestamp).toLocaleString()}</span>
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8">
              <FileText className="h-16 w-16 mx-auto text-gray-300 mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">No requests recorded</h3>
              <p className="text-gray-500 mb-4">
                {isRecording 
                  ? "Start making HTTP requests to capture them in this flow"
                  : "Select a flow or start recording to see captured requests"
                }
              </p>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}

