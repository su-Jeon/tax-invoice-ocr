import sys

import ollama

PROMPT = "이 사진에서 '공급가액'에 해당하는 숫자만 답해줘. 다른 설명은 하지 말고 숫자만 답해."
MODELS_TO_TEST = ["qwen2.5vl:3b"]


def main(image_path):
    for model in MODELS_TO_TEST:
        print(f"\n===== {model} =====")
        response = ollama.chat(
            model=model,
            messages=[
                {
                    "role": "user",
                    "content": PROMPT,
                    "images": [image_path],
                }
            ],
            options={"num_ctx": 8192},
        )
        print(response["message"]["content"])


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("사용법: python test_vision.py 사진.jpg")
        sys.exit(1)
    main(sys.argv[1])
