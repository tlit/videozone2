import torch
from diffusers import AutoPipelineForImage2Image, LCMScheduler
from diffusers.utils import load_image
import numpy as np
import cv2
from PIL import Image
import os

class AIPipeline:
    def __init__(self, model_id: str = "SimianLuo/LCM_Dreamshaper_v7", device: str = "cuda"):
        self.device = device
        self.model_id = model_id
        self.pipe = None
        self.loading_status = "IDLE"
        
    def load_model(self):
        print(f"Loading model: {self.model_id}...")
        try:
            self.loading_status = "CHECKING LOCAL PATH..."
            
            # 1. Check strict local path (from manual download script)
            local_model_path = r"c:\repos\videozone\models\SimianLuo\LCM_Dreamshaper_v7"
            
            if os.path.exists(local_model_path):
                 print(f"Found manual download at {local_model_path}")
                 
                 # Check if fp16 weights actually exist
                 unet_fp16 = os.path.join(local_model_path, "unet", "diffusion_pytorch_model.fp16.safetensors")
                 use_fp16_variant = os.path.exists(unet_fp16)
                 
                 # Force None for now to ensure standard loading
                 variant_arg = None 
                 # variant_arg = "fp16" if use_fp16_variant else None
                 
                 print(f"FP16 Weights Found: {use_fp16_variant}. Using variant={variant_arg}")

                 self.pipe = AutoPipelineForImage2Image.from_pretrained(
                    local_model_path, 
                    # torch_dtype=torch.float16, # Revert to fp32 for stability
                    variant=variant_arg,
                    local_files_only=True,
                    use_safetensors=True,
                    safety_checker=None
                )
            else:
                self.loading_status = "CHECKING HF CACHE..."
                # 2. Try standard HF Cache (Offline)
                try:
                    self.pipe = AutoPipelineForImage2Image.from_pretrained(
                        self.model_id, 
                        # torch_dtype=torch.float16,
                        variant="fp16",
                        local_files_only=True,
                        use_safetensors=True,
                        safety_checker=None
                    )
                    print("Model found in local HF cache.")
                except Exception as e:
                     print(f"Local cache miss: {e}")
                     raise e

            self.loading_status = "CONFIGURING SCHEDULER..."
            self.pipe.scheduler = LCMScheduler.from_config(self.pipe.scheduler.config)
            
            self.loading_status = "CONFIGURING SCHEDULER..."
            self.pipe.scheduler = LCMScheduler.from_config(self.pipe.scheduler.config)
            
            self.loading_status = "MOVING TO GPU..."
            self.loading_status = "MOVING TO GPU..."
            self.pipe.to(self.device)
            
            # Explicitly ensure all sub-models are on the correct device
            if hasattr(self.pipe, "text_encoder") and self.pipe.text_encoder:
                self.pipe.text_encoder.to(self.device)
            if hasattr(self.pipe, "unet") and self.pipe.unet:
                self.pipe.unet.to(self.device)
            if hasattr(self.pipe, "vae") and self.pipe.vae:
                self.pipe.vae.to(self.device)
            # self.pipe.enable_model_cpu_offload() # Caused input device mismatch
            
            self.loading_status = "OPTIMIZING MEMORY..."
            
            self.loading_status = "OPTIMIZING MEMORY..."
            # Enable memory optimizations
            # self.pipe.enable_attention_slicing() # Disable for now to debug device issue
            
            print("Model loaded successfully.")
            self.loading_status = "READY"
        except Exception as e:
            print(f"Failed to load model logic: {e}")
            self.loading_status = f"ERROR: {str(e)[:50]}..."
            self.pipe = None

    def generate(self, prompt: str, image: np.ndarray, strength: float = 0.3, guidance_scale: float = 8.0) -> np.ndarray:
        if self.pipe is None:
            # Fallback for when model isn't downloaded yet or fails
            # Just return the input image with some noise
            noise = np.random.randint(-5, 5, image.shape, dtype=np.int16)
            return np.clip(image.astype(np.int16) + noise, 0, 255).astype(np.uint8)

        # Convert CV2 (BGR) to PIL (RGB)
        pil_image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        
        # Inference
        result = self.pipe(
            prompt=prompt,
            image=pil_image,
            num_inference_steps=4, # Low steps for LCM
            guidance_scale=guidance_scale,
            strength=strength
        ).images[0]
        
        # Convert PIL (RGB) back to CV2 (BGR)
        return cv2.cvtColor(np.array(result), cv2.COLOR_RGB2BGR)
