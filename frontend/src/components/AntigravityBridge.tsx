import React, { useEffect } from 'react';

// Define the global window interface extension
declare global {
    interface Window {
        __ANTIGRAVITY__?: {
            getState: () => AntigravityState;
            actions: AntigravityActions;
            timestamp: number;
        };
    }
}

export interface AntigravityState {
    status: string;
    lastPrompt: string;
    streamUrl: string;
    backendConnected: boolean;
}

export interface AntigravityActions {
    injectPrompt: (prompt: string) => Promise<boolean>;
    pingBackend: () => Promise<boolean>;
}

interface AntigravityBridgeProps {
    prompt: string;
    streamUrl: string;
    onPromptInject: (prompt: string) => Promise<boolean>;
}

export const AntigravityBridge: React.FC<AntigravityBridgeProps> = ({
    prompt,
    streamUrl,
    onPromptInject
}) => {
    
    useEffect(() => {
        // Mount the bridge
        window.__ANTIGRAVITY__ = {
            timestamp: Date.now(),
            getState: () => ({
                status: 'ACTIVE',
                lastPrompt: prompt,
                streamUrl: streamUrl,
                backendConnected: true // Simplification for now, could be passed in
            }),
            actions: {
                injectPrompt: async (newPrompt: string) => {
                    console.log(`[Antigravity] Injecting prompt: ${newPrompt}`);
                    return await onPromptInject(newPrompt);
                },
                pingBackend: async () => {
                    try {
                        const res = await fetch('http://localhost:8000/debug/status');
                        return res.ok;
                    } catch (e) {
                        return false;
                    }
                }
            }
        };

        // Cleanup
        return () => {
            delete window.__ANTIGRAVITY__;
        };
    }, [prompt, streamUrl, onPromptInject]);

    // Render nothing visually, or a tiny indicator in dev mode
    return null;
};
