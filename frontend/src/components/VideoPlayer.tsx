import React from 'react';

interface VideoPlayerProps {
    streamUrl: string;
}

export const VideoPlayer: React.FC<VideoPlayerProps> = ({ streamUrl }) => {
    return (
        <div className="relative w-full aspect-video bg-black rounded-lg overflow-hidden border-2 border-cyan-500 shadow-[0_0_20px_rgba(6,182,212,0.5)]">
            <img
                src={streamUrl}
                alt="Live Hallucination Feed"
                className="w-full h-full object-cover"
            />
            <div className="absolute top-4 left-4 text-cyan-500 font-mono text-sm animate-pulse">
                LIVE FEED // NEURAL_LINK_ACTIVE
            </div>
        </div>
    );
};
