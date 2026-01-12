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
    spark_active?: boolean;
}

export interface AntigravityActions {
    injectPrompt: (prompt: string) => Promise<boolean>;
    pingBackend: () => Promise<boolean>;
    updateParams: (params: { strength: number; guidance: number }) => Promise<boolean>;
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
                },
                updateParams: async (params: { strength: number; guidance: number }) => {
                    try {
                        const res = await fetch('http://localhost:8000/update_params', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({ strength: params.strength, guidance_scale: params.guidance })
                        });
                        return res.ok;
                    } catch (e) {
                        console.error("Failed to update params:", e);
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
