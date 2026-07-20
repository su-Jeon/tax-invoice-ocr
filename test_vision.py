import ollama

IMAGE_PATH = r"C:\Users\PC001\Desktop\전승욱\세금계산서 사진\KakaoTalk_20260720_131744150_01.jpg"
PROMPT = "이 사진에서 '공급가액'에 해당하는 숫자만 답해줘. 다른 설명은 하지 말고 숫자만 답해."

MODELS_TO_TEST = ["qwen2.5vl:3b"]

for model in MODELS_TO_TEST:
    print(f"\n===== {model} =====")
    response = ollama.chat(
        model=model,
        messages=[
            {
                "role": "user",
                "content": PROMPT,
                "images": [IMAGE_PATH],
            }
        ],
        options={"num_ctx": 8192},
    )
    print(response["message"]["content"])
