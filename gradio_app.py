import gradio as gr

from ocr_core import process_image


def add_image(image_path, gallery):
    gallery = gallery or []
    if image_path is not None:
        gallery = gallery + [image_path]
    return gallery, None


def calculate_total(gallery):
    if not gallery:
        return "사진을 먼저 추가해줘"

    lines = []
    total = 0
    need_check = []

    for item in gallery:
        path = item[0] if isinstance(item, (list, tuple)) else item
        supply, tax, is_consistent = process_image(path)

        if supply is None:
            lines.append(f"[실패] 숫자를 못 찾음")
            continue

        tax_display = f"{tax:,}" if tax is not None else "?"
        status = "OK" if is_consistent else "확인 필요"
        lines.append(f"공급가액: {supply:,}원 / 세액: {tax_display}원 -> {status}")

        total += supply
        if not is_consistent:
            need_check.append(path)

    lines.append(f"\n합계: {total:,}원")
    if need_check:
        lines.append(f"확인이 필요한 사진이 {len(need_check)}장 있어 (위 목록에서 확인 필요 항목)")

    return "\n".join(lines)


with gr.Blocks(title="세금계산서 공급가액 합산기") as demo:
    gr.Markdown("# 세금계산서 공급가액 합산기")
    gr.Markdown("로컬 Ollama(qwen2.5vl:3b)로 처리해서 사진이 외부로 전송되지 않아요.")

    image_input = gr.Image(
        sources=["upload", "clipboard"],
        type="filepath",
        label="사진 붙여넣기(Ctrl+V) 또는 업로드",
    )
    add_btn = gr.Button("목록에 추가")

    gallery = gr.Gallery(label="추가된 사진들", columns=6)
    state = gr.State([])

    calc_btn = gr.Button("합계 계산", variant="primary")
    result = gr.Textbox(label="결과", lines=10)

    add_btn.click(add_image, inputs=[image_input, state], outputs=[state, image_input])
    state.change(lambda s: s, inputs=state, outputs=gallery)
    calc_btn.click(calculate_total, inputs=state, outputs=result)


if __name__ == "__main__":
    demo.launch(inbrowser=True)
