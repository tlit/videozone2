import React, { useState } from 'react';

interface CommandCenterProps {
    onPromptUpdate: (prompt: string) => Promise<boolean>;
}

export const CommandCenter: React.FC<CommandCenterProps> = ({ onPromptUpdate }) => {
    const [prompt, setPrompt] = useState('');
    const [status, setStatus] = useState<'IDLE' | 'INJECTING' | 'SUCCESS' | 'ERROR'>('IDLE');

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (prompt.trim() && status !== 'INJECTING') {
            setStatus('INJECTING');
            const success = await onPromptUpdate(prompt);

            if (success) {
                setStatus('SUCCESS');
                setPrompt(''); // Clear input
                setTimeout(() => setStatus('IDLE'), 2000); // Reset after delay
            } else {
                setStatus('ERROR');
                setTimeout(() => setStatus('IDLE'), 3000);
            }
        }
    };

    return (
        <div className="mt-6 p-4 bg-gray-900/80 backdrop-blur border border-purple-500/50 rounded-xl relative overflow-hidden transition-colors duration-500">
            {/* Status Overlay/Border Effect */}
            <div className={`absolute inset-0 pointer-events-none transition-opacity duration-500 ${status === 'SUCCESS' ? 'bg-green-500/10 border-2 border-green-500' :
                    status === 'ERROR' ? 'bg-red-500/10 border-2 border-red-500' : 'opacity-0'
                }`} />

            <h2 className="text-purple-400 font-mono text-lg mb-2 flex justify-between">
                <span>NEURAL OVERRIDE</span>
                {status === 'INJECTING' && <span className="text-cyan-400 animate-pulse">TRANSMITTING...</span>}
                {status === 'SUCCESS' && <span className="text-green-400">ACCEPTED</span>}
                {status === 'ERROR' && <span className="text-red-400">FAILURE</span>}
            </h2>
            <form onSubmit={handleSubmit} className="flex gap-4 relative z-10">
                <input
                    type="text"
                    value={prompt}
                    onChange={(e) => setPrompt(e.target.value)}
                    placeholder="Inject dream parameters..."
                    className="flex-1 bg-black/50 border border-gray-700 rounded px-4 py-2 text-cyan-300 placeholder-gray-600 focus:outline-none focus:border-cyan-500 font-mono"
                    disabled={status === 'INJECTING'}
                />
                <button
                    type="submit"
                    disabled={status === 'INJECTING'}
                    className={`px-6 py-2 font-bold rounded transition-all shadow-[0_0_15px_rgba(139,92,246,0.5)] ${status === 'INJECTING' ? 'bg-gray-700 text-gray-400 cursor-not-allowed' :
                            'bg-gradient-to-r from-purple-600 to-cyan-600 text-white hover:from-purple-500 hover:to-cyan-500'
                        }`}
                >
                    {status === 'INJECTING' ? '...' : 'INJECT'}
                </button>
            </form>
        </div>
    );
};
