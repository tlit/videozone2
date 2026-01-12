import { useState } from 'react'
import { VideoPlayer } from './components/VideoPlayer'
import { CommandCenter } from './components/CommandCenter'
import { DebugConsole } from './components/DebugConsole'
import { AntigravityBridge } from './components/AntigravityBridge'
import './App.css'

function App() {
  const [streamUrl] = useState('http://localhost:8000/video_feed')
  const [lastPrompt, setLastPrompt] = useState('')

  const handlePromptUpdate = async (prompt: string) => {
    try {
      const url = new URL('http://localhost:8000/update_prompt');
      url.searchParams.append('prompt', prompt);

      const response = await fetch(url.toString(), {
        method: 'POST',
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      setLastPrompt(prompt); // Track valid prompt
      return true; // Indicate success
    } catch (error) {
      console.error('Failed to update prompt:', error);
      return false;
    }
  }

  return (
    <div className="min-h-screen bg-black text-white p-8 flex flex-col items-center justify-center font-sans selection:bg-cyan-500 selection:text-black">
      <DebugConsole />
      <div className="max-w-4xl w-full">
        <header className="mb-8 flex justify-between items-end border-b border-gray-800 pb-4">
          <div>
            <h1 className="text-4xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-cyan-400 to-purple-600">
              VIDEOZONE
            </h1>
            <p className="text-gray-500 text-sm font-mono mt-1">INFINITE HALLUCINATION ENGINE // RTX4090 OPTIMIZED</p>
          </div>
          <div className="text-right">
            <div className="text-xs text-green-500 font-mono">SYSTEM: ONLINE</div>
            <div className="text-xs text-gray-600 font-mono">LATENCY: 12ms</div>
          </div>
        </header>

        <main>
          <VideoPlayer streamUrl={streamUrl} />
          <CommandCenter onPromptUpdate={handlePromptUpdate} />
          <AntigravityBridge
            prompt={lastPrompt}
            streamUrl={streamUrl}
            onPromptInject={handlePromptUpdate}
          />
        </main>
      </div>
    </div>
  )
}

export default App
