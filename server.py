
import io
from fastapi import FastAPI, File, Form, UploadFile
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from transformers import AutoProcessor, AutoModelForImageTextToText
from PIL import Image
import torch

app = FastAPI()

# Global variables for model
model = None
processor = None
MODEL_ID = "LiquidAI/LFM2.5-VL-1.6B"

@app.on_event("startup")
async def startup_event():
    global model, processor
    print("Loading model...")
    # Load model with bfloat16 as per original script
    model = AutoModelForImageTextToText.from_pretrained(
        MODEL_ID,
        device_map="auto",
        dtype="bfloat16",
        trust_remote_code=True,
    )
    processor = AutoProcessor.from_pretrained(
        MODEL_ID,
        trust_remote_code=True,
    )
    print("Model loaded.")

@app.post("/analyze")
async def analyze(
    image: UploadFile = File(...),
    prompt: str = Form(...)
):
    try:
        # Read image
        contents = await image.read()
        pil_image = Image.open(io.BytesIO(contents)).convert("RGB")
        
        conversation = [
            {
                "role": "user",
                "content": [
                    {"type": "image", "image": pil_image},
                    {"type": "text", "text": prompt},
                ],
            },
        ]
        
        inputs = processor.apply_chat_template(
            conversation,
            add_generation_prompt=True,
            return_tensors="pt",
            return_dict=True,
            tokenize=True,
        ).to(model.device)
        
        # Generate
        outputs = model.generate(**inputs, max_new_tokens=64)
        generated_ids = outputs[:, inputs.input_ids.shape[1]:]
        result = processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
        
        return {"result": result}
    except Exception as e:
        print(f"Error during analysis: {e}")
        return JSONResponse(content={"error": str(e)}, status_code=500)

if __name__ == "__main__":
    import uvicorn
    # Mount static LAST so that API routes take precedence, though unrelated here as /analyze is distinct
    # But we want to serve index.html at root, which StaticFiles(html=True) handles if mapped to "/"
    app.mount("/", StaticFiles(directory="static", html=True), name="static")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
