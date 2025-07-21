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
  Plus, 
  Folder, 
  Calendar, 
  Globe, 
  FileText,
  Trash2,
  Eye
} from 'lucide-react'

export default function FlowManager({ currentFlow, setCurrentFlow }) {
  const [flows, setFlows] = useState([])
  const [loading, setLoading] = useState(true)
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false)
  const [newFlow, setNewFlow] = useState({
    name: '',
    description: '',
    target_domain: ''
  })
  const { toast } = useToast()

  useEffect(() => {
    fetchFlows()
  }, [])

  const fetchFlows = async () => {
    try {
      setLoading(true)
      const response = await fetch('/api/flows')
      if (response.ok) {
        const data = await response.json()
        setFlows(data)
      } else {
        throw new Error('Failed to fetch flows')
      }
    } catch (error) {
      console.error('Error fetching flows:', error)
      toast({
        title: "Error",
        description: "Failed to fetch flows",
        variant: "destructive",
      })
    } finally {
      setLoading(false)
    }
  }

  const createFlow = async () => {
    if (!newFlow.name.trim()) {
      toast({
        title: "Error",
        description: "Flow name is required",
        variant: "destructive",
      })
      return
    }

    try {
      const response = await fetch('/api/flows', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(newFlow),
      })

      if (response.ok) {
        const data = await response.json()
        toast({
          title: "Success",
          description: "Flow created successfully",
        })
        setIsCreateDialogOpen(false)
        setNewFlow({ name: '', description: '', target_domain: '' })
        fetchFlows()
      } else {
        const error = await response.json()
        throw new Error(error.error || 'Failed to create flow')
      }
    } catch (error) {
      console.error('Error creating flow:', error)
      toast({
        title: "Error",
        description: error.message,
        variant: "destructive",
      })
    }
  }

  const selectFlow = async (flow) => {
    try {
      const response = await fetch(`/api/flows/${flow.flow_id}`)
      if (response.ok) {
        const data = await response.json()
        setCurrentFlow(data)
        toast({
          title: "Flow Selected",
          description: `Selected flow: ${data.name}`,
        })
      }
    } catch (error) {
      console.error('Error selecting flow:', error)
      toast({
        title: "Error",
        description: "Failed to select flow",
        variant: "destructive",
      })
    }
  }

  if (loading) {
    return (
      <div className="p-8">
        <div className="animate-pulse space-y-6">
          <div className="h-8 bg-gray-200 rounded w-1/4"></div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[...Array(6)].map((_, i) => (
              <div key={i} className="h-48 bg-gray-200 rounded"></div>
            ))}
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="p-8 space-y-8">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Flow Manager</h1>
          <p className="text-gray-600 mt-2">
            Manage your testing flows and select active flow
          </p>
        </div>
        <Dialog open={isCreateDialogOpen} onOpenChange={setIsCreateDialogOpen}>
          <DialogTrigger asChild>
            <Button>
              <Plus className="h-4 w-4 mr-2" />
              Create Flow
            </Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Create New Flow</DialogTitle>
              <DialogDescription>
                Create a new testing flow to organize your anomaly detection activities.
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
                <Button variant="outline" onClick={() => setIsCreateDialogOpen(false)}>
                  Cancel
                </Button>
                <Button onClick={createFlow}>
                  Create Flow
                </Button>
              </div>
            </div>
          </DialogContent>
        </Dialog>
      </div>

      {/* Current Flow */}
      {currentFlow && (
        <Card className="border-blue-200 bg-blue-50">
          <CardHeader>
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <div className="w-3 h-3 bg-blue-500 rounded-full"></div>
                <CardTitle className="text-blue-900">Current Active Flow</CardTitle>
              </div>
              <Badge variant="secondary">Active</Badge>
            </div>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              <h3 className="font-semibold text-blue-900">{currentFlow.name}</h3>
              {currentFlow.description && (
                <p className="text-blue-700 text-sm">{currentFlow.description}</p>
              )}
              <div className="flex items-center space-x-4 text-sm text-blue-600">
                {currentFlow.target_domain && (
                  <div className="flex items-center space-x-1">
                    <Globe className="h-4 w-4" />
                    <span>{currentFlow.target_domain}</span>
                  </div>
                )}
                <div className="flex items-center space-x-1">
                  <FileText className="h-4 w-4" />
                  <span>{currentFlow.request_count} requests</span>
                </div>
                {currentFlow.timestamp && (
                  <div className="flex items-center space-x-1">
                    <Calendar className="h-4 w-4" />
                    <span>{new Date(currentFlow.timestamp).toLocaleDateString()}</span>
                  </div>
                )}
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Flows Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {flows.length > 0 ? (
          flows.map((flow) => (
            <Card 
              key={flow.flow_id} 
              className={`cursor-pointer transition-all hover:shadow-md ${
                currentFlow?.flow_id === flow.flow_id ? 'ring-2 ring-blue-500' : ''
              }`}
              onClick={() => selectFlow(flow)}
            >
              <CardHeader>
                <div className="flex items-center justify-between">
                  <CardTitle className="text-lg flex items-center space-x-2">
                    <Folder className="h-5 w-5 text-blue-500" />
                    <span className="truncate">{flow.name}</span>
                  </CardTitle>
                  {currentFlow?.flow_id === flow.flow_id && (
                    <Badge variant="default">Active</Badge>
                  )}
                </div>
                {flow.description && (
                  <CardDescription className="line-clamp-2">
                    {flow.description}
                  </CardDescription>
                )}
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-500">Requests:</span>
                    <Badge variant="secondary">{flow.request_count}</Badge>
                  </div>
                  {flow.target_domain && (
                    <div className="flex items-center space-x-2 text-sm">
                      <Globe className="h-4 w-4 text-gray-400" />
                      <span className="text-gray-600 truncate">{flow.target_domain}</span>
                    </div>
                  )}
                  {flow.timestamp && (
                    <div className="flex items-center space-x-2 text-sm">
                      <Calendar className="h-4 w-4 text-gray-400" />
                      <span className="text-gray-600">
                        {new Date(flow.timestamp).toLocaleDateString()}
                      </span>
                    </div>
                  )}
                  <div className="flex justify-between items-center pt-2">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={(e) => {
                        e.stopPropagation()
                        selectFlow(flow)
                      }}
                    >
                      <Eye className="h-4 w-4 mr-1" />
                      Select
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))
        ) : (
          <div className="col-span-full text-center py-12">
            <Folder className="h-16 w-16 mx-auto text-gray-300 mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No flows yet</h3>
            <p className="text-gray-500 mb-4">
              Create your first flow to start testing for business logic anomalies
            </p>
            <Button onClick={() => setIsCreateDialogOpen(true)}>
              <Plus className="h-4 w-4 mr-2" />
              Create Your First Flow
            </Button>
          </div>
        )}
      </div>
    </div>
  )
}

