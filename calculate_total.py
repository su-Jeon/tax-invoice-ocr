import sys

from ocr_core import process_image


def main(image_paths):
    print(f"총 {len(image_paths)}장 처리 시작\n")

    total = 0
    supply_by_path = {}
    need_check = []

    for path in image_paths:
        supply, tax, is_consistent = process_image(path)

        if supply is None:
            print(f"[실패] {path} -> 숫자를 못 찾음")
            need_check.append(path)
            continue

        status = "OK" if is_consistent else "확인 필요"
        tax_display = f"{tax:,}" if tax is not None else "?"
        print(f"[{path}] 공급가액: {supply:,}원 / 세액: {tax_display}원 -> {status}")

        supply_by_path[path] = supply
        total += supply
        if not is_consistent:
            need_check.append(path)

    # 확인 필요한 사진들 재시도: 크롭한 사진으로 다시 시도할 기회를 줌
    if need_check:
        print(f"\n{len(need_check)}장이 확인이 필요해. 공급가액 부분만 크롭해서 재시도할 수 있어.")

        still_need_check = []
        for path in need_check:
            retry_path = input(
                f"\n[{path}] 크롭한 파일 경로 입력 (그냥 Enter면 원본 값 유지): "
            ).strip()

            if not retry_path:
                still_need_check.append(path)
                continue

            supply, tax, is_consistent = process_image(retry_path)

            if supply is None:
                print("  -> 재시도에서도 숫자를 못 찾음. 원본 값 유지")
                still_need_check.append(path)
                continue

            tax_display = f"{tax:,}" if tax is not None else "?"
            status = "OK" if is_consistent else "여전히 확인 필요"
            print(f"  -> 재시도 결과: 공급가액 {supply:,}원 / 세액 {tax_display}원 ({status})")

            # 원래 값(있었다면)을 빼고 새 값을 더함
            total -= supply_by_path.get(path, 0)
            total += supply
            supply_by_path[path] = supply

            if not is_consistent:
                still_need_check.append(path)

        need_check = still_need_check

    print(f"\n최종 합계: {total:,}원")
    if need_check:
        print(f"주의: 아래 {len(need_check)}장은 여전히 원본과 직접 대조가 필요해 -> {need_check}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("사용법: python calculate_total.py 사진1.jpg 사진2.jpg ...")
        sys.exit(1)
    main(sys.argv[1:])
