import re
import sys

import ollama

MODEL = "qwen2.5vl:3b"
PROMPT = (
    "이 세금계산서 사진에서 '공급가액'과 '세액'에 해당하는 숫자를 각각 찾아줘. "
    "다른 설명 없이 정확히 이 형식으로만 답해: 공급가액=숫자,세액=숫자"
)
TAX_RATE = 0.1
TOLERANCE = 0.05  # 세액이 공급가액의 10%에서 이만큼(5%)까지 벗어나면 정상으로 봄


def extract_text(image_path):
    response = ollama.chat(
        model=MODEL,
        messages=[
            {
                "role": "user",
                "content": PROMPT,
                "images": [image_path],
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


def main(image_paths):
    print(f"총 {len(image_paths)}장 처리 시작\n")

    total = 0
    need_check = []

    for path in image_paths:
        raw_text = extract_text(path)
        supply = parse_field(raw_text, "공급가액")
        tax = parse_field(raw_text, "세액")

        if supply is None:
            print(f"[실패] {path} -> 모델 응답: '{raw_text}'")
            need_check.append(path)
            continue

        expected_tax = supply * TAX_RATE
        is_consistent = tax is not None and abs(tax - expected_tax) <= max(1, expected_tax * TOLERANCE)
        status = "OK" if is_consistent else "확인 필요"

        tax_display = f"{tax:,}" if tax is not None else "?"
        print(f"[{path}] 공급가액: {supply:,}원 / 세액: {tax_display}원 -> {status}")

        if not is_consistent:
            need_check.append(path)

        total += supply

    print(f"\n합계(자동 추출 기준): {total:,}원")
    if need_check:
        print(f"주의: 아래 {len(need_check)}장은 원본과 대조가 필요해 -> {need_check}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("사용법: python calculate_total.py 사진1.jpg 사진2.jpg ...")
        sys.exit(1)
    main(sys.argv[1:])
