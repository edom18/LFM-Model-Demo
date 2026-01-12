from transformers import AutoProcessor, AutoModelForImageTextToText
from transformers.image_utils import load_image

model_id = "LiquidAI/LFM2.5-VL-1.6B"
model = AutoModelForImageTextToText.from_pretrained(
    model_id,
    device_map="auto",
    dtype="bfloat16",
    trust_remote_code=True,
)
processor = AutoProcessor.from_pretrained(
    model_id,
    trust_remote_code=True,
)

url = "https://cdn.britannica.com/61/93061-050-99147DCE/Statue-of-Liberty-Island-New-York-Bay.jpg"
image = load_image(url)
conversation =[
    {
        "role": "user",
        "content": [
            {
                "type": "image",
                "image": image,
            },
            {
                "type": "text",
                "text": "この写真にはなにが写っていますか？",
            }
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
outputs = model.generate(**inputs, max_new_tokens=64)
result = processor.batch_decode(outputs, skip_special_tokens=True)[0]
print(result)