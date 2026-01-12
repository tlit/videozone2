from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from backend.engine.core import HallucinationEngine
import asyncio

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Engine
engine = HallucinationEngine()

@app.on_event("startup")
async def startup_event():
    await engine.start()

@app.get("/")
def read_root():
    return {"message": "VideoZone Engine Online", "prompt": engine.prompt}

@app.post("/update_prompt")
def update_prompt(prompt: str):
    engine.update_prompt(prompt)
    return {"status": "Prompt updated", "prompt": prompt}

@app.get("/debug/status")
def debug_status():
    return engine.get_status()

def generate_stream():
    while True:
        frame_bytes = engine.get_frame()
        if frame_bytes:
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
        # Cap FPS for streaming (consumer side) if needed, but engine controls generation rate
        import time
        time.sleep(0.01)

@app.get("/video_feed")
def video_feed():
    return StreamingResponse(generate_stream(), media_type="multipart/x-mixed-replace; boundary=frame")

