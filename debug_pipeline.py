from backend.engine.pipeline import AIPipeline
import numpy as np
import cv2

try:
    print("Initializing Pipeline...")
    ai = AIPipeline()
    ai.load_model()
    
    print(f"Pipeline Device: {ai.pipe.device}")
    print(f"UNet Device: {ai.pipe.unet.device}")
    
    # Test Generation
    print("Testing Generation...")
    img = np.random.randint(0, 255, (512, 912, 3), dtype=np.uint8)
    res = ai.generate("test prompt", img)
    print("Generation Success!")
except Exception as e:
    print(f"CRITICAL ERROR: {e}")
    import traceback
    traceback.print_exc()
