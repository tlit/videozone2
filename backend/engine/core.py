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
        self.strength = 0.25
        self.guidance_scale = 8.0
        self.frame = self._initial_noise()
        self.running = False
        self.lock = asyncio.Lock()
        self.frame_count = 0
        self.last_gen_time = 0.0
        
        # Components
        self.motion = MotionEngine(zoom_factor=1.05)
        self.ai = AIPipeline() # Model loading happens on startup or separate thread
        
        # Subconscious Seeding State
        self.last_spark_frame = 0
        self.spark_active = False
        self.current_seed_img = None
        self.seed_progress = 0
        self.SEED_DURATION = 20 # Frames to grow the seed

    def _check_stagnation(self, frame):
        """Detects if the hallucination has faded into darkness or uniformity."""
        # Convert to grayscale for simple brightness check
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        mean_brightness = np.mean(gray)
        
        # Threshold: < 40 brightness is too dark (8-bit scale)
        is_stagnant = mean_brightness < 40
        return is_stagnant, mean_brightness

    def _generate_seed(self):
        """Generates a high-strength 'pure' hallucination to re-seed the dream."""
        print("Spark Ignited: Generating Seed...")
        # Create a blank noise canvas
        noise = np.random.randint(0, 256, (512, 512, 3), dtype=np.uint8)
        
        # Generate at high strength (0.95) to act almost like txt2img
        # We use a square 512x512 for the seed
        seed_img = self.ai.generate(
            prompt=self.prompt,
            image=noise,
            strength=0.95,
            guidance_scale=8.5 # Slightly higher guidance for clarity
        )
        return seed_img

    def _inject_seed(self, current_frame, seed_img, progress_factor):
        """Softly blends the seed into the center of the frame, growing over time."""
        h, w = current_frame.shape[:2]
        
        # 1. Calculate size based on progress (Linear growth 10% -> 80%)
        # progress_factor is 0.0 to 1.0
        min_size = int(h * 0.1)
        max_size = int(h * 0.8)
        
        current_size = int(min_size + (max_size - min_size) * progress_factor)
        
        # Resize seed
        seed_small = cv2.resize(seed_img, (current_size, current_size))
        
        # 2. Create a soft radial alpha mask
        # Create a linear gradient from center
        Y, X = np.ogrid[:current_size, :current_size]
        center = current_size / 2.0
        dist_from_center = np.sqrt((X - center)**2 + (Y - center)**2)
        
        # Gaussian falloff - sigma scales with size
        sigma = current_size / 3.0
        mask = np.exp(-(dist_from_center**2) / (2 * sigma**2))
        mask = np.dstack([mask] * 3) # 3 channels
        
        # 3. Position in center of frame
        y_offset = (h - current_size) // 2
        x_offset = (w - current_size) // 2
        
        # 4. Alpha Blend
        roi = current_frame[y_offset:y_offset+current_size, x_offset:x_offset+current_size]
        
        # blended = src * mask + dst * (1 - mask)
        blended = (seed_small * mask + roi * (1.0 - mask)).astype(np.uint8)
        
        # Put it back
        current_frame[y_offset:y_offset+current_size, x_offset:x_offset+current_size] = blended
        
        return current_frame
        
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
                   
                   # 1.5 Subconscious Seeding (Anti-Stagnation)
                   is_stagnant, brightness = self._check_stagnation(zoomed)
                   
                   # Igniter Logic
                   if is_stagnant and (self.frame_count - self.last_spark_frame > 30) and not self.spark_active:
                       print(f"Stagnation Detected (Brightness: {brightness:.1f}). Igniting Spark.")
                       self.spark_active = True
                       self.last_spark_frame = self.frame_count
                       self.seed_progress = 0
                       # Generate Seed (This blocks briefly, but acceptable for a "reset")
                       self.current_seed_img = await asyncio.to_thread(self._generate_seed)

                   # Seeding Logic (Multi-frame)
                   if self.spark_active:
                       self.seed_progress += 1
                       progress_factor = self.seed_progress / self.SEED_DURATION
                       
                       # Inject Suggestion
                       if self.current_seed_img is not None:
                           zoomed = self._inject_seed(zoomed, self.current_seed_img, progress_factor)
                           
                       # End Seeding
                       if self.seed_progress >= self.SEED_DURATION:
                           print("Spark Complete. Releasing control to AI.")
                           self.spark_active = False
                           self.current_seed_img = None

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
            "guidance_scale": self.guidance_scale,
            "spark_active": getattr(self, "spark_active", False)
        }
