import os
import tempfile

import streamlit as st

from ocr_core import process_image

st.set_page_config(page_title="세금계산서 공급가액 합산기")
st.title("세금계산서 공급가액 합산기")
st.caption("로컬 Ollama(qwen2.5vl:3b)로 처리해서 사진이 외부로 전송되지 않아요.")

uploaded_files = st.file_uploader(
    "세금계산서 사진을 올리거나 Ctrl+V로 붙여넣으세요 (여러 장 가능, 카톡에서 오는 대로 하나씩 추가해도 됨)",
    type=["jpg", "jpeg", "png"],
    accept_multiple_files=True,
)

if uploaded_files:
    st.write(f"현재 {len(uploaded_files)}장 준비됨")

if st.button("합계 계산", disabled=not uploaded_files):
    total = 0
    need_check = []

    for f in uploaded_files:
        col1, col2 = st.columns([1, 2])
        with col1:
            st.image(f, width=150)
        with col2:
            suffix = os.path.splitext(f.name)[1] or ".jpg"
            with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
                tmp.write(f.getvalue())
                tmp_path = tmp.name

            try:
                with st.spinner(f"{f.name} 처리 중... (CPU라 몇 분 걸릴 수 있어요)"):
                    supply, tax, is_consistent = process_image(tmp_path)
            finally:
                os.remove(tmp_path)

            if supply is None:
                st.error(f"{f.name}: 숫자를 못 찾았어요")
                need_check.append(f.name)
                continue

            tax_display = f"{tax:,}" if tax is not None else "?"
            if is_consistent:
                st.success(f"공급가액: {supply:,}원 / 세액: {tax_display}원")
            else:
                st.warning(
                    f"공급가액: {supply:,}원 / 세액: {tax_display}원 -> 확인 필요 "
                    "(공급가액 부분만 크롭해서 다시 올려보세요)"
                )
                need_check.append(f.name)

            total += supply

    st.divider()
    st.metric("합계", f"{total:,}원")
    if need_check:
        st.warning(f"확인이 필요한 사진: {', '.join(need_check)}")
