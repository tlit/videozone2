import React, { useEffect, useState } from 'react';

interface DebugStatus {
    status: string;
    prompt: string;
    frame_count: number;
    last_gen_time_ms: number;
    model_loaded: boolean;
    loading_state: string; // New field
    device: string;
}

export const DebugConsole: React.FC = () => {
    const [debugData, setDebugData] = useState<DebugStatus | null>(null);

    useEffect(() => {
        const interval = setInterval(async () => {
            try {
                const res = await fetch('http://localhost:8000/debug/status');
                if (res.ok) {
                    const data = await res.json();
                    setDebugData(data);
                }
            } catch (err) {
                console.error("Debug fetch failed", err);
            }
        }, 1000); // Poll every second

        return () => clearInterval(interval);
    }, []);

    if (!debugData) return null;

    return (
        <div className="fixed top-4 right-4 bg-black/80 backdrop-blur border border-red-500/30 p-4 rounded font-mono text-xs text-red-400 w-64 shadow-lg pointer-events-none z-50">
            <h3 className="font-bold border-b border-red-500/30 mb-2 pb-1">DEBUG_OVERLAY</h3>
            <div className="space-y-1">
                <div className="flex justify-between">
                    <span>STATUS:</span>
                    <span className={debugData.status.startsWith("ERROR") ? "text-red-500 font-bold" : "text-green-400"}>
                        {debugData.status}
                    </span>
                </div>
                <div className="flex justify-between">
                    <span>MODEL:</span>
                    <span className={debugData.model_loaded ? "text-green-400" : "text-yellow-400 blink"}>
                        {debugData.model_loaded ? "LOADED" : debugData.loading_state}
                    </span>
                </div>
                <div className="flex justify-between">
                    <span>DEVICE:</span>
                    <span>{debugData.device}</span>
                </div>
                <div className="flex justify-between">
                    <span>FRAMES:</span>
                    <span>{debugData.frame_count}</span>
                </div>
                <div className="flex justify-between">
                    <span>GEN_TIME:</span>
                    <span>{debugData.last_gen_time_ms.toFixed(1)}ms</span>
                </div>
                <div className="flex justify-between">
                    <span>FPS:</span>
                    <span>{debugData.last_gen_time_ms > 0 ? (1000 / debugData.last_gen_time_ms).toFixed(1) : "0.0"}</span>
                </div>
            </div>
            <div className="mt-2 text-[10px] text-gray-500 break-words">
                PROMPT: {debugData.prompt}
            </div>
        </div>
    );
};
