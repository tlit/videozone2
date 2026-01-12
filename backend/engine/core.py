import asyncio
import numpy as np
import cv2
import time
from .transform import MotionEngine
from .pipeline import AIPipeline

class HallucinationEngine:
    def __init__(self):
        self.prompt = "A futuristic cyberpunk city, neon lights, fast motion"
        # 16:9 Aspect Ratio (YouTube Optimal)
        self.width = 912
        self.height = 512
        self.strength = 0.3
        self.guidance_scale = 8.0
        self.frame = self._initial_noise()
        self.running = False
        self.lock = asyncio.Lock()
        self.frame_count = 0
        self.last_gen_time = 0.0
        
        # Components
        self.motion = MotionEngine(zoom_factor=1.05)
        self.ai = AIPipeline() # Model loading happens on startup or separate thread
        
    def _initial_noise(self):
        return np.random.randint(0, 256, (self.height, self.width, 3), dtype=np.uint8)

    async def start(self):
        self.running = True
        print("Initializing AI Pipeline...")
        
        # Fire and forget model loading in a separate thread so it doesn't block startup
        asyncio.create_task(self._load_model_async())
        
        # Start the loop immediately
        asyncio.create_task(self._loop())

    async def _load_model_async(self):
        print("Starting Model Load in Background...")
        await asyncio.to_thread(self.ai.load_model)
        print("AI Pipeline Initialized (Background)")

    def update_prompt(self, prompt: str):
        print(f"Update Prompt: {prompt}")
        self.prompt = prompt

    def update_params(self, strength: float, guidance_scale: float):
        print(f"Update Params: strength={strength}, guidance={guidance_scale}")
        self.strength = strength
        self.guidance_scale = guidance_scale

    async def _loop(self):
        print("Engine Loop Started")
        self.status = "RUNNING"
        while self.running:
            start_time = time.time()
            
            async with self.lock:
                try:
                   # 1. Apply Motion (Zoom)
                   zoomed = self.motion.apply_zoom(self.frame)
                   
                   # 2. Generate Next Frame (Hallucinate)
                   # We use the zoomed frame as input for Img2Img
                   # If AI is slow, this will control the FPS. 
                   # For RTX 4090 with LCM, we expect ~10-20 FPS.
                   
                   # Run generation in thread pool to avoid blocking event loop
                   next_frame = await asyncio.to_thread(
                       self.ai.generate, 
                       prompt=self.prompt, 
                       image=zoomed,
                       strength=self.strength,
                       guidance_scale=self.guidance_scale
                   )
                   
                   self.frame = next_frame
                   self.frame_count += 1
                   self.last_gen_time = (time.time() - start_time) * 1000
                except Exception as e:
                   print(f"Error in loop: {e}")
                   self.status = f"ERROR: {e}"

            await asyncio.sleep(0.01) # Yield control

    def get_frame(self):
        # Return JPEG encoded frame for streaming
        if self.frame is not None:
             _, buffer = cv2.imencode('.jpg', self.frame)
             return buffer.tobytes()
        return None

    def get_status(self):
        return {
            "status": getattr(self, "status", "INITIALIZING"),
            "prompt": self.prompt,
            "frame_count": getattr(self, "frame_count", 0),
            "last_gen_time_ms": getattr(self, "last_gen_time", 0),
            "model_loaded": self.ai.pipe is not None,
            "loading_state": getattr(self.ai, "loading_status", "UNKNOWN"),
            "device": str(self.ai.device),
            "strength": self.strength,
            "guidance_scale": self.guidance_scale
        }
