import re

import ollama

MODEL = "qwen2.5vl:3b"
PROMPT = (
    "이 세금계산서 사진에서 '공급가액'과 '세액'에 해당하는 숫자를 각각 찾아줘. "
    "다른 설명 없이 정확히 이 형식으로만 답해: 공급가액=숫자,세액=숫자"
)
TAX_RATE = 0.1
TOLERANCE = 0.05  # 세액이 공급가액의 10%에서 이만큼(5%)까지 벗어나면 정상으로 봄


def extract_text(image_source):
    """image_source: 파일 경로(str) 또는 이미지 bytes"""
    response = ollama.chat(
        model=MODEL,
        messages=[
            {
                "role": "user",
                "content": PROMPT,
                "images": [image_source],
            }
        ],
        options={"num_ctx": 8192},
    )
    return response["message"]["content"]


def parse_field(text, label):
    match = re.search(rf"{label}\s*=?\s*([\d,]+)", text)
    if not match:
        return None
    return int(match.group(1).replace(",", ""))


def process_image(image_source):
    """사진 하나를 처리해서 (공급가액, 세액, 비율이 맞는지)를 반환"""
    raw_text = extract_text(image_source)
    supply = parse_field(raw_text, "공급가액")
    tax = parse_field(raw_text, "세액")

    if supply is None:
        return None, None, False

    expected_tax = supply * TAX_RATE
    is_consistent = tax is not None and abs(tax - expected_tax) <= max(1, expected_tax * TOLERANCE)
    return supply, tax, is_consistent
