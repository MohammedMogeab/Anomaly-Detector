import { useState, useEffect } from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { Toaster } from '@/components/ui/sonner'
import Sidebar from './components/Sidebar'
import Dashboard from './components/Dashboard'
import FlowManager from './components/FlowManager'
import RecordingInterface from './components/RecordingInterface'
import PayloadGenerator from './components/PayloadGenerator'
import ReplayInterface from './components/ReplayInterface'
import AnalysisResults from './components/AnalysisResults'
import ReportsView from './components/ReportsView'
import './App.css'

function App() {
  const [currentFlow, setCurrentFlow] = useState(null)
  const [isRecording, setIsRecording] = useState(false)

  // Check recording status on app load
  useEffect(() => {
    checkRecordingStatus()
  }, [])

  const checkRecordingStatus = async () => {
    try {
      const response = await fetch('/api/recording/status')
      const data = await response.json()
      setIsRecording(data.is_recording)
      if (data.current_flow_id) {
        // Fetch current flow details
        const flowResponse = await fetch(`/api/flows/${data.current_flow_id}`)
        if (flowResponse.ok) {
          const flowData = await flowResponse.json()
          setCurrentFlow(flowData)
        }
      }
    } catch (error) {
      console.error('Failed to check recording status:', error)
    }
  }

  return (
    <Router>
      <div className="flex h-screen bg-gray-50">
        <Sidebar currentFlow={currentFlow} isRecording={isRecording} />
        <main className="flex-1 overflow-auto">
          <Routes>
            <Route path="/" element={<Navigate to="/dashboard" replace />} />
            <Route path="/dashboard" element={<Dashboard />} />
            <Route 
              path="/flows" 
              element={
                <FlowManager 
                  currentFlow={currentFlow} 
                  setCurrentFlow={setCurrentFlow} 
                />
              } 
            />
            <Route 
              path="/recording" 
              element={
                <RecordingInterface 
                  isRecording={isRecording}
                  setIsRecording={setIsRecording}
                  currentFlow={currentFlow}
                  setCurrentFlow={setCurrentFlow}
                  onRecordingStatusChange={checkRecordingStatus}
                />
              } 
            />
            <Route 
              path="/payloads" 
              element={<PayloadGenerator currentFlow={currentFlow} />} 
            />
            <Route 
              path="/replay" 
              element={<ReplayInterface currentFlow={currentFlow} />} 
            />
            <Route 
              path="/analysis" 
              element={<AnalysisResults currentFlow={currentFlow} />} 
            />
            <Route 
              path="/reports" 
              element={<ReportsView currentFlow={currentFlow} />} 
            />
          </Routes>
        </main>
        <Toaster />
      </div>
    </Router>
  )
}

export default App

