import React, { useEffect, useRef } from 'react'
import { useUIStore } from './store/useUIStore'
import { useConnectionStore } from './store/useConnectionStore'
import { useWebSocket } from './hooks/useWebSocket'
import WebcamFeed from './components/WebcamFeed'
import PredictionPanel from './components/PredictionPanel'
import SentenceBuilder from './components/SentenceBuilder'
import Header from './components/Header'
import HistoryPanel from './components/HistoryPanel'

function App() {
  const darkMode = useUIStore((state) => state.darkMode);
  const connectionStatus = useConnectionStore((state) => state.status);
  
  const { sendFrame, sendControlAction } = useWebSocket();
  const webcamRef = useRef(null);

  // Apply dark mode
  useEffect(() => {
    if (darkMode) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [darkMode]);

  // Capture loop
  useEffect(() => {
    let intervalId;
    
    // Only capture if connected to WebSocket
    if (connectionStatus === 'connected') {
      intervalId = setInterval(async () => {
        if (webcamRef.current) {
          const blob = await webcamRef.current.captureFrame();
          if (blob) {
            sendFrame(blob);
          }
        }
      }, 250);
    }
    
    return () => {
      if (intervalId) clearInterval(intervalId);
    };
  }, [connectionStatus, sendFrame]);

  return (
    <div className="min-h-screen bg-bg flex flex-col">
      <Header />
      
      <main className="flex-1 px-6 py-6 md:px-10 lg:px-16 flex flex-col items-center">
        <div className="w-full flex flex-col gap-6">
          
          {/* Top Row: Camera (~70%) and Prediction (~30%) */}
          <div className="flex flex-col lg:flex-row gap-6 h-auto lg:h-[600px]">
          
          {/* Webcam Container */}
          <div className="w-full lg:w-[70%] h-[400px] sm:h-[500px] lg:h-full relative">
            <WebcamFeed ref={webcamRef} />
          </div>
          
          {/* Prediction Panel */}
          <div className="w-full lg:w-[30%] h-[400px] lg:h-full">
            <PredictionPanel />
          </div>
          
        </div>
        
        {/* Bottom Row: Sentence Builder */}
        <div className="w-full">
          <SentenceBuilder sendControlAction={sendControlAction} />
        </div>
        
        {/* History Panel */}
        <HistoryPanel />
        
        </div>
      </main>
    </div>
  )
}

export default App
